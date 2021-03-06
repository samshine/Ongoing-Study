// 2015-02-04T15:54+08:00

#include "get_command.h"

#include <fstream>

#include <boost/filesystem.hpp>
#include <boost/progress.hpp>

#include "../../azure_cloud_storage_service.h"

// TODO: download_attributes()
// TODO: override prompt

// Note that, blob name is case sensitive.
void download_block_blob(azure::storage::cloud_blob_container &container,
    const utility::string_t &blob_name, const utility::string_t &target_file_name, 
    utility::size64_t downloading_bytes_each_time)
{
    auto blob = container.get_block_blob_reference(blob_name);
    if (!blob.exists()) {
        ucerr << U("Block blob \"") << blob_name << U("\" doesn't exist.\n");
        return;
    }

    boost::filesystem::path target_path(target_file_name);
    if (boost::filesystem::exists(target_path))
    {
        ucout << U("Warning! File \"") << target_file_name 
            << U("\" already exists, and it will be overwrite.") << std::endl;
    }
    else
    {
        target_path.remove_filename();
        if (!boost::filesystem::exists(target_path))
        {
            ucout << U("Creating directory \"") << target_path.string<utility::string_t>()
                << U("\"...") << std::endl;
            if (!boost::filesystem::create_directories(target_path))
            {
                ucerr << U("Failed to create directory \"")
                    << target_path.string<utility::string_t>() << U("\"!\n");
                return;
            }
        }
    }

    // Get blob's size(in bytes)
    auto blob_size = blob.properties().size();

    if (0 == blob_size) {
        blob.download_to_file(target_file_name);
        return;
    }

    assert(downloading_bytes_each_time > 0);
    if (downloading_bytes_each_time == 0 || downloading_bytes_each_time > blob_size) {
        downloading_bytes_each_time = blob_size;
    }

    std::ofstream out_file(target_file_name, std::ofstream::binary);
    if (!out_file) {
        ucout << U("Opening file \"") << target_file_name << U("\" failed.\n");
        return;
    }

    ucout << U("Downloading file to: ") << target_file_name << U("...");
    boost::progress_display prog(blob_size);

    utility::size64_t offset = 0;
    utility::size64_t bytes_read;
    while (offset < blob_size) {
        // Create a memory buffer
        concurrency::streams::container_buffer<std::vector<uint8_t>> buffer;
        // Read data
        concurrency::streams::ostream tmp_out_stream(buffer);
        blob.download_range_to_stream(tmp_out_stream, offset, downloading_bytes_each_time);
        bytes_read = buffer.collection().size();
        // Write out...
        out_file.write(reinterpret_cast<char *>(buffer.collection().data()), bytes_read);
        //out_file.flush();
        // Upgrade the progress bar and other states
        prog += bytes_read;
        offset += bytes_read;
    }

    // The last step...
    blob.download_block_list();
}

GetCommand::GetCommand()
{
    options_desc_.add_options()
        ("blob,b", boost::program_options::wvalue<utility::string_t>(&blob_name_)->required(), "The blob to download")
        ("out,o", boost::program_options::wvalue<utility::string_t>(&target_local_file_name_)->required(), "Target local file name")
        ("size,s", boost::program_options::value<utility::size64_t>(&size_)->default_value(1024 * 1024), "How many bytes to be downloaded each time")
        ;
}

bool GetCommand::parse(const std::vector<utility::string_t> &vargs)
{
    container_name_.clear();
    blob_name_.clear();
    target_local_file_name_.clear();

    boost::program_options::variables_map args_map;

    try {
        boost::program_options::store(boost::program_options::basic_command_line_parser<CharT>(vargs).
            options(options_desc_).run(), args_map);
        boost::program_options::notify(args_map);

        return true;
    } catch (const std::exception &e) {
        notify_err(e.what(), GET_COMMAND_STR);
        return false;
    }
}

bool GetCommand::run(AzureCloudStorageService *storage_service)
{
    if (container_name_.empty()) {
        if (!storage_service->current_container_.is_valid()) {
            ucerr << U("Container name didn't provided.\n");
        } else {
            download_block_blob(storage_service->current_container_, blob_name_, target_local_file_name_, size_);
        }
    } else {
        auto container = storage_service->blob_client_.get_container_reference(container_name_);
        if (!container.exists()) {
            ucerr << U("Container \"") << container_name_ << U("\" doesn't exist.\n");
        } else {
            download_block_blob(container, blob_name_, target_local_file_name_, size_);
        }
    }

    return true;
}

void GetCommand::help() const
{
    ucout << U("Download specified blob.\nUsage: ") << GET_COMMAND_STR << U(" [options]\n");
    Command::help();
}
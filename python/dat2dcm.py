#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# 2015-03-23T14:34+08:00

__author__ = 'myd7349 <myd7349@gmail.com>'
__version__ = '0.0.1'

import logging
import os
import struct
import sys

import dicom  # [pydicom](http://www.pydicom.org/)

import fileutil
import unpacker

_frozen = hasattr(sys, 'frozen') or hasattr(sys, 'importers')

if _frozen:
    __file__ = sys.executable  # Fix issue #6
else:
    import warnings  # Fix issue #7

# Fix issue #5
# Don't use os.environ['HOME'], use os.path.expanduser('~') instead.
logger_filename = os.path.join(os.path.expanduser('~'),
                            fileutil.replace_ext(os.path.basename(__file__), '.log'))
logging.basicConfig(level = logging.NOTSET, filename = logger_filename,
                    format ='%(asctime)s [%(levelname)s]: %(message)s')
#logging.captureWarnings(True)
logger = logging.getLogger(__name__)


# PS3.16 CID 3001 ECG Leads
CID_3001_for_12_Lead_ECG = {
    'I': ('2:1', 'Lead I'),
    'II': ('2:2', 'Lead II'),
    'III': ('2:61', 'Lead III'),
    'aVR': ('2:62', 'aVR, augmented voltage, right'),
    'aVL': ('2:63', 'aVL, augmented voltage, left'),
    'aVF': ('2:64', 'aVF, augmented voltage, foot'),
    'V1': ('2:3', 'Lead V1'),
    'V2': ('2:4', 'Lead V2'),
    'V3': ('2:5', 'Lead V3'),
    'V4': ('2:6', 'Lead V4'),
    'V5': ('2:7', 'Lead V5'),
    'V6': ('2:8', 'Lead V6'),
    }

class DCMECGDataset(dicom.dataset.FileDataset):
    def __init__(self, file, fmt, sampling_frequency, channels, channel_labels,
                 adjust_callback=int, is_12_lead_ecg=True, **kwargs):
        """Represents a DICOM waveform data set, with necessary attributed added.

        file: An opened file object or a file name represents a file on the disk.
        fmt: Format specification for unpacking data from file.
        sampling_frequency: Sampling frequency of the data.
        channels: Number of channels.
        channel_labels: An iterable object that contains labels for each channel.
        adjust_callback: A callback function to adjust unpacked data.
        is_12_lead_ecg: True for 12-Lead ECG IOD, False for General ECG IOD.
        """
        super().__init__('', {}, is_implicit_VR=False, preamble=b'\x00' * 128, **kwargs)

        self._file = file
        self._format = fmt
        self._sampling_frequency = sampling_frequency
        self._channels = channels
        self._channel_labels = channel_labels
        self._adjust_callback = adjust_callback
        self._is_12_lead_ecg = is_12_lead_ecg

        # The format of DICOM file is described in:
        #   PS3.10 7.1 DICOM File Meta Information
        # The 12-Lead ECG IOD is described in:
        #   PS3.3 A.34.3.1 12-Lead ECG IOD Descriptionfile, fmt, sampling_frequency, channels, channel_labels

        # To make things simple, when generating DICOM-ECG waveform files:
        # 1. We only care those modules that are mandatory;
        # 2. We pay most of our attention on those attributes of type 1 and 2;
        
        # 1. DICOM File Meta Information
        self._fill_file_meta_info()
        # 2. Patient IE(M)
        self._fill_patient_IE()
        # 3. Study IE(M)
        self._fill_study_IE()
        # 4. Series IE(M)
        self._fill_series_IE()
        # 5. Frame of Reference IE(U)
        # 6. Equipment IE(M)
        self._fill_equipment_IE()
        # 7. Waveform IE(M)
        self._fill_waveform_IE()

    def _fill_file_meta_info(self):
        self.file_meta = dicom.dataset.Dataset()
        # dicom.dataset.Dataset.save_as calls dicom.filewriter.write_file to do
        # the real work. And the latter calls dicom.filewriter._write_file_meta_info
        # to write the file meta information.
        #----------------------------------------------------------------------
        # 1. File Preamble.
        #----------------------------------------------------------------------
        # 2. DICOM Prefix.
        #----------------------------------------------------------------------
        # 3. File Meta Information Group
        # dicom.filewriter._write_file_meta_info will add the following two
        # elements for us:
        #   FileMetaInformationGroupLength
        #   FileMetaInformationVersion

        # PS3.4 B.5 Standard SOP Classes. See PS3.4 B.5 Standard SOP Classes.
        # Note that, this program only supports 12-Lead ECG IOD and General ECG IOD currently.
        if self._is_12_lead_ecg:
            # For 12-Lead ECG, we use:
            self.file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.9.1.1'
        else:
            # Otherwise, suppose that it is General Electrocardiogram IOD. So we use:
            self.file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.9.1.2'

        self.file_meta.MediaStorageSOPInstanceUID = '1.3.6.1.4.1.6018.1.1'#dicom.UID.generate_uid() # ???

        # PS3.5 A.2 DICOM Little Endian Transfer Syntax (Explicit VR)
        self.file_meta.TransferSyntaxUID = dicom.UID.ExplicitVRLittleEndian
        
        self.file_meta.ImplementationClassUID = '1.3.6.1.4.1.6018.2.11111'#dicom.UID.generate_uid() # ???
        #----------------------------------------------------------------------

    def _fill_patient_IE(self):
        #----------------------------------------------------------------------
        # 1. Patient(M)
        self.PatientName = '^' # Type 2. PN.
        self.PatientID = ' ' # Type 2. LO.
        self.PatientBirthDate = ' ' # Type 2. YYYYMMDD
        self.PatientSex = ' ' # Type 2. M(ale)/F(emale)/O(ther)
        #----------------------------------------------------------------------
        # 2. Clinical Trial Subject(U)
        #----------------------------------------------------------------------

    def _fill_study_IE(self):
        #----------------------------------------------------------------------
        # 1. General Study(M)

        # PS3.3 C.7.2.1 General Study Module tells us the Tag of Study Instance UID.
        # PS3.6 6 Registry of DICOM Data Elements tells us the VR of it: UI.
        # PS3.5 6.2 Value Representation (VR) tells us the meaning of UI and how to
        # generate a UID.
        self.StudyInstanceUID = '1.3.6.1.4.1.6018.4.999' # dicom.UID.generate_uid() # Type 1. UI.
        self.StudyDate = ' ' # Type 2. DA.
        self.StudyTime = ' ' # Type 2. TM.
        self.ReferringPhysicianName = '^' # Type 2. PN.
        self.StudyID = ' ' # Type 2. SH.
        self.AccessionNumber = ' ' # Type 2. SH.
        #----------------------------------------------------------------------
        # 2. Patient Study(U)
        #self.AdmittingDiagnosesDescription = '' # Type 3. LO.
        self.PatientAge = ' ' # Type 3. AS.
        self.PatientSize = ' ' # Type 3. DS.
        self.PatientWeight = ' ' # Type 3. DS.
        self.AdditionalPatientHistory = ' ' # Type 3. LT.
        #----------------------------------------------------------------------
        # 3. Clinical Trial Study(U)
        #----------------------------------------------------------------------

    def _fill_series_IE(self):
        #----------------------------------------------------------------------
        # 1. General Series(M)
        self.Modality = 'ECG' # Type 1. DICOM PS3.3-2015a A.34.3.4.1
        self.SeriesInstanceUID = ' 1.3.6.1.4.1.6018.5.999'#dicom.UID.generate_uid() # Type 1. UI. ???
        self.SeriesNumber = '0001' # (0020,0011), Type 2. IS. ***
        #----------------------------------------------------------------------
        # 2. Clinical Trial Series(U)
        #----------------------------------------------------------------------

    def _fill_equipment_IE(self):
        #----------------------------------------------------------------------
        # 1. General Equipment(M)
        self.Manufacturer = ' ' # Type 2. LO.
        self.InstitutionName = ' ' # Type 3. LO.
        self.InstitutionAddress = ' ' # Type 3. ST.
        self.SoftwareVersions = __version__ # Type 3. LO.
        self.InstitutionalDepartmentName = ' ' # Type 3. LO.
        #----------------------------------------------------------------------

    def _generate_channel_source_sequence(self, label):
        # PS3.3 A.34.3.4.7 Channel Source
        # PS3.3 C.10.9.1.4.1 Channel Source and Modifiers
        channel_source_seq = dicom.dataset.Dataset()

        if self._is_12_lead_ecg:
            channel_source_seq.CodeValue = CID_3001_for_12_Lead_ECG[label][0] # Type 1C. SH.
            channel_source_seq.CodingSchemeDesignator = 'MDC' # Type 1C. SH.
            channel_source_seq.CodeMeaning = CID_3001_for_12_Lead_ECG[label][1] # Type 1. LO.
        else:
            pass

        return (channel_source_seq, )

    def _generate_channel_sensitivity_units_sequence(self):
        # I don't how to fill this part, so follow GE's step.
        sensitivity_unit_seq = dicom.dataset.Dataset()
        sensitivity_unit_seq.CodeValue = 'mV' # SH.
        sensitivity_unit_seq.CodingSchemeDesignator = 'UCUM'
        sensitivity_unit_seq.CodingSchemeVersion = '1.4' # Type 1C. SH.
        sensitivity_unit_seq.CodeMeaning = 'millivolt'

        return (sensitivity_unit_seq, )

    def _generate_channel_definition_sequence(self):
        channel_def_seq = dicom.sequence.Sequence()

        assert len(self._channel_labels) >= self._channels
        for c in range(self._channels):
            channel_def_item = dicom.dataset.Dataset()
            
            channel_def_item.ChannelLabel = self._channel_labels[c] # Type 3. SH.
            channel_def_item.ChannelSourceSequence = self._generate_channel_source_sequence(self._channel_labels[c]) # Type 1
            channel_def_item.ChannelSensitivity = '0.00122' # Type 1C. DS.
            channel_def_item.ChannelSensitivityUnitsSequence = self._generate_channel_sensitivity_units_sequence() # Type 1C
            channel_def_item.ChannelSensitivityCorrectionFactor = '1' # Type 1C. DS. ?
            channel_def_item.ChannelBaseline = '0' # Type 1C. DS.
            channel_def_item.ChannelTimeSkew = '0' # Type 1C. DS. PS3.3 C.10.9.1.4.3 Channel Skew and Channel Offset
            channel_def_item.WaveformBitsStored = 16 # Type 1. US. PS3.3 C.10.9.1.5 Waveform Bits Allocated and Waveform Sample Interpretation

            channel_def_seq.append(channel_def_item)

        return channel_def_seq
    
    def _generate_waveform_sequence(self):
        if self._is_12_lead_ecg:
            maximum_waveform_sequences = 5 # PS3.3 A.34.3.4.3 Waveform Sequence
            maximum_waveform_samples = 16384 # PS3.3 A.34.3.4.5 Number of Waveform Samples
        else:
            maximum_waveform_sequences = 4 # PS3.3 A.34.4.4.2 Waveform Sequence
            maximum_waveform_samples = 2 ** 32 - 1 # NumberOfWaveformSamples's VR is `UL`.
        
        data_file_len = fileutil.file_size(self._file)
        pack_size = struct.calcsize(self._format)
        data_file_total_samples = data_file_len // pack_size
        saved_samples = maximum_waveform_sequences * maximum_waveform_samples
        if data_file_total_samples > saved_samples:
            warn_msg = 'File "{}" is too big. File size: {}, pack size: {}, format string: {}, ' \
                       'total samples: {}, saved samples: {}, saved size: {}.'.format(
                           fileutil.file_name(self._file), data_file_len, pack_size, self._format,
                           data_file_total_samples, saved_samples, saved_samples * pack_size)
            if not _frozen:  # Fix issue #7
                warnings.warn(warn_msg)
            logger.warn(warn_msg)
            data_file_total_samples = saved_samples

        waveform_seq = dicom.sequence.Sequence()
        data_unpacker = unpacker.unpack_data_from_file(self._file, self._format)
        target_fmt = '<{}'.format('h' * self._channels)
        adjusted_data = map(lambda v: map(self._adjust_callback, v), data_unpacker)
        while data_file_total_samples > 0:
            seq_item = dicom.dataset.Dataset()
            seq_item.WaveformOriginality = 'ORIGINAL'  # Type 1
            
            seq_item.NumberOfWaveformChannels = self._channels  # Type 1.
            if self._is_12_lead_ecg:
                assert 1 <= seq_item.NumberOfWaveformChannels <= 13  # PS3.3 A.34.3.4.4
            else:
                assert 1 <= seq_item.NumberOfWaveformChannels <= 24  # PS3.3 A.34.4.4.3 Number of Waveform Channels

            if data_file_total_samples >= maximum_waveform_samples:
                seq_item.NumberOfWaveformSamples = maximum_waveform_samples  # Type 1. UL.
            else:
                seq_item.NumberOfWaveformSamples = data_file_total_samples  # Type 1. UL.
            data_file_total_samples -= seq_item.NumberOfWaveformSamples

            assert 200 <= self._sampling_frequency <= 1000 # DICOM PS3.3-2015a A.34.3.4.6
            seq_item.SamplingFrequency = '{:d}'.format(self._sampling_frequency) # Type 1. DS.

            seq_item.ChannelDefinitionSequence = self._generate_channel_definition_sequence() # Type 1.

            seq_item.WaveformBitsAllocated = 16 # Type 1. PS3.3 C.10.9.1.5 Waveform Bits Allocated and Waveform Sample Interpretation
            seq_item.WaveformSampleInterpretation = 'SS' # Type 1. PS3.3 A.34.3.4.8 Waveform Sample Interpretation

            # The VR of `Waveform Padding Value` may be OB or OW, so:
            #seq_item.WaveformPaddingValue = b'\x00\x00'
            # will not work, instead:
            seq_item.add_new((0x5400, 0x100A), 'OW', b'\x00\x80')  # Type 1C. OB or OW.

            data = bytearray()
            for i, d in zip(range(seq_item.NumberOfWaveformSamples), adjusted_data):
                data.extend(struct.pack(target_fmt, *d))
            seq_item.add_new((0x5400, 0x1010), 'OW', bytes(data)) # WaveformData. Type 1. OB or OW.

            waveform_seq.append(seq_item)
        
        return waveform_seq
    
    def _generate_acquisition_context_sequence(self):
        # PS3.3 A.34.3.4.2 Acquisition Context Module
        acquisition_context_seq = dicom.dataset.Dataset()

        # I don't know how to fill this part, so follow GE's step.
        concept_name_code_seq = dicom.dataset.Dataset()
        concept_name_code_seq.CodeValue = '109057'
        concept_name_code_seq.CodingSchemeDesignator = 'DCM'
        concept_name_code_seq.CodingSchemeVersion = '01'
        concept_name_code_seq.CodeMeaning = 'Catheterization Procedure Phase'
        
        acquisition_context_seq.ConceptNameCodeSequence = (concept_name_code_seq, )

        concept_code_seq = dicom.dataset.Dataset()
        concept_code_seq.CodeValue = 'G-7293'
        concept_code_seq.CodingSchemeDesignator = 'SRT'
        concept_code_seq.CodingSchemeVersion = 'V1'
        concept_code_seq.CodeMeaning = 'Cardiac catheterization baseline phase'

        acquisition_context_seq.ConceptCodeSequence = (concept_code_seq, )
        
        return (acquisition_context_seq, )

    def _fill_waveform_IE(self):
        #----------------------------------------------------------------------
        # 1. Waveform Identification(M)
        self.InstanceNumber = '0001' # 0x00200013. Type 1. IS.
        self.ContentDate = '19991223' # 0x00080023. Type 1. DA.
        self.ContentTime = '100709' # 0x00080033. Type 1. TM.
        self.AcquisitionDateTime = '19991223100709' # 0x0008002A. Type 1. DT.
        #----------------------------------------------------------------------
        # 2. Waveform(M)
        self.WaveformSequence = self._generate_waveform_sequence() # 0x54000100. Type 1
        #self.WaveformDataDisplayScale = 0 # Type 3
        #----------------------------------------------------------------------
        # 3. Acquisition Context(M)
        self.AcquisitionContextSequence = self._generate_acquisition_context_sequence() # 0x00400555, SQ. Type 2 T3401 ECG Acquisition Context # A.34.3.4.2
        #----------------------------------------------------------------------
        # 4. Waveform Annotation(C)
        #----------------------------------------------------------------------
        # 5. SOP Common(M)
        # PS3.3 C.12.1.1.1 SOP Class UID, SOP Instance UID
        self.SOPClassUID = self.file_meta.MediaStorageSOPClassUID # Type 1
        self.SOPInstanceUID = '1.3.6.1.4.1.6018.3.999'#self.file_meta.MediaStorageSOPInstanceUID # Type 1
        # PS3.3 C.12.1.1.2 Specific Character Set
        self.SpecificCharacterSet = 'ISO_IR 192' # Type 1C. 'ISO_IR 192' for UTF-8, 'GBK' for GBK, 'GB18030' for GB18030.
        self.TimezoneOffsetFromUTC = '+0800' # Type 3
        #----------------------------------------------------------------------

def fecg_to_dcm(src, dest = None):
    '''Convert Foetus Electrocardiogram data into DICOM-ECG standard compliant format.'''
    # Data values are encoded interleaved. That is:
    # lead 1, 2, 3, 4, 5, 1, 2, ...
    if not dest:
        dest = fileutil.replace_ext(src, '.dcm')
    
    data_set = DCMECGDataset(src, '<{}'.format('d' * 5), 1000, 5, ('', '', '', '', ''),
                             adjust_callback = lambda v: int(v * 100),
                             is_12_lead_ecg = False)
    data_set.save_as(dest)

def ecg_to_dcm(src, dest = None):
    '''Convert 12-Lead Electrocardiogram data into DICOM-ECG standard compliant format.'''
    # Data values are encoded interleaved. That is:
    # Lead I, II, III, aVR, aVL, aVF, V1, V2, V3, V4, V5, V6, I, II, III, ...
    # The unit of signals collected by the cardiac conduction is: 0.4V/(2^15).
    if not dest:
        dest = fileutil.replace_ext(src, '.dcm')

    data_set = DCMECGDataset(src, '<{}'.format('d' * 12), 500, 12,
                             ('I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6'),
                             adjust_callback = lambda v: int(v * 1000 / 6))
    data_set.save_as(dest)

if __name__ == '__main__':
    u = unpacker.unpack_data_from_file(r'E:\data\1\20110607153002.dat', '<d')
    print(max(u))
    u = unpacker.unpack_data_from_file(r'E:\data\1\20110607153002.dat', '<d')
    print(min(u))
    
    ecg_to_dcm(r'E:\data\1\20110607153002.dat')
    ecg_to_dcm(r'd:\20120503152310.dat')

# References:
# DICOM 2015a PS3.5 7.4 Data Element Type
# DICOM 2015a PS3.5 8.3 Waveform Data and Related Data Elements
# DICOM 2015a PS3.6 6 Registry of DICOM Data Elements
# [DICOM Waveform Generator](http://libir.tmu.edu.tw/bitstream/987654321/21661/1/B09.pdf)
# [Mandatory Tags for DICOM Instance](http://stackoverflow.com/questions/6608535/mandatory-tags-for-dicom-instance)
# [Questions regarding the DICOM file](http://fixunix.com/dicom/50267-questions-regarding-dicom-file.html)
# [Dicom: What's the point of SOPInstanceUID tag?](http://stackoverflow.com/questions/1434918/dicom-whats-the-point-of-sopinstanceuid-tag)

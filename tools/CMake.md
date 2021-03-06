1. cmake -G "Visual Studio 10 2010" ..

2. E:\vcpkg>vcpkg.exe integrate install
    >Applied user-wide integration for this vcpkg root.
    >
    >All MSBuild C++ projects can now #include any installed libraries.
    >Linking will be handled automatically.
    >Installing new libraries will make them instantly available.
    >
    >CMake projects should use: "-DCMAKE_TOOLCHAIN_FILE=e:/vcpkg/scripts/buildsystems/vcpkg.cmake"

3. Specify toolchain file

    - [CMake: specifying build toolchain](https://stackoverflow.com/questions/5098360/cmake-specifying-build-toolchain)
    - [CMAKE_TOOLCHAIN_FILE only recognized on command line](https://github.com/queezythegreat/arduino-cmake/issues/38)
    - [cmake : Set environment variables from a script](https://stackoverflow.com/questions/21047399/cmake-set-environment-variables-from-a-script)
    - [Cross Compiling](https://gitlab.kitware.com/cmake/community/wikis/doc/cmake/CrossCompiling)

4. Specify build type

    - [CMAKE_BUILD_TYPE not being used in CMakeLists.txt](https://stackoverflow.com/questions/24460486/cmake-build-type-not-being-used-in-cmakelists-txt)

5. [Difference between CMAKE_CURRENT_SOURCE_DIR and CMAKE_CURRENT_LIST_DIR](https://stackoverflow.com/questions/24460486/cmake-build-type-not-being-used-in-cmakelists-txt)

6. [OS specific instructions in CMAKE: How to?](https://stackoverflow.com/questions/9160335/os-specific-instructions-in-cmake-how-to)

7. Couldn't find Threads when building raylib on Ubuntu:
* [cmake and libpthread](https://stackoverflow.com/questions/1620918/cmake-and-libpthread)
* [How to get CMake to recognize pthread on Ubuntu?](https://stackoverflow.com/questions/15193785/how-to-get-cmake-to-recognize-pthread-on-ubuntu)
* [CMake can't find pthread](https://askubuntu.com/questions/499238/cmake-cant-find-pthread)
* [CMake failing to detect pthreads due to warnings](https://stackoverflow.com/questions/24813827/cmake-failing-to-detect-pthreads-due-to-warnings/25130590#25130590)

8. Couldn't find OpenGL on Linux
* [How to use CMake to find and link OpenGL(mesa) package in Ubuntu](https://stackoverflow.com/questions/34001996/how-to-use-cmake-to-find-and-link-openglmesa-package-in-ubuntu)
* [Couldn't find OpenGL on Ubuntu](https://stackoverflow.com/questions/31170869/cmake-could-not-find-opengl-in-ubuntu)

9. Setting the MSVC runtime in CMake
* [Setting the MSVC runtime in CMake](https://stackoverflow.com/questions/10113017/setting-the-msvc-runtime-in-cmake)

10. [When should I quote variables?](https://stackoverflow.com/questions/35847655/when-should-i-quote-variables)

11. [CMake FetchContent](https://cmake.org/cmake/help/latest/module/FetchContent.html)
* [imgui-plot](https://github.com/soulthreads/imgui-plot)

12. Override options in subdirectory
* [Override options in cmake subproject](https://stackoverflow.com/questions/14061605/override-option-in-cmake-subproject)
* [CMake: set subdirectory options](https://stackoverflow.com/questions/20239334/cmake-set-subdirectory-options)

13. MSVC UTF-8
* [Possible to force CMake/MSVC to use UTF-8 encoding for source files without a BOM? C4819](https://stackoverflow.com/questions/47690822/possible-to-force-cmake-msvc-to-use-utf-8-encoding-for-source-files-without-a-bo)
* https://github.com/ethereum/aleth/issues/4102

14. Threads
* [cmake and libpthread](https://stackoverflow.com/questions/1620918/cmake-and-libpthread)
* [Significance of -pthread flag when compiling](https://stackoverflow.com/questions/2127797/significance-of-pthread-flag-when-compiling)

15. CMAKE_BUILD_TYPE
* [CMAKE_BUILD_TYPE is not being used in CMakeLists.txt](https://stackoverflow.com/questions/24460486/cmake-build-type-is-not-being-used-in-cmakelists-txt)

16. CMAKE_CXX_COMPILER_ID
* [In CMake, how can I test if the compiler is Clang?](https://stackoverflow.com/questions/10046114/in-cmake-how-can-i-test-if-the-compiler-is-clang)

17. C++17
* [How to enable C++17 in CMake](https://stackoverflow.com/questions/45688522/how-to-enable-c17-in-cmake)
> target_compile_features(${TARGET_NAME} PRIVATE cxx_std_17)

18.
* [CMAKE_RUNTIME_OUTPUT_DIRECTORY](https://github.com/microsoft/vcpkg/issues/11547#issuecomment-633211556)

19. libm
* [Can CMake detect if I need to link to libm when using pow in C?](https://stackoverflow.com/questions/32816646/can-cmake-detect-if-i-need-to-link-to-libm-when-using-pow-in-c)

20.
* [CMake install](https://github.com/uriparser/uriparser/pull/75)

21
* [CMAKE_CURRENT_SOURCE_DIR vs PROJECT_SOURCE_DIR](https://github.com/mandreyel/mio/commit/61567f4c579aeb2ec1ab8f6bc285de461c7149a8)

22.
* https://github.com/llvm/llvm-project/commit/bb73d1b278eb478ca8e56153cf1469bf7eb13a3f
> include_directories(AFTER ${CMAKE_CURRENT_BINARY_DIR})

https://github.com/rafat/wavelib/blob/a92456d2e20451772dd76c2a0a3368537ee94184/CMakeLists.txt#L24-L25
```cmake
# cleanup prefix lib for Unix-like OSes
set(CMAKE_SHARED_MODULE_PREFIX)
```

[CMake and Boost](https://github.com/microsoft/vcpkg/issues/4188)
```cmake
cmake_minimum_required (VERSION 3.10)

project ("Example" LANGUAGES CXX)

set(Boost_USE_STATIC_LIBS ON)
find_package(Boost REQUIRED COMPONENTS random )# asio is header only no library, random is for example
include_directories(${Boost_INCLUDE_DIR})

add_executable (Example "Example.cpp")
target_link_libraries(Example ${Boost_LIBRARIES})
```

[How to detect if 64 bit MSVC with cmake?](https://stackoverflow.com/questions/39258250/how-to-detect-if-64-bit-msvc-with-cmake)
```cmake
if(NOT "${CMAKE_GENERATOR}" MATCHES "(Win64|IA64)")
    ...
endif()

if("${CMAKE_SIZEOF_VOID_P}" STREQUAL "4")
    ...
endif()

if(NOT CMAKE_CL_64)
   ...
endif()
```

> [Beware of the cmake 3.14 release, now the bitness in the generator name is dropped.](https://cmake.org/cmake/help/v3.14/generator/Visual%20Studio%2016%202019.html#generator:Visual%20Studio%2016%202019)

```bash
cmake -G "Visual Studio 16 2019" -A Win32
cmake -G "Visual Studio 16 2019" -A x64
cmake -G "Visual Studio 16 2019" -A ARM
cmake -G "Visual Studio 16 2019" -A ARM64
```

[How can I install a hierarchy of files using CMake?](https://stackoverflow.com/questions/11096471/how-can-i-install-a-hierarchy-of-files-using-cmake)

[cmake glob include while preserving directory structure](https://stackoverflow.com/questions/6216554/cmake-glob-include-while-preserving-directory-structure)

https://github.com/google/benchmark/blob/master/cmake/AddCXXCompilerFlag.cmake

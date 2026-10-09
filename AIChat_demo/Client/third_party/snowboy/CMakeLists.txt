cmake_minimum_required(VERSION 3.10)

# Option to choose target architecture
option(TARGET_ARM "Build for ARM architecture" OFF)

# Find the architecture
if(TARGET_ARM)
	    # ARM 交叉编译时跳过 OpenBLAS，只用数学库 m
	        set(BLAS_LIBRARIES m)
		    set(LAPACK_LIBRARIES m)
		        set(BLAS_INCLUDE_DIRS "")
		else()
			    find_package(BLAS REQUIRED)
			        find_package(LAPACK REQUIRED)
			endif()

# Set the project name and define the library
project(SnowboyLib)

add_compile_definitions(_GLIBCXX_USE_CXX11_ABI=0)

# Include directories
include_directories(${CMAKE_CURRENT_SOURCE_DIR})

# 搜索所有 .cc 和 .h 文件
file(GLOB_RECURSE SNOWBOY_SOURCES
    #"${CMAKE_CURRENT_SOURCE_DIR}/*.cc"
    "${CMAKE_CURRENT_SOURCE_DIR}/*.h"
    "${CMAKE_CURRENT_SOURCE_DIR}/snowboy-detect-c-wrapper.cc"
)

# 添加静态库
add_library(snowboy STATIC ${SNOWBOY_SOURCES})

# Link libraries
target_link_libraries(snowboy PRIVATE ${SNOWBOY_LIBRARY})

# Additional flags and options
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(PkgConfig REQUIRED)

# 确保链接必要的数学库
if(TARGET_ARM)
    set(BLAS_LIBRARIES m)
    set(LAPACK_LIBRARIES m)
    set(BLAS_INCLUDE_DIRS "")

    if(OpenBLAS_FOUND)
        set(BLAS_LIBRARIES ${OpenBLAS_LIBRARIES})
        set(LAPACK_LIBRARIES ${OpenBLAS_LIBRARIES})  # OpenBLAS 包含 LAPACK 实现
        set(BLAS_INCLUDE_DIRS ${OpenBLAS_INCLUDE_DIR})
    endif()
else()
    find_package(BLAS REQUIRED)
    find_package(LAPACK REQUIRED)
endif()

# 将找到的库添加到目标
target_include_directories(snowboy PUBLIC ${BLAS_INCLUDE_DIRS})
target_link_libraries(snowboy PRIVATE ${BLAS_LIBRARIES} ${LAPACK_LIBRARIES})

# Create the C wrapper for snowboy-detect
add_library(snowboy-detect-c-wrapper STATIC
    snowboy-detect-c-wrapper.cc  # C wrapper implementation
)

# Link the snowboy C++ library into the C wrapper
target_link_libraries(snowboy-detect-c-wrapper PRIVATE snowboy)

# 添加一个可选的 demo 可执行文件
if(BUILD_DEMO)
    target_link_libraries(demo2 snowboy)
endif()

set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR arm)

set(SDK_PATH "/home/xuanyue/Echo-Mate/SDK/rv1106-sdk")

set(TOOLCHAIN_DIR "${SDK_PATH}/tools/linux/toolchain/arm-rockchip830-linux-uclibcgnueabihf")

set(CMAKE_C_COMPILER ${TOOLCHAIN_DIR}/bin/arm-rockchip830-linux-uclibcgnueabihf-gcc)
set(CMAKE_CXX_COMPILER ${TOOLCHAIN_DIR}/bin/arm-rockchip830-linux-uclibcgnueabihf-g++)

set(CMAKE_SYSROOT ${TOOLCHAIN_DIR}/arm-rockchip830-linux-uclibcgnueabihf/sysroot)

set(CMAKE_FIND_ROOT_PATH ${CMAKE_SYSROOT})

set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)

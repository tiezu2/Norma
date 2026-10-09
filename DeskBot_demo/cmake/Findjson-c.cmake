find_package(PkgConfig REQUIRED)
pkg_check_modules(JSONC REQUIRED json-c)

set(json-c_FOUND TRUE)
set(json-c_INCLUDE_DIRS ${JSONC_INCLUDE_DIRS})
set(json-c_LIBRARIES ${JSONC_LIBRARIES})
set(json-c_LIBRARY_DIRS ${JSONC_LIBRARY_DIRS})

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(json-c DEFAULT_MSG JSONC_FOUND)

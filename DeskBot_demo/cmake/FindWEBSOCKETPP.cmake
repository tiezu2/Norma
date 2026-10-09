find_path(WEBSOCKETPP_INCLUDE_DIR
    NAMES websocketpp/client.hpp
    PATHS $ENV{HOME}/websocketpp /usr/include /usr/local/include
    NO_CMAKE_FIND_ROOT_PATH
)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(WEBSOCKETPP
    DEFAULT_MSG
    WEBSOCKETPP_INCLUDE_DIR
)

if(WEBSOCKETPP_FOUND)
    set(WEBSOCKETPP_INCLUDE_DIRS ${WEBSOCKETPP_INCLUDE_DIR})
    set(WEBSOCKETPP_LIBRARIES "")
endif()

find_path(SDL2_IMAGE_INCLUDE_DIR
	    NAMES SDL_image.h
	        PATHS /usr/include/SDL2 /usr/local/include/SDL2
		)

	find_library(SDL2_IMAGE_LIBRARY
		    NAMES SDL2_image
		        PATHS /usr/lib/x86_64-linux-gnu /usr/local/lib
			)

		include(FindPackageHandleStandardArgs)
		find_package_handle_standard_args(SDL2_image
			    DEFAULT_MSG
			        SDL2_IMAGE_LIBRARY
				    SDL2_IMAGE_INCLUDE_DIR
				    )

			    if(SDL2_image_FOUND)
				        set(SDL2_IMAGE_INCLUDE_DIRS ${SDL2_IMAGE_INCLUDE_DIR})
					    set(SDL2_IMAGE_LIBRARIES ${SDL2_IMAGE_LIBRARY})
				    endif()

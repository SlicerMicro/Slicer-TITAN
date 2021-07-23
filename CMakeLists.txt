cmake_minimum_required(VERSION 3.13.4)

project(HypModule2)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://github.com/SlicerMicro/Slicer-TITAN")
set(EXTENSION_CATEGORY "Analysis")
set(EXTENSION_CONTRIBUTORS "Sindhura Thirumal (Queen's University)")
set(EXTENSION_DESCRIPTION "TITAN is responsible for the pre-processing and analysis tasks of imaging mass cytometry (IMC) data. It performs visualization, segmentation, and various analyses functions on IMC data.")
set(EXTENSION_ICONURL "https://user-images.githubusercontent.com/21988487/126827263-15f356e4-bef0-4244-8e0e-8a763e223242.PNG")
set(EXTENSION_SCREENSHOTURLS "https://user-images.githubusercontent.com/21988487/126827330-1b7fec78-3358-4d61-b2a9-9510cc3d13c8.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
# add_subdirectory(HyperionModuleCode)
add_subdirectory(HypModuleCode)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})

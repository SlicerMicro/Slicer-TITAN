cmake_minimum_required(VERSION 3.13.4)

project(HypModule2)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://github.com/SlicerMicro/Slicer-TITAN")
set(EXTENSION_CATEGORY "Analysis")
set(EXTENSION_CONTRIBUTORS "Sindhura Thirumal (Queen's University)")
set(EXTENSION_DESCRIPTION "TITAN is responsible for the pre-processing and analysis tasks of imaging mass cytometry (IMC) data. It performs visualization, segmentation, and various analyses functions on IMC data.")
set(EXTENSION_ICONURL "https://raw.githubusercontent.com/sindhurathiru/TITAN/master/HypModuleCode/Resources/Icons/logo%20v2.PNG?token=AFHYJB2MGCUT2PJ35XRKCVTA5X2EU")
set(EXTENSION_SCREENSHOTURLS "https://user-images.githubusercontent.com/21988487/125518905-0ca9aeb4-a904-415d-80f1-e5afa04cd938.png")
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

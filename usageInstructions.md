# TITAN Instruction Manual

## Installation
1.	Open 3D Slicer. In the “Modules” section of the toolbar, find “Extension Wizard” and open the module.
2.	Select “Select Extension”.
3.	In the file explorer that pops up, navigate to where you’ve saved the folder “TITAN”. Select the folder.
4.	In the popup, select “Add selected module to search paths”, then click “Yes”. The extension will take some time to install. You may track the progress in the Python Interactor.
5.	In the “Modules” section of the toolbar, find “TITAN” and open the module.

## Loading Data
6.	Open 3D Slicer. In the “Modules” section of the toolbar, find “TITAN” and open the module.
7.	Once TITAN is open, click "DATA".
8.	Select “Choose Directory to Add”. 
9.	Navigate to folder containing the ROI folders with .tiff images, exported from .mcd file. Select each ROI folder to be loaded into TITAN. Click “OK”.
10.	In the Load Data tab of TITAN, scroll to the bottom of the scroll box. Right-click and select “Create hierarchy from loaded data structure”. This will group the images into their respective ROI.
11.	Go to Data Selection tab and click “Refresh Lists”. The list of ROI and channels will be displayed.

## Visualization
### Thumbnail Overview
1.	In Data Selection, select one ROI and at least one channel to be displayed as single-channel thumbnails.
2.	In Visualization, click “View Thumbnails” and a montage of thumbnails will be displayed.

### Image Overlay
1.	In Visualization, select an ROI from the “ROI:” dropdown menu.
2.	Select a channel for the desired colours to be displayed. The overlaid images will be displayed in their respective colours.

### Thresholding Image Adjustments
1.	Use “Threshold Min” and “Threshold Max” sliders in Visualization to customize the visualization.

### Window/Level Adjustments

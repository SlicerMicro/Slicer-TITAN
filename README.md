![logo v2](https://user-images.githubusercontent.com/21988487/126827263-15f356e4-bef0-4244-8e0e-8a763e223242.PNG)

TITAN is an extension developed for 3D Slicer that is responsible for the pre-processing and analysis tasks of imaging mass cytometry (IMC) data. It performs visualization, segmentation, and various analyses functions on IMC data.

![overview v2](https://user-images.githubusercontent.com/21988487/126827330-1b7fec78-3358-4d61-b2a9-9510cc3d13c8.png)

## Installation
1.	Open 3D Slicer. In the “Modules” section of the toolbar, find “Extension Wizard” and open the module.
2.	Select “Select Extension”.
3.	In the file explorer that pops up, navigate to where you’ve saved the folder “TITAN”. Select the folder.
4.	In the popup, select “Add selected module to search paths”, then click “Yes”. The extension will take some time to install. You may track the progress in the Python Interactor.
5.	In the “Modules” section of the toolbar, find “TITAN” and open the module.
6.	Go to "Edit" -> "Application Settings" and update "Default scene location" to the desired folder for saving results.

## Loading Data
1.	Open 3D Slicer. In the “Modules” section of the toolbar, find “TITAN” and open the module.
2.	Once TITAN is open, click ![data](https://user-images.githubusercontent.com/21988487/113910186-8a902580-97a6-11eb-9af1-e778137daa85.png).
3.	Select “Choose Directory to Add”. 
4.	Navigate to folder containing the ROI folders with .tiff images, exported from .mcd file. Select each ROI folder to be loaded into TITAN. Click “OK”.
5.	In the Load Data tab of TITAN, scroll to the bottom of the scroll box. Right-click and select “Create hierarchy from loaded data structure”. This will group the images into their respective ROI.
6.	Go to Data Selection tab and click “Refresh Lists”. The list of ROI and channels will be displayed.

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
1.	For manual adjustments, click ![windowlevel](https://user-images.githubusercontent.com/21988487/113910116-764c2880-97a6-11eb-94a3-71216879cb63.png)
  a.	Click and drag on the image overlay to adjust the window/level. Up/down adjusts brightness, left/right adjusts contrast.
2.	For automatic adjustments, click the dropdown beside ![windowlevel](https://user-images.githubusercontent.com/21988487/113910116-764c2880-97a6-11eb-94a3-71216879cb63.png) and select “Select region – centered”.
3.	Make a selection on the image to set optimal window/level for the selected region.
4.	To apply the same window/level settings to a different image:
a.	Click “Get Window/Level” in Visualization.
b.	Select the new channel/ROI to apply the adjustments to.
c.	Click “Set Window/Level”.
5.	To save the image, click “Save Image to Current Directory”.

## Segmentation
1.	In Data Selection, select at least one ROI and the nucleus channel (193Ir-NA2).
2.	In Segmentation, choose the minimum and maximum nucleus area, and cell radius. Default values are 5, 40, and 3 respectively.
3.	Click “Create Nucleus, Cell, and Cytoplasm Masks”. The resulting masks as well as number of cells will be displayed.

## Analysis
Cell masks for ROI must be created prior to using any of the following functions.

### Histogram
1.	In Data Selection, select at least one ROI and channel.
2.	In Analysis, click “Create Histogram”.
3.	Click “Save Table” to save the data in a .csv file if desired.

### Heat Map
1.	In Data Selection, select at least one ROI and channel.
2.	In Analysis, click “Create Heatmap”.

### Heat Map Channel Overlay
1.	In Data Selection, select one ROI and two channels.
2.	In Analysis, click “Create Heatmap on Selected Channel”.
3.	Click “Save Table” to save the data in a .csv file if desired.

### Scatter Plot
1.	In Data Selection, select one ROI and one channel.
2.	In Analysis, click “Create Scatter Plot”.
3.	Click “Save Table” to save the data in a .csv file if desired.

### Gating on Scatter Plot
1.	Type in the name of your gate (eg. T cells)
2.	In plot window (top right), click the pin icon to open the plot menu.
3.	In the “Interaction mode” drop down, select either “select points” (makes a rectangular selection) or “free-hand select points” (makes free-hand selection).
4.	Make selection on the points on plot to be gated. The cell mask (top left) will be updated to only display the selected cells and the number of selected cells will be displayed.
5.	In the box below, select the mask that you would like to use for further scatter plot analysis.
6.	In Data Selection, choose the two channels to plot with only the selected cells.
7.	In Analysis, click “Create Scatter Plot”.

### Gating on Image/Cell Mask
1.	Type in the name of your gate (eg. T cells)
2.	In the Slicer toolbar, click  . This will take you to the “Segment Editor” module.
3.	Click “Add”  “Draw”.
4.	Draw your selection on either the image or cell mask and then right-click to create the selection.
5.	Navigate back to “TITAN” module and click “Update plot from image selection in Analysis.
6.	In the box below, select the mask that you would like to use for further scatter plot analysis.
7.	In Data Selection, choose the two channels to plot with only the selected cells.
8.	In Analysis, click “Create Scatter Plot”.

## Advanced Analysis
Cell masks for ROI must be created prior to using any of the following functions. Following functions can also be very computationally intensive depending on the data (i.e. number of cells, number of channels, etc.), can take significant amount of time to run.

### Raw Data Table
1.	In Advanced, click “Create Table”. Will create a table of mean intensity values of each channel for each cell across all ROI.

### Dimensionality Reduction (t-SNE/PCA)
1.	In Data Selection, select at least one ROI and channel.
2.	In Advanced, click either “Create t-SNE Plot” or “Create PCA plot” depending on which dimensionality reduction method you would like to use. 
3.	Gating can be done on plot if data in plot comes from only one ROI

### Clustering (K-Means/Hierarchical)
<i>Requires t-SNE or PCA plot to already have been created.</i>
1.	In Advanced, select the “Number of Clusters” desired.
2.	Click either “Create K-Means Cluster” or “Create Hierarchical Cluster” depending on which clustering method you would like to use. 

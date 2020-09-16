import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import numpy as np
import pip
from pip._internal import main
import math
import SimpleITK as sitk
import re

# Need to run Slicer as an administrator in order to install matplotlib
# try:
#   import matplotlib
# except:
#   main(["install", "matplotlib"])
# from matplotlib import pyplot as plt

# # Install sklearn
# main(["install", "sklearn"])
# # Install seaborn
# main(["install", "seaborn"])

# load the python wrapped OpenCV module
# Taken from Slicer github
# try:
#     print 'Trying to import cv2'
#     # the module is in the python path
#     import cv2
#
#     print 'Imported!'
# except ImportError:
#     print 'Trying to import from file'
#     # for the build directory, load from the file
#     import imp, platform
#
#     if platform.system() == 'Windows':
#         cv2File = 'cv2.pyd'
#         cv2Path = '../../../../OpenCV-build/lib/Release/' + cv2File
#     else:
#         cv2File = 'cv2.so'
#         cv2Path = '../../../../OpenCV-build/lib/' + cv2File
#     cv2Path = os.path.abspath(os.path.join(scriptPath, cv2Path))
#     # in the build directory, this path should exist, but in the installed extension
#     # it should be in the python path, so only use the short file name
#     if not os.path.isfile(cv2Path):
#         print 'Full path not found: ', cv2Path
#         cv2Path = cv2File
#     print 'Loading cv2 from ', cv2Path
#     cv2 = imp.load_dynamic('cv2', cv2File)


# TO DO:
# Analysis: figure out what they want to see in the yellow and green windows
# Stretch out graph so that points aren't all in one end
# For PCA plot, use sklearn.decomposition to create the data, then plot this data
# Add all ROI's for one channel into a volume by just making a [501, 500, 5] (if 5 ROI's)

# Define global variables
import time

nodeName = '\\result_{}.png'.format(int(time.time()))
globalCellMask = {}
roiNames = []
channelNames = []
selectedRoi = None
selectedChannel = None
scatterPlotRoi = None


#
# HypModule
#

class HypModuleCode(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Hyperion Analysis"  # TODO make this more human readable by adding spaces
        self.parent.categories = ["Analysis"]
        self.parent.dependencies = []
        self.parent.contributors = [
            "Sindhura Thirumal (Med-i Lab Queen's University)"]  # replace with "Firstname Lastname (Organization)"
        self.parent.helpText = """
This is an analysis pipeline catered towards Hyperion data.
It allows for visualization, mask creation, and statistical analyses.
"""
        self.parent.helpText += self.getDefaultModuleDocumentationLink()
        self.parent.acknowledgementText = """
This file was originally developed by Sindhura Thirumal, Med-i Lab at Queen's University.
"""  # replace with organization, grant and thanks.

        # Set module icon from Resources/Icons/<ModuleName>.png
        moduleDir = os.path.dirname(self.parent.path)
        iconPath = os.path.join(moduleDir, 'Resources/Icons', self.moduleName + '.png')
        if os.path.isfile(iconPath):
            parent.icon = qt.QIcon(iconPath)

        # Add this test to the SelfTest module's list for discovery when the module
        # is created.  Since this module may be discovered before SelfTests itself,
        # create the list if it doesn't already exist.
        try:
            slicer.selfTests
        except AttributeError:
            slicer.selfTests = {}
        slicer.selfTests[self.moduleName] = self.runTest


#
# HypModuleWidget
#

class HypModuleCodeWidget(ScriptedLoadableModuleWidget):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)

        # Load widget from .ui file (created by Qt Designer)
        uiWidget = slicer.util.loadUI(self.resourcePath('UI/HypModuleCode.ui'))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Set inputs to be a MRML node in a scene

        # Data
        self.ui.subjectHierarchy.setMRMLScene(slicer.mrmlScene)
        # self.ui.dataSelection.setMRMLScene(slicer.mrmlScene)

        # Connections

        # Data

        self.ui.roiList.connect("itemSelectionChanged()", self.onRoiList)
        self.ui.channelList.connect("itemSelectionChanged()", self.onChannelList)
        self.ui.refreshLists.connect("clicked(bool)", self.onRefreshLists)

        # Visualization
        self.ui.resetViewButton.connect("clicked(bool)", self.onReset)

        self.ui.roiVisualization.connect("activated(int)", self.onVisualization)

        self.ui.redSelect.connect("activated(int)", self.onVisualization)
        self.ui.greenSelect.connect("activated(int)", self.onVisualization)
        self.ui.blueSelect.connect("activated(int)", self.onVisualization)
        self.ui.yellowSelect.connect("activated(int)", self.onVisualization)
        self.ui.cyanSelect.connect("activated(int)", self.onVisualization)
        self.ui.magentaSelect.connect("activated(int)", self.onVisualization)
        self.ui.whiteSelect.connect("activated(int)", self.onVisualization)

        self.ui.threshMinSlider.connect('valueChanged(int)', self.onVisualization)
        self.ui.threshMaxSlider.connect('valueChanged(int)', self.onVisualization)

        self.ui.getWLButton.connect("clicked(bool)", self.onGetWL)
        self.ui.setWLButton.connect("clicked(bool)", self.onSetWL)

        self.ui.saveImgButton.connect('clicked(bool)', self.onSaveButton)

        # Add vertical spacer
        self.layout.addStretch(1)

        # Mask Creation
        self.ui.crtMaskButton.connect('clicked(bool)', self.onCreateMasks)

        # Analysis
        self.ui.crtPlotButton.connect('clicked(bool)', self.onCreatePlot)

        self.ui.analysisResetButton.connect("clicked(bool)", self.onReset)

        self.ui.saveHistoTable.connect('clicked(bool)', self.onHistoSave)

        self.ui.crtHeatmapChannel.connect('clicked(bool)', self.onHeatmapChannelPlot)
        self.ui.saveHeatmapTable.connect('clicked(bool)', self.onHeatmapSaveTable)

        self.ui.crtScatterButton.connect('clicked(bool)', self.onScatterPlot)
        self.ui.saveScatPlotTable.connect('clicked(bool)', self.onScatPlotSaveTable)

        self.ui.crtHeatmapButton.connect('clicked(bool)', self.onHeatmapPlot)

    def cleanup(self):
        pass

    def onReset(self):
        slicer.util.resetSliceViews()

    def onSubjectHierarchy(self):
        print(self.ui.subjectHierarchy.currentItems)

    # Whenever something is updated in Visualization tab, this function runs
    def onVisualization(self):
        logic = HypModuleLogic()

        logic.visualizationRun(self.ui.roiVisualization.currentText, self.ui.redSelect.currentText,
                               self.ui.greenSelect.currentText, self.ui.blueSelect.currentText,
                               self.ui.yellowSelect.currentText, self.ui.cyanSelect.currentText,
                               self.ui.magentaSelect.currentText, self.ui.whiteSelect.currentText, self.ui.threshMinSlider.value,
                               self.ui.threshMaxSlider.value)

        self.ui.fileNameLabel.text = nodeName + ".png"

        self.ui.saveImgButton.enabled = self.ui.roiVisualization.currentText or self.ui.redSelect.currentText or \
                                        self.ui.greenSelect.currentText or self.ui.blueSelect.currentText or \
                                        self.ui.yellowSelect.currentText or self.ui.cyanSelect.currentText or \
                                        self.ui.magentaSelect.currentText or self.ui.whiteSelect.currentText

        self.ui.threshMinSlider.enabled = self.ui.roiVisualization.currentText or self.ui.redSelect.currentText or \
                                        self.ui.greenSelect.currentText or self.ui.blueSelect.currentText or \
                                        self.ui.yellowSelect.currentText or self.ui.cyanSelect.currentText or \
                                        self.ui.magentaSelect.currentText or self.ui.whiteSelect.currentText

        self.ui.threshMaxSlider.enabled = self.ui.roiVisualization.currentText or self.ui.redSelect.currentText or \
                                        self.ui.greenSelect.currentText or self.ui.blueSelect.currentText or \
                                        self.ui.yellowSelect.currentText or self.ui.cyanSelect.currentText or \
                                        self.ui.magentaSelect.currentText or self.ui.whiteSelect.currentText

        self.ui.threshMin.enabled = self.ui.roiVisualization.currentText or self.ui.redSelect.currentText or \
                                        self.ui.greenSelect.currentText or self.ui.blueSelect.currentText or \
                                        self.ui.yellowSelect.currentText or self.ui.cyanSelect.currentText or \
                                        self.ui.magentaSelect.currentText or self.ui.whiteSelect.currentText

        self.ui.threshMax.enabled = self.ui.roiVisualization.currentText or self.ui.redSelect.currentText or \
                                        self.ui.greenSelect.currentText or self.ui.blueSelect.currentText or \
                                        self.ui.yellowSelect.currentText or self.ui.cyanSelect.currentText or \
                                        self.ui.magentaSelect.currentText or self.ui.whiteSelect.currentText
        # self.ui.applyButton.enabled = self.ui.roiVisualization.currentText or self.ui.redSelect.currentText or \
        #                                 self.ui.greenSelect.currentText

    def onGetWL(self):
        currentId = slicer.app.layoutManager().sliceWidget("Red").sliceLogic().GetSliceCompositeNode().GetBackgroundVolumeID()
        currentNode = slicer.util.getNode(currentId)
        displayNode = currentNode.GetDisplayNode()
        window = displayNode.GetWindow()
        level = displayNode.GetLevel()
        self.ui.getWindow.text = str(window)
        self.ui.getLevel.text = str(level)
        self.ui.setWindow.value = window
        self.ui.setLevel.value = level

    def onSetWL(self):
        currentId = slicer.app.layoutManager().sliceWidget("Red").sliceLogic().GetSliceCompositeNode().GetBackgroundVolumeID()
        currentNode = slicer.util.getNode(currentId)
        displayNode = currentNode.GetDisplayNode()
        window = self.ui.setWindow.value
        level = self.ui.setLevel.value
        displayNode.SetWindow(window)
        displayNode.SetLevel(level)

    def onSelect(self):
        self.ui.crtPlotButton.enabled = self.ui.imageHistogramSelect.currentNode() \
                                        and self.ui.imageHistogramSelectTwo.currentNode() \
                                        and self.ui.imageHistogramSelectThree.currentNode()
        # self.ui.crtHeatmapChannel.enabled = self.ui.heatmapChannelSelect.currentNode()
        self.ui.crtScatterButton.enabled = self.ui.channelTwoScatter.currentNode() and self.ui.channelOneScatter.currentNode()

    def onRoiList(self):
        global selectedRoi
        selectedRoi = []
        for item in self.ui.roiList.selectedItems():
            selectedRoi.append(item.text())

    def onChannelList(self):
        global selectedChannel
        selectedChannel = []
        for item in self.ui.channelList.selectedItems():
            selectedChannel.append(item.text())

    def onRefreshLists(self):
        # Get list of ROI's

        global channelNames
        channelNames = []
        global roiNames
        roiNames = []

        # Get list of all channels
        allChannels = slicer.util.getNodesByClass("vtkMRMLScalarVolumeNode")

        # Create dictionary of each channel with its respective ROI
        shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
        for channel in allChannels:
            # if shNode.GetItemName(shNode.GetItemParent(shNode.GetItemByDataNode(channel))) != "Scene":
            itemId = shNode.GetItemByDataNode(channel)  # Channel
            parent = shNode.GetItemParent(itemId)  # ROI
            roiName = shNode.GetItemName(parent)
            channelName = shNode.GetItemName(itemId)
            if re.findall(r"_[0-9]\b", channelName) != []:
                channelName = channelName[:-2]
            if channelName not in channelNames:
                if channelName.endswith(".ome"):
                    channelNames.append(channelName)
            if roiName not in roiNames:
                roiNames.append(roiName)
        if roiNames == ["Scene"]:
            roiNames = ["ROI"]


        # Display ROI's and Channels in list widget

        self.ui.roiList.clear()
        self.ui.channelList.clear()
        self.ui.roiVisualization.clear()
        self.ui.redSelect.clear()
        self.ui.blueSelect.clear()
        self.ui.greenSelect.clear()
        self.ui.yellowSelect.clear()
        self.ui.cyanSelect.clear()
        self.ui.magentaSelect.clear()
        self.ui.whiteSelect.clear()

        self.ui.redSelect.addItem("None")
        self.ui.greenSelect.addItem("None")
        self.ui.blueSelect.addItem("None")
        self.ui.yellowSelect.addItem("None")
        self.ui.cyanSelect.addItem("None")
        self.ui.magentaSelect.addItem("None")
        self.ui.whiteSelect.addItem("None")

        for roi in roiNames:
            if roi != "Scene":
                self.ui.roiList.addItem(roi)
                self.ui.roiVisualization.addItem(roi)
        for channel in channelNames:
            self.ui.channelList.addItem(channel)
            self.ui.redSelect.addItem(channel)
            self.ui.greenSelect.addItem(channel)
            self.ui.blueSelect.addItem(channel)
            self.ui.yellowSelect.addItem(channel)
            self.ui.cyanSelect.addItem(channel)
            self.ui.magentaSelect.addItem(channel)
            self.ui.whiteSelect.addItem(channel)

    # When "Save Image" is clicked, run saveVisualization function
    def onSaveButton(self):
        logic = HypModuleLogic()
        logic.saveVisualization(self.ui.fileNameLabel.text)

    # When Create Nucleus Mask is clicked, run nucleusMaskRun function
    def onCreateMasks(self):
        if selectedChannel is None or len(selectedChannel) != 1:
            self.ui.segmentationErrorMessage.text = "ERROR: 1 channel should be selected."
            return
        elif selectedRoi is None or len(selectedRoi) == 0:
            self.ui.segmentationErrorMessage.text = "ERROR: Minimum 1 ROI should be selected."
            return
        else:
            self.ui.segmentationErrorMessage.text = ""
        logic = HypModuleLogic()
        nucleiMin = self.ui.nucleiMin.value
        nucleiMax = self.ui.nucleiMax.value
        cellDim = self.ui.cellDimInput.value
        nCells = logic.crtMasksRun(nucleiMin, nucleiMax, cellDim)
        nCellsText = []
        for roi in nCells:
            nCellsText.append(roi + ": " + str(nCells[roi]))
        self.ui.nCellsLabel.text = "\n".join(nCellsText)

    def onCreatePlot(self):
        if selectedChannel is None or len(selectedChannel) < 1:
            self.ui.analysisErrorMessage.text = "ERROR: Minimum 1 channel should be selected."
            return
        elif selectedRoi is None or len(selectedRoi) == 0:
            self.ui.analysisErrorMessage.text = "ERROR: Minimum 1 ROI should be selected."
            return
        else:
            self.ui.analysisErrorMessage.text = ""
        logic = HypModuleLogic()
        logic.analysisRun()

    def onHistoSave(self):
        logic = HypModuleLogic()
        logic.saveTableData()

    def onHeatmapChannelPlot(self):
        if selectedChannel is None or len(selectedChannel) != 1:
            self.ui.analysisErrorMessage.text = "ERROR: 1 channel should be selected."
            return
        elif selectedRoi is None or len(selectedRoi) != 1:
            self.ui.analysisErrorMessage.text = "ERROR: 1 ROI should be selected."
            return
        elif len(globalCellMask) == 0:
            self.ui.analysisErrorMessage.text = "ERROR: Masks have not been created."
            return
        else:
            self.ui.analysisErrorMessage.text = ""
        logic = HypModuleLogic()
        logic.heatmapChannelRun()

    def onHeatmapSaveTable(self):
        logic = HypModuleLogic()
        logic.saveTableData()

    def onScatterPlot(self):
        if selectedChannel is None or len(selectedChannel) != 2:
            self.ui.analysisErrorMessage.text = "ERROR: 2 channels should be selected."
            return
        elif selectedRoi is None or len(selectedRoi) != 1:
            self.ui.analysisErrorMessage.text = "ERROR: 1 ROI should be selected."
            return
        elif len(globalCellMask) == 0:
            self.ui.analysisErrorMessage.text = "ERROR: Masks have not been created."
            return
        else:
            self.ui.analysisErrorMessage.text = ""

        self.ui.selectedCellsCount.text = ""

        logic = HypModuleLogic()

        # If check box is checked, use the selected cells mask for the scatter plot
        if self.ui.checkBoxSelectedCells.checkState() == 0:
            logic.scatterPlotRun(False)
        else:
            logic.scatterPlotRun(True)

        # Scatter plot gating signal
        layoutManager = slicer.app.layoutManager()
        plotWidget = layoutManager.plotWidget(0)
        plotView = plotWidget.plotView()
        plotView.connect("dataSelected(vtkStringArray*, vtkCollection*)", self.onDataSelected)

    def onDataSelected(self, mrmlPlotDataIDs, selectionCol):
        """
        Runs when user selects point on scatter plot
        """

        # Delete any existing selected cell masks
        existingMasks = slicer.util.getNodesByClass("vtkMRMLScalarVolumeNode")



        for selectionIndex in range(mrmlPlotDataIDs.GetNumberOfValues()):
            pointIdList = []
            pointIds = selectionCol.GetItemAsObject(selectionIndex)
            for pointIndex in range(pointIds.GetNumberOfValues()):
                pointIdList.append(pointIds.GetValue(pointIndex))
            # The value returned is the row number of that cell, however you need to add 2 to the value to get
            # the correct number. eg. value 171 actually refers to the cell at row 173.
            # BUT in the code, the incorrect row number returned actually works out to refer to the correct cell

        # Get cell number
        tables = slicer.util.getNodesByClass("vtkMRMLTableNode")
        tableNode = tables[0]
        cellLabels = []
        for cell in pointIdList:
            label = tableNode.GetCellText(cell, 2)
            cellLabels.append(label)
        cellCount = len(cellLabels)
        self.ui.selectedCellsCount.text = cellCount

        # Get cell mask array
        # global globalCellMask
        #
        # cellMaskId = slicer.app.layoutManager().sliceWidget("Red").sliceLogic().GetSliceCompositeNode().GetBackgroundVolumeID()
        # cellNode = slicer.util.getNode(cellMaskId)
        # cellName = cellNode.GetName()
        #
        # roi = None
        #
        # if "Cell Mask: Selected Cells" in cellName:
        #     roi = "Selected Cells"
        # else:
        #     roi = scatterPlotRoi

        cellMaskNode = globalCellMask[scatterPlotRoi]
        cellMaskArray = slicer.util.arrayFromVolume(cellMaskNode)
        selectedCellsMask = np.copy(cellMaskArray)

        # Remove cells in the array that aren't part of the selected cells
        for cell in np.unique(selectedCellsMask):
            if cell != 0:
                if str(cell) not in cellLabels:
                    selectedCellsMask[selectedCellsMask == cell] = 0

        # Create new cell mask image
        name = "Cell Mask: Selected Cells"

        volumeNode = slicer.modules.volumes.logic().CloneVolume(cellMaskNode, name)
        slicer.util.updateVolumeFromArray(volumeNode, selectedCellsMask)

        # Add to global list of cell masks
        globalCellMask["Selected Cells"] = volumeNode

        # Change colormap of volume
        # labels = slicer.util.getFirstNodeByName("Labels")
        # maskDisplayNode = volumeNode.GetScalarVolumeDisplayNode()
        # maskDisplayNode.SetAndObserveColorNodeID(labels.GetID())
        red_logic = slicer.app.layoutManager().sliceWidget("Red").sliceLogic()
        red_logic.GetSliceCompositeNode().SetBackgroundVolumeID(volumeNode.GetID())

        for img in existingMasks:
            if "Cell Mask: Selected Cells" in img.GetName():
                slicer.mrmlScene.RemoveNode(img)

    def onScatPlotSaveTable(self):
        logic = HypModuleLogic()
        logic.saveTableData()

    def onHeatmapPlot(self):
        if selectedChannel is None or len(selectedChannel) < 1:
            self.ui.analysisErrorMessage.text = "ERROR: Minimum 1 channel should be selected."
            return
        elif selectedRoi is None or len(selectedRoi) < 1:
            self.ui.analysisErrorMessage.text = "ERROR: Minimum 1 ROI should be selected."
            return
        else:
            self.ui.analysisErrorMessage.text = ""

        logic = HypModuleLogic()
        logic.heatmapRun()

#
# HypModuleLogic
#


class HypModuleLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def hasImageData(self, volumeNode):
        """This is an example logic method that
        returns true if the passed in volume
        node has valid image data
        """
        if not volumeNode:
            logging.debug('hasImageData failed: no volume node')
            return False
        if volumeNode.GetImageData() is None:
            logging.debug('hasImageData failed: no image data in volume node')
            return False
        return True


    def visualizationRun(self, roiSelect, redSelect, greenSelect, blueSelect, yellowSelect, cyanSelect, magentaSelect, whiteSelect, threshMin, threshMax):
        """
        Runs the algorithm to display the volumes selected in "Visualization" in their respective colours
        """
        # Delete any existing image overlays
        existingOverlays = slicer.util.getNodesByClass("vtkMRMLVectorVolumeNode")

        # Make dictionary of the selected channels
        selectChannels = {} # key = colour, value = node
        shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
        allChannels = slicer.util.getNodesByClass("vtkMRMLScalarVolumeNode")
        for channel in allChannels:
            name = channel.GetName()
            if redSelect in name:
                # Check if channel is the correct ROI
                id = shNode.GetItemByDataNode(channel)
                parent = shNode.GetItemParent(id)
                roiName = shNode.GetItemName(parent)
                if roiName == roiSelect:
                    selectChannels["red"] = channel
            elif greenSelect in name:
                # Check if channel is the correct ROI
                id = shNode.GetItemByDataNode(channel)
                parent = shNode.GetItemParent(id)
                roiName = shNode.GetItemName(parent)
                if roiName == roiSelect:
                    selectChannels["green"] = channel
            elif blueSelect in name:
                # Check if channel is the correct ROI
                id = shNode.GetItemByDataNode(channel)
                parent = shNode.GetItemParent(id)
                roiName = shNode.GetItemName(parent)
                if roiName == roiSelect:
                    selectChannels["blue"] = channel
            elif yellowSelect in name:
                # Check if channel is the correct ROI
                id = shNode.GetItemByDataNode(channel)
                parent = shNode.GetItemParent(id)
                roiName = shNode.GetItemName(parent)
                if roiName == roiSelect:
                    selectChannels["yellow"] = channel
            elif cyanSelect in name:
                # Check if channel is the correct ROI
                id = shNode.GetItemByDataNode(channel)
                parent = shNode.GetItemParent(id)
                roiName = shNode.GetItemName(parent)
                if roiName == roiSelect:
                    selectChannels["cyan"] = channel
            elif magentaSelect in name:
                # Check if channel is the correct ROI
                id = shNode.GetItemByDataNode(channel)
                parent = shNode.GetItemParent(id)
                roiName = shNode.GetItemName(parent)
                if roiName == roiSelect:
                    selectChannels["magenta"] = channel
            elif whiteSelect in name:
                # Check if channel is the correct ROI
                id = shNode.GetItemByDataNode(channel)
                parent = shNode.GetItemParent(id)
                roiName = shNode.GetItemName(parent)
                if roiName == roiSelect:
                    selectChannels["white"] = channel
        saveImageName = ""
        arrayList = []
        arraySize = None
        for colour in selectChannels:
            if colour == "red":
                name = redSelect[:-4]
                saveImageName += name
                # Set redscale array
                array = slicer.util.arrayFromVolume(selectChannels[colour])
                # Scale the array
                scaled = np.interp(array, (array.min(), array.max()), (0, 255))
                if arraySize == None:
                    arraySize = scaled.shape
                stacked = np.stack((scaled,) * 3, axis=-1)
                stacked[:, :, :, 1] = 0
                stacked[:, :, :, 2] = 0
                arrayList.append(stacked)
            elif colour == "green":
                name = greenSelect[:-4]
                saveImageName += name
                # Set greenscale array
                array = slicer.util.arrayFromVolume(selectChannels[colour])
                # Scale the array
                scaled = np.interp(array, (array.min(), array.max()), (0, 255))
                if arraySize == None:
                    arraySize = scaled.shape
                stacked = np.stack((scaled,) * 3, axis=-1)
                stacked[:, :, :, 0] = 0
                stacked[:, :, :, 2] = 0
                arrayList.append(stacked)
            elif colour == "blue":
                name = blueSelect[:-4]
                saveImageName += name
                # Set bluescale array
                array = slicer.util.arrayFromVolume(selectChannels[colour])
                # Scale the array
                scaled = np.interp(array, (array.min(), array.max()), (0, 255))
                if arraySize == None:
                    arraySize = scaled.shape
                stacked = np.stack((scaled,) * 3, axis=-1)
                stacked[:, :, :, 0] = 0
                stacked[:, :, :, 1] = 0
                arrayList.append(stacked)
            elif colour == "yellow":
                name = yellowSelect[:-4]
                saveImageName += name
                # Set bluescale array
                array = slicer.util.arrayFromVolume(selectChannels[colour])
                # Scale the array
                scaled = np.interp(array, (array.min(), array.max()), (0, 255))
                if arraySize == None:
                    arraySize = scaled.shape
                stacked = np.stack((scaled,) * 3, axis=-1)
                stacked[:, :, :, 2] = 0
                arrayList.append(stacked)
            elif colour == "cyan":
                name = cyanSelect[:-4]
                saveImageName += name
                # Set bluescale array
                array = slicer.util.arrayFromVolume(selectChannels[colour])
                # Scale the array
                scaled = np.interp(array, (array.min(), array.max()), (0, 255))
                if arraySize == None:
                    arraySize = scaled.shape
                stacked = np.stack((scaled,) * 3, axis=-1)
                stacked[:, :, :, 0] = 0
                arrayList.append(stacked)
            elif colour == "magenta":
                name = magentaSelect[:-4]
                saveImageName += name
                # Set bluescale array
                array = slicer.util.arrayFromVolume(selectChannels[colour])
                # Scale the array
                scaled = np.interp(array, (array.min(), array.max()), (0, 255))
                if arraySize == None:
                    arraySize = scaled.shape
                stacked = np.stack((scaled,) * 3, axis=-1)
                stacked[:, :, :, 1] = 0
                arrayList.append(stacked)
            elif colour == "white":
                name = whiteSelect[:-4]
                saveImageName += name
                # Set bluescale array
                array = slicer.util.arrayFromVolume(selectChannels[colour])
                # Scale the array
                scaled = np.interp(array, (array.min(), array.max()), (0, 255))
                if arraySize == None:
                    arraySize = scaled.shape
                stacked = np.stack((scaled,) * 3, axis=-1)
                arrayList.append(stacked)

        overlay = sum(arrayList)

        # Run helper function
        HypModuleLogic().visualizationRunHelper(overlay, threshMin, threshMax, saveImageName, arraySize,
                                                existingOverlays)
        return True


    def visualizationRunHelper(self, overlay, threshMin, threshMax, saveImageName, arraySize, existingOverlays):

        # Set array with thresholded values
        overlay[overlay < threshMin] = 0
        threshMaxVal = 255 - threshMax
        overlay[overlay > threshMaxVal] = 255

        # Create new volume "Image Overlay"
        # Set name of overlaid image to be the names of all the channels being overlaid
        imageSize = [arraySize[2], arraySize[1], 1]
        voxelType = vtk.VTK_UNSIGNED_CHAR
        imageOrigin = [0.0, 0.0, 0.0]
        imageSpacing = [1.0, 1.0, 1.0]
        imageDirections = [[-1, 0, 0], [0, -1, 0], [0, 0, 1]]
        fillVoxelValue = 0

        # Create an empty image volume, filled with fillVoxelValue
        imageData = vtk.vtkImageData()
        imageData.SetDimensions(imageSize)
        imageData.AllocateScalars(voxelType, 3)
        imageData.GetPointData().GetScalars().Fill(fillVoxelValue)

        # Create volume node
        # Needs to be a vector volume in order to show in colour
        volumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLVectorVolumeNode", saveImageName)
        volumeNode.SetOrigin(imageOrigin)
        volumeNode.SetSpacing(imageSpacing)
        volumeNode.SetIJKToRASDirections(imageDirections)
        volumeNode.SetAndObserveImageData(imageData)
        volumeNode.CreateDefaultDisplayNodes()
        volumeNode.CreateDefaultStorageNode()

        voxels = slicer.util.arrayFromVolume(volumeNode)
        voxels[:] = overlay

        volumeNode.Modified()

        volumeNode.GetDisplayNode().AutoWindowLevelOff()
        volumeNode.GetDisplayNode().SetWindowLevel((arraySize[1] // 4), 127)

        slicer.util.setSliceViewerLayers(background=volumeNode, foreground=None)

        for overlay in existingOverlays:
            slicer.mrmlScene.RemoveNode(overlay)

        global nodeName
        nodeName = saveImageName
        # Set slice view to display Red window only
        lm = slicer.app.layoutManager()
        lm.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpRedSliceView)

        # Reset field of view to show entire image
        slicer.util.resetSliceViews()

    def saveVisualization(self, fileName):
        viewNodeID = 'vtkMRMLSliceNodeRed'
        import ScreenCapture
        cap = ScreenCapture.ScreenCaptureLogic()
        view = cap.viewFromNode(slicer.mrmlScene.GetNodeByID(viewNodeID))
        pathName = os.getcwd() + '\\' + fileName
        cap.captureImageFromView(view, pathName)
        import subprocess
        subprocess.Popen(r'explorer /select,' + pathName)

    def crtMasksRun(self, nucleiMin, nucleiMax, cellDimInput):
        """
        Perform threshold segmentation on the nucleiImageInput
        """

        # Get list of all channels
        allChannels = slicer.util.getNodesByClass("vtkMRMLScalarVolumeNode")

        # Create dictionary of each channel with its respective ROI
        shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
        parentDict = {}
        for channel in allChannels:
            itemId = shNode.GetItemByDataNode(channel)  # Channel
            parent = shNode.GetItemParent(itemId)  # ROI
            roiName = shNode.GetItemName(parent)
            channelName = shNode.GetItemName(itemId)
            if re.findall(r"_[0-9]\b", channelName) != []:
                channelName = channelName[:-2]
            # Check if the specific channel was selected
            if roiName == "Scene":
                roiName = "ROI"
            if roiName in selectedRoi and channelName in selectedChannel:
                parentDict[itemId] = roiName

        # Set dictionary for number of cells of each mask
        nCells = {}

        # Set "global" variables for nucleus, cell, and cytoplasm volumes, in order to display later
        nucleusMaskVolume = None
        cellMaskVolume = None
        cytoplasmMaskVolume = None
        dnaNode = None

        # For each nucleus mask, run this loop; parentDict length should be number of ROI's
        for itemId in parentDict:
            # Get array of channel
            roiName = parentDict[itemId]
            dnaName = shNode.GetItemName(itemId)
            dnaNode = slicer.util.getNode(dnaName)
            dnaArray = slicer.util.arrayFromVolume(dnaNode)
            dnaImg = sitk.GetImageFromArray(dnaArray)

            # Delete any existing masks
            existingVolumes = slicer.util.getNodesByClass("vtkMRMLScalarVolumeNode")

            for img in existingVolumes:
                if roiName + " Nucleus Mask" in img.GetName():
                    slicer.mrmlScene.RemoveNode(img)
                elif roiName + " Cell Mask" in img.GetName():
                    slicer.mrmlScene.RemoveNode(img)
                elif roiName + " Cytoplasm Mask" in img.GetName():
                    slicer.mrmlScene.RemoveNode(img)

            # Rescale image
            filter = sitk.RescaleIntensityImageFilter()
            filter.SetOutputMinimum(0)
            filter.SetOutputMaximum(255)
            rescaled = filter.Execute(dnaImg)
            # Adjust contrast
            filter = sitk.AdaptiveHistogramEqualizationImageFilter()
            contrasted = filter.Execute(rescaled)
            # Otsu thresholding
            filter = sitk.OtsuThresholdImageFilter()
            t_otsu = filter.Execute(contrasted)
            # Closing
            filter = sitk.BinaryMorphologicalClosingImageFilter()
            binImg = filter.Execute(t_otsu)

            # Connected-component labeling
            min_img = sitk.RegionalMinima(binImg, backgroundValue=0, foregroundValue=1.0, fullyConnected=False,
                                          flatIsMinima=True)
            labeled = sitk.ConnectedComponent(min_img)
            # Fill holes in image
            filter = sitk.BinaryFillholeImageFilter()
            filled = filter.Execute(binImg)
            # Distance Transform
            dist = sitk.SignedMaurerDistanceMap(filled != 0, insideIsPositive=False, squaredDistance=False,
                                                useImageSpacing=False)
            # Get seeds
            # if dnaImg.GetSpacing()[0] <= 0.001:
            #     sigma = dnaImg.GetSpacing()[0]
            # else:
            #     sigma = 0.001
            sigma = 0.0001
            seeds = sitk.ConnectedComponent(dist < -sigma)
            seeds = sitk.RelabelComponent(seeds)

            # Invert distance transform to use with watershed
            distInvert = -1*dist
            # Watershed using distance transform
            ws = sitk.MorphologicalWatershedFromMarkers(distInvert, seeds)
            ws = sitk.Mask(ws, sitk.Cast(labeled, ws.GetPixelID()))
            ws = sitk.ConnectedComponent(ws)

            # Generate nucleus mask array
            nucleusMaskArray = sitk.GetArrayFromImage(ws)

            # Remove nuclei too small or large
            stats = sitk.LabelShapeStatisticsImageFilter()
            stats.Execute(ws)

            labelSizes = {}

            for label in stats.GetLabels():
                labelSizes[label] = stats.GetNumberOfPixels(label)

            for i in labelSizes:
                if i != 0:
                    if labelSizes[i] > nucleiMax:
                        nucleusMaskArray[nucleusMaskArray == i] = 0
                    elif labelSizes[i] < nucleiMin:
                        nucleusMaskArray[nucleusMaskArray == i] = 0

            # Manually remove border cells
            nucMaskShape = nucleusMaskArray.shape
            for i in range(nucMaskShape[2]):
                label = nucleusMaskArray[0][0][i]
                if label != 0:
                    nucleusMaskArray[nucleusMaskArray == label] = 0
                label = nucleusMaskArray[0][nucMaskShape[1]-1][i]
                if label != 0:
                    nucleusMaskArray[nucleusMaskArray == label] = 0
            for i in range(nucMaskShape[1]):
                label = nucleusMaskArray[0][i][0]
                if label != 0:
                    nucleusMaskArray[nucleusMaskArray == label] = 0
                label = nucleusMaskArray[0][i][nucMaskShape[2] - 1]
                if label != 0:
                    nucleusMaskArray[nucleusMaskArray == label] = 0

            # Create simpleitk object of nucleus mask
            nucleusMaskObject = sitk.GetImageFromArray(nucleusMaskArray)

            # Create new volume using the nucleus mask array
            name = roiName + " Nucleus Mask"
            nucleusMaskVolume = slicer.modules.volumes.logic().CloneVolume(dnaNode, name)
            slicer.util.updateVolumeFromArray(nucleusMaskVolume, nucleusMaskArray)

            # Change colormap of volume
            labels = slicer.util.getFirstNodeByName("Labels")
            nucleusDisplayNode = nucleusMaskVolume.GetScalarVolumeDisplayNode()
            nucleusDisplayNode.SetAndObserveColorNodeID(labels.GetID())

            # Create cell mask
            # cellDilate = sitk.BinaryDilate(nucleusMaskObject!=0, cellDimInput)
            filter = sitk.BinaryDilateImageFilter()
            filter.SetKernelRadius(cellDimInput)
            cellDilate = filter.Execute(nucleusMaskObject!=0)
            distCell = sitk.SignedMaurerDistanceMap(nucleusMaskObject != 0, insideIsPositive=False, squaredDistance=False,
                                                    useImageSpacing=False)
            wsdCell = sitk.MorphologicalWatershedFromMarkers(distCell, nucleusMaskObject, markWatershedLine=False)
            cellMask = sitk.Mask(wsdCell, cellDilate)
            cellMaskArray = sitk.GetArrayFromImage(cellMask)

            # Manually remove border cells
            cellMaskShape = cellMaskArray.shape
            for i in range(cellMaskShape[2]):
                label = cellMaskArray[0][0][i]
                if label != 0:
                    cellMaskArray[cellMaskArray == label] = 0
                label = cellMaskArray[0][cellMaskShape[1] - 1][i]
                if label != 0:
                    cellMaskArray[cellMaskArray == label] = 0
            for i in range(cellMaskShape[1]):
                label = cellMaskArray[0][i][0]
                if label != 0:
                    cellMaskArray[cellMaskArray == label] = 0
                label = cellMaskArray[0][i][cellMaskShape[2] - 1]
                if label != 0:
                    cellMaskArray[cellMaskArray == label] = 0

            nCells[roiName] = len(np.unique(cellMaskArray)) - 1 # subtracting 1 for the "0" labels

            # Create new volume using cell mask array
            name = roiName + " Cell Mask"
            cellMaskVolume = slicer.modules.volumes.logic().CloneVolume(dnaNode, name)
            slicer.util.updateVolumeFromArray(cellMaskVolume, cellMaskArray)
            global globalCellMask
            globalCellMask[roiName] = cellMaskVolume

            # Change colormap of volume
            labels = slicer.util.getFirstNodeByName("Labels")
            cellDisplayNode = cellMaskVolume.GetScalarVolumeDisplayNode()
            cellDisplayNode.SetAndObserveColorNodeID(labels.GetID())

            # Create cytoplasm mask
            cytoplasmMaskArray = cellMaskArray[:]
            cytoplasmMaskArray[cytoplasmMaskArray == nucleusMaskArray] = 0

            # Create new volume using cytoplasm mask array
            name = roiName + " Cytoplasm Mask"
            cytoplasmMaskVolume = slicer.modules.volumes.logic().CloneVolume(dnaNode, name)
            slicer.util.updateVolumeFromArray(cytoplasmMaskVolume, cytoplasmMaskArray)

            # Change colormap of volume
            labels = slicer.util.getFirstNodeByName("Labels")
            cytoplasmDisplayNode = cytoplasmMaskVolume.GetScalarVolumeDisplayNode()
            cytoplasmDisplayNode.SetAndObserveColorNodeID(labels.GetID())

        # View nucleus image in window
        slicer.util.setSliceViewerLayers(background=nucleusMaskVolume, foreground=None)
        lm = slicer.app.layoutManager()
        lm.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutTwoOverTwoView)

        # Set red slice to show the heatmap
        red_logic = slicer.app.layoutManager().sliceWidget("Red").sliceLogic()
        red_logic.GetSliceCompositeNode().SetBackgroundVolumeID(nucleusMaskVolume.GetID())

        # Set yellow slice to show cloned, thresholded channel
        yellow_widget = slicer.app.layoutManager().sliceWidget("Yellow")
        yellow_widget.setSliceOrientation("Axial")
        # yellowDisplayNode = channelOne.GetScalarVolumeDisplayNode()
        # yellowDisplayNode.SetAndObserveColorNodeID("vtkMRMLColorTableNodeRed")
        yellow_logic = yellow_widget.sliceLogic()
        yellow_logic.GetSliceCompositeNode().SetBackgroundVolumeID(cellMaskVolume.GetID())

        # Set green slice to show cell mask
        green_widget = slicer.app.layoutManager().sliceWidget("Green")
        green_widget.setSliceOrientation("Axial")
        # greenDisplayNode = channelTwo.GetScalarVolumeDisplayNode()
        # greenDisplayNode.SetAndObserveColorNodeID("vtkMRMLColorTableNodeRed")
        green_logic = green_widget.sliceLogic()
        green_logic.GetSliceCompositeNode().SetBackgroundVolumeID(cytoplasmMaskVolume.GetID())

        # Set black slice to show original nucleus channel
        blackDisplayNode = dnaNode.GetScalarVolumeDisplayNode()
        blackDisplayNode.SetAndObserveColorNodeID("vtkMRMLColorTableNodeRed")
        black_logic = slicer.app.layoutManager().sliceWidget("Slice4").sliceLogic()
        black_logic.GetSliceCompositeNode().SetBackgroundVolumeID(dnaNode.GetID())

        slicer.util.resetSliceViews()

        return nCells


    def analysisRun(self):
        """
        Create histogram of intensity values of the selected image
        """

        # Delete any existing plots
        existingPlots = slicer.util.getNodesByClass("vtkMRMLPlotChartNode")
        existingSeriesNodes = slicer.util.getNodesByClass("vtkMRMLPlotSeriesNode")
        existingTables = slicer.util.getNodesByClass("vtkMRMLTableNode")

        for plot in existingPlots:
            slicer.mrmlScene.RemoveNode(plot)
        for seriesNode in existingSeriesNodes:
            slicer.mrmlScene.RemoveNode(seriesNode)
        for table in existingTables:
            slicer.mrmlScene.RemoveNode(table)

        # Get list of all channels
        allChannels = slicer.util.getNodesByClass("vtkMRMLScalarVolumeNode")

        # Create dictionary of each channel with its respective ROI
        shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
        parentDict = {}
        for channel in allChannels:
            itemId = shNode.GetItemByDataNode(channel)  # Channel
            parent = shNode.GetItemParent(itemId)  # ROI
            roiName = shNode.GetItemName(parent)
            channelName = shNode.GetItemName(itemId)
            if re.findall(r"_[0-9]\b", channelName) != []:
                channelName = channelName[:-2]
            # Check if the specific channel was selected
            if roiName == "Scene":
                roiName = "ROI"
            if roiName in selectedRoi and channelName in selectedChannel:
                parentDict[itemId] = roiName


        # Set "global" variables in order to display later
        tableNode = None
        plotChartNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotChartNode",
                                                           "Histogram of Channel Mean Intensities")
        plotChartNode.SetTitle("Histogram of Channel Mean Intensities")
        plotChartNode.SetXAxisTitle("Mean Intensity of Channel in Cell (Bins)")
        plotChartNode.SetYAxisTitle("Count")
        displayList = []

        # Set a count to determine what colour the plot series will be
        count = 0

        # For each channel, run this loop to create histogram; parentDict length should be number of channels to be plotted
        for itemId in parentDict:

            count +=1
            # Get array of channel
            roiName = parentDict[itemId]
            channelName = shNode.GetItemName(itemId)
            channelNode = slicer.util.getNode(channelName)
            channelArray = slicer.util.arrayFromVolume(channelNode)

            if count <= 3:
                displayList.append(channelNode)

            # Get array for cell mask
            cellMask = globalCellMask[roiName]
            cellMaskArray = slicer.util.arrayFromVolume(cellMask)

            # Get counts of pixels in each cell
            cell, counts = np.unique(cellMaskArray, return_counts=True)
            cellPixelCounts = dict(zip(cell, counts))

            channelMeanIntens = []

            for cell in cellPixelCounts.keys():
                if cell != 0:
                    blank, i, j = np.nonzero(cellMaskArray == cell)
                    # if blank.shape[0] != 0 and i.shape[0] == 0 and j.shape[0] == 0:
                    cellPixels = channelArray[:, i, j]
                    sumIntens = np.sum(cellPixels)
                    nonZeroes = np.where(cellPixels != 0)
                    numNonZeroes = nonZeroes[1].shape[0]
                    if numNonZeroes == 0:
                        avg = 0
                    else:
                        avg = float(sumIntens) / float(numNonZeroes)
                    channelMeanIntens.append(avg)

            histogram = np.histogram(channelMeanIntens, bins=20)

            # Save results to a new table node
            tableNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTableNode", channelName + "_" + roiName + 'data')
            slicer.util.updateTableFromArray(tableNode, histogram)
            tableNode.GetTable().GetColumn(0).SetName("Count")
            tableNode.GetTable().GetColumn(1).SetName("Intensity")

            # Create plot
            plotSeriesNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotSeriesNode",
                                                                channelName + "_" + roiName + " series")
            plotSeriesNode.SetAndObserveTableNodeID(tableNode.GetID())
            plotSeriesNode.SetXColumnName("Intensity")
            plotSeriesNode.SetYColumnName("Count")
            plotSeriesNode.SetPlotType(plotSeriesNode.PlotTypeBar)
            if count % 3 == 1:
                plotSeriesNode.SetColor(1.0, 0, 0)
            elif count % 3 == 2:
                plotSeriesNode.SetColor(0, 1.0, 0)
            else:
                plotSeriesNode.SetColor(0, 0, 1.0)

            # Create chart and add plot
            plotChartNode = slicer.util.getNode("Histogram of Channel Mean Intensities")
            plotChartNode.AddAndObservePlotSeriesNodeID(plotSeriesNode.GetID())

        # Show plot in layout
        slicer.modules.plots.logic().ShowChartInLayout(plotChartNode)
        slicer.app.layoutManager().setLayout(
            slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpPlotView)  # or SlicerLayoutThreeOverThreePlotView
        slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID(tableNode.GetID())
        slicer.app.applicationLogic().PropagateTableSelection()

        # Set red slice to show the heatmap
        redDisplayNode = displayList[0].GetScalarVolumeDisplayNode()
        redDisplayNode.SetAndObserveColorNodeID("vtkMRMLColorTableNodeRed")
        red_logic = slicer.app.layoutManager().sliceWidget("Red").sliceLogic()
        red_logic.GetSliceCompositeNode().SetBackgroundVolumeID(displayList[0].GetID())

        # Set green slice to show cell mask
        green_widget = slicer.app.layoutManager().sliceWidget("Green")
        green_widget.setSliceOrientation("Axial")
        if len(displayList) > 1:
            greenDisplayNode = displayList[1].GetScalarVolumeDisplayNode()
            greenDisplayNode.SetAndObserveColorNodeID("vtkMRMLColorTableNodeGreen")
            green_logic = green_widget.sliceLogic()
            green_logic.GetSliceCompositeNode().SetBackgroundVolumeID(displayList[1].GetID())
        else:
            green_logic = green_widget.sliceLogic()
            green_logic.GetSliceCompositeNode().SetBackgroundVolumeID(displayList[0].GetID())

        # Set yellow slice to show cloned, thresholded channel
        yellow_widget = slicer.app.layoutManager().sliceWidget("Yellow")
        yellow_widget.setSliceOrientation("Axial")
        if len(displayList) > 2:
            yellowDisplayNode = displayList[2].GetScalarVolumeDisplayNode()
            yellowDisplayNode.SetAndObserveColorNodeID("vtkMRMLColorTableNodeBlue")
            yellow_logic = yellow_widget.sliceLogic()
            yellow_logic.GetSliceCompositeNode().SetBackgroundVolumeID(displayList[2].GetID())
        else:
            yellow_logic = yellow_widget.sliceLogic()
            yellow_logic.GetSliceCompositeNode().SetBackgroundVolumeID(displayList[0].GetID())

        slicer.util.resetSliceViews()

    def scatterPlotRun(self, checkboxState):

        """
        Create scatter plot of channelOne x channelTwo, where data points are the cells, values are the mean intensity
        of each channel within that cell
        """

        # Delete any existing plots
        existingPlots = slicer.util.getNodesByClass("vtkMRMLPlotChartNode")
        existingSeriesNodes = slicer.util.getNodesByClass("vtkMRMLPlotSeriesNode")
        existingTables = slicer.util.getNodesByClass("vtkMRMLTableNode")

        for plot in existingPlots:
            slicer.mrmlScene.RemoveNode(plot)
        for seriesNode in existingSeriesNodes:
            slicer.mrmlScene.RemoveNode(seriesNode)
        for table in existingTables:
            slicer.mrmlScene.RemoveNode(table)

        # Get list of all channels
        allChannels = slicer.util.getNodesByClass("vtkMRMLScalarVolumeNode")

        # Create dictionary of each channel with its respective ROI
        shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
        parentDict = {}
        for channel in allChannels:
            itemId = shNode.GetItemByDataNode(channel)  # Channel
            parent = shNode.GetItemParent(itemId)  # ROI
            roiName = shNode.GetItemName(parent)
            channelName = shNode.GetItemName(itemId)
            if re.findall(r"_[0-9]\b", channelName) != []:
                channelName = channelName[:-2]
            # Check if the specific channel was selected
            if roiName == "Scene":
                roiName = "ROI"
            if roiName in selectedRoi and channelName in selectedChannel:
                parentDict[itemId] = roiName
            if len(parentDict) == 2:
                break

        channels = list(parentDict.keys())
        # Get ROI name or Selected Cells mask
        if checkboxState == False:
            roiName = parentDict[channels[0]]
        else:
            roiName = "Selected Cells"
        # Get array of channel

        channelOneName = shNode.GetItemName(channels[0])
        channelOneNode = slicer.util.getNode(channelOneName)
        channelOneArray = slicer.util.arrayFromVolume(channelOneNode)
        channelTwoName = shNode.GetItemName(channels[1])
        channelTwoNode = slicer.util.getNode(channelTwoName)
        channelTwoArray = slicer.util.arrayFromVolume(channelTwoNode)

        # Get arrays for cell mask and channels
        cellMask = globalCellMask[roiName]
        cellMaskArray = slicer.util.arrayFromVolume(cellMask)

        # Get counts of pixels in each cell
        cell, counts = np.unique(cellMaskArray, return_counts=True)
        cellPixelCounts = dict(zip(cell, counts))

        # Create list of mean intensities for all cells for each channel
        channelOneMeanIntens = []
        channelTwoMeanIntens = []
        cellLabels = []

        for cell in range(cellMaskArray.max() + 1):
            if cell != 0:
                if cell in cellPixelCounts.keys():
                    # Channel one
                    blank, i, j = np.nonzero(cellMaskArray == cell)
                    cellPixels = channelOneArray[:, i, j]
                    sumIntens = np.sum(cellPixels)
                    nonZeroes = np.where(cellPixels != 0)
                    numNonZeroes = nonZeroes[1].shape[0]
                    if numNonZeroes == 0:
                        avg = 0
                    else:
                        avg = float(sumIntens) / float(numNonZeroes)
                    channelOneMeanIntens.append(avg)
                    # Channel two
                    cellPixelsTwo = channelTwoArray[:, i, j]
                    sumIntensTwo = np.sum(cellPixelsTwo)
                    nonZeroesTwo = np.where(cellPixelsTwo != 0)
                    numNonZeroesTwo = nonZeroesTwo[1].shape[0]
                    if numNonZeroesTwo == 0:
                        avgTwo = 0
                    else:
                        avgTwo = float(sumIntensTwo) / float(numNonZeroesTwo)
                    channelTwoMeanIntens.append(avgTwo)
                    # Cell label
                    cellLabels.append(cell)

        # Set x and y values
        x = channelOneMeanIntens
        y = channelTwoMeanIntens
        z = cellLabels
        nPoints = len(x)

        # Create table with x and y columns
        tableNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTableNode", roiName + ": " + channelOneName + " x " + channelTwoName + " data")
        table = tableNode.GetTable()

        arrX = vtk.vtkFloatArray()
        arrX.SetName(channelOneName)
        table.AddColumn(arrX)

        arrY = vtk.vtkFloatArray()
        arrY.SetName(channelTwoName)
        table.AddColumn(arrY)

        arrZ = vtk.vtkIntArray()
        arrZ.SetName("Cell Label")
        table.AddColumn(arrZ)

        # Fill in table with values
        table.SetNumberOfRows(nPoints)
        for i in range(nPoints):
            table.SetValue(i, 0, x[i])
            table.SetValue(i, 1, y[i])
            table.SetValue(i, 2, z[i])

        # Create plot series nodes
        plotSeriesNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotSeriesNode", roiName + ": Cells")
        plotSeriesNode.SetAndObserveTableNodeID(tableNode.GetID())
        plotSeriesNode.SetXColumnName(channelOneName)
        plotSeriesNode.SetYColumnName(channelTwoName)
        plotSeriesNode.SetPlotType(slicer.vtkMRMLPlotSeriesNode.PlotTypeScatter)
        plotSeriesNode.SetLineStyle(slicer.vtkMRMLPlotSeriesNode.LineStyleNone)
        plotSeriesNode.SetMarkerStyle(slicer.vtkMRMLPlotSeriesNode.MarkerStyleCircle)
        plotSeriesNode.SetColor(0.46, 0.67, 0.96)

        # Create plot chart node
        plotChartNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotChartNode", roiName + ": " + channelOneName + " x " + channelTwoName)
        plotChartNode.AddAndObservePlotSeriesNodeID(plotSeriesNode.GetID())
        plotChartNode.SetTitle(roiName + ": " + channelOneName + " x " + channelTwoName)
        plotChartNode.SetXAxisTitle(channelOneName)
        plotChartNode.SetYAxisTitle(channelTwoName)

        # Show plot in layout
        slicer.modules.plots.logic().ShowChartInLayout(plotChartNode)
        slicer.app.layoutManager().setLayout(
            slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpPlotView)

        # Set red slice to show the heatmap
        red_logic = slicer.app.layoutManager().sliceWidget("Red").sliceLogic()
        red_logic.GetSliceCompositeNode().SetBackgroundVolumeID(cellMask.GetID())

        # Set yellow slice to show cloned, thresholded channel
        yellow_widget = slicer.app.layoutManager().sliceWidget("Yellow")
        yellow_widget.setSliceOrientation("Axial")
        yellowDisplayNode = channelOneNode.GetScalarVolumeDisplayNode()
        yellowDisplayNode.SetAndObserveColorNodeID("vtkMRMLColorTableNodeRed")
        yellow_logic = yellow_widget.sliceLogic()
        yellow_logic.GetSliceCompositeNode().SetBackgroundVolumeID(channelOneNode.GetID())

        # Set green slice to show cell mask
        green_widget = slicer.app.layoutManager().sliceWidget("Green")
        green_widget.setSliceOrientation("Axial")
        greenDisplayNode = channelTwoNode.GetScalarVolumeDisplayNode()
        greenDisplayNode.SetAndObserveColorNodeID("vtkMRMLColorTableNodeRed")
        green_logic = green_widget.sliceLogic()
        green_logic.GetSliceCompositeNode().SetBackgroundVolumeID(channelTwoNode.GetID())

        slicer.util.resetSliceViews()

        # # Scatter plot gating signal
        # layoutManager = slicer.app.layoutManager()
        # plotWidget = layoutManager.plotWidget(0)
        # plotView = plotWidget.plotView()
        # plotView.connect("dataSelected(vtkStringArray*, vtkCollection*)", self.onDataSelected)

        global scatterPlotRoi
        scatterPlotRoi = roiName


    def saveTableData(self):
        # Get table node
        tables = slicer.util.getNodesByClass("vtkMRMLTableNode")
        savedPaths = []
        # Save table to .csv file
        for table in tables:
            fileName = table.GetName() + ".csv"
            pathName = os.getcwd() + '\\' + fileName
            slicer.util.saveNode(table, pathName)
            savedPaths.append(pathName)
        import subprocess
        subprocess.Popen(r'explorer /select,' + savedPaths[0])

    def heatmapChannelRun(self):

        """
        Create heatmap of the selected channel overlaid onto the cell mask
        """

        # Delete any existing heatmap images
        existingHeatmaps = slicer.util.getNodesByClass("vtkMRMLScalarVolumeNode")

        for img in existingHeatmaps:
            if "Heatmap" in img.GetName():
                slicer.mrmlScene.RemoveNode(img)

        # Get list of all channels
        allChannels = slicer.util.getNodesByClass("vtkMRMLScalarVolumeNode")

        # Create dictionary of each channel with its respective ROI
        shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
        parentDict = {}
        for channel in allChannels:
            itemId = shNode.GetItemByDataNode(channel)  # Channel
            parent = shNode.GetItemParent(itemId)  # ROI
            roiName = shNode.GetItemName(parent)
            channelName = shNode.GetItemName(itemId)
            if re.findall(r"_[0-9]\b", channelName) != []:
                channelName = channelName[:-2]
            # Check if the specific channel was selected
            if roiName == "Scene":
                roiName = "ROI"
            if roiName in selectedRoi and channelName in selectedChannel:
                parentDict[itemId] = roiName
            if len(parentDict) == 1:
                break

        channels = list(parentDict.keys())
        # Get array of channel
        roiName = parentDict[channels[0]]
        channelName = shNode.GetItemName(channels[0])
        channelNode = slicer.util.getNode(channelName)
        channelArray = slicer.util.arrayFromVolume(channelNode)

        # Get arrays for cell mask and channels
        cellMask = globalCellMask[roiName]
        cellMaskArray = slicer.util.arrayFromVolume(cellMask)

        # Get counts of pixels in each cell
        cell, counts = np.unique(cellMaskArray, return_counts=True)
        cellPixelCounts = dict(zip(cell, counts))

        # Create dictionary of heatmap percentages for all cells
        hmapPercentages = {0: 0}

        for cell in range(cellMaskArray.max() + 1):
            if cell != 0:
                if cell in cellPixelCounts.keys():
                    # blank, i, j = np.nonzero(cellMaskArray == cell)
                    # cellPixels = channelArray[:, i, j]
                    # sumIntens = np.sum(cellPixels)
                    # nonZeroes = np.where(cellPixels != 0)
                    # numNonZeroes = nonZeroes[1].shape[0]
                    # avg = float(sumIntens) / float(numNonZeroes)
                    # hmapPercentages[cell] = avg

                    blank, i, j = np.nonzero(cellMaskArray == cell)
                    cellPixels = channelArray[:, i, j]
                    nActivePixels = np.count_nonzero(cellPixels)
                    perc = float(nActivePixels) / float(cellPixelCounts[cell])
                    hmapPercentages[cell] = perc

        # Map percentages to the cell mask array
        cellMaskHeatmap = np.copy(cellMaskArray)
        for cell in range(cellMaskHeatmap.max() + 1):
            if cell != 0:
                if cell in cellPixelCounts.keys():
                    cellMaskHeatmap = np.where(cellMaskHeatmap == cell, hmapPercentages[cell], cellMaskHeatmap)

        # Display image of cellMaskHeatmap
        # Create new volume "Heatmap on Channel"
        name = channelName
        if ".ome" in name:
            name = name.replace(".ome", "")

        volumeNode = slicer.modules.volumes.logic().CloneVolume(cellMask, "Heatmap on Channel " + name)
        slicer.util.updateVolumeFromArray(volumeNode, cellMaskHeatmap)

        # Change colormap of volume
        inferno = slicer.util.getFirstNodeByName("Inferno")
        displayNode = volumeNode.GetScalarVolumeDisplayNode()
        displayNode.SetAndObserveColorNodeID(inferno.GetID())

        # Fix window/level
        # volumeNode.GetDisplayNode().AutoWindowLevelOff()
        # volumeNode.GetDisplayNode().SetWindowLevel((cellMaskHeatmap.shape[1] // 4), 127)

        slicer.util.setSliceViewerLayers(background=volumeNode, foreground=None)

        # Create histogram plot of the intensity values

        # Delete any existing plots
        existingPlots = slicer.util.getNodesByClass("vtkMRMLPlotChartNode")
        existingSeriesNodes = slicer.util.getNodesByClass("vtkMRMLPlotSeriesNode")
        existingTables = slicer.util.getNodesByClass("vtkMRMLTableNode")

        for plot in existingPlots:
            slicer.mrmlScene.RemoveNode(plot)
        for seriesNode in existingSeriesNodes:
            slicer.mrmlScene.RemoveNode(seriesNode)
        for table in existingTables:
            slicer.mrmlScene.RemoveNode(table)

        # Compute histogram values
        histValues = np.array(list(hmapPercentages.values()))
        histogram = np.histogram(histValues[histValues!=0], bins=20)

        # Save results to a new table node
        tableNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTableNode", volumeNode.GetName() + ' data')
        slicer.util.updateTableFromArray(tableNode, histogram)
        tableNode.GetTable().GetColumn(0).SetName("Count")
        tableNode.GetTable().GetColumn(1).SetName("Marker:Cell Ratio")

        # Create plot
        plotSeriesNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotSeriesNode",
                                                            volumeNode.GetName() + " plot")
        plotSeriesNode.SetAndObserveTableNodeID(tableNode.GetID())
        plotSeriesNode.SetXColumnName("Marker:Cell Ratio")
        plotSeriesNode.SetYColumnName("Count")
        plotSeriesNode.SetPlotType(plotSeriesNode.PlotTypeScatterBar)
        plotSeriesNode.SetColor(0.46, 0.67, 0.96)

        # Create chart and add plot
        plotChartNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotChartNode",
                                                           volumeNode.GetName() + 'histogram')
        plotChartNode.AddAndObservePlotSeriesNodeID(plotSeriesNode.GetID())
        plotChartNode.SetTitle("Histogram of Marker:Cell Ratio")
        plotChartNode.SetXAxisTitle("Marker:Cell Ratio")
        plotChartNode.SetYAxisTitle("Count")
        # plotChartNode.YAxisRangeAutoOff()
        # plotChartNode.SetYAxisRange(0, 150000)
        # plotChartNode.XAxisRangeAutoOff()
        # plotChartNode.SetXAxisRange(0, 1)

        # Show plot in layout
        slicer.modules.plots.logic().ShowChartInLayout(plotChartNode)
        slicer.app.layoutManager().setLayout(
            slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpPlotView)

        # Set red slice to show the heatmap
        red_logic = slicer.app.layoutManager().sliceWidget("Red").sliceLogic()
        red_logic.GetSliceCompositeNode().SetBackgroundVolumeID(volumeNode.GetID())

        # Set yellow slice to show cloned, thresholded channel
        yellow_widget = slicer.app.layoutManager().sliceWidget("Yellow")
        yellow_widget.setSliceOrientation("Axial")
        yellowDisplayNode = channelNode.GetScalarVolumeDisplayNode()
        yellowDisplayNode.SetAndObserveColorNodeID("vtkMRMLColorTableNodeRed")
        yellow_logic = yellow_widget.sliceLogic()
        yellow_logic.GetSliceCompositeNode().SetBackgroundVolumeID(cellMask.GetID())

        # Set green slice to show cell mask
        green_widget = slicer.app.layoutManager().sliceWidget("Green")
        green_widget.setSliceOrientation("Axial")
        green_logic = green_widget.sliceLogic()
        green_logic.GetSliceCompositeNode().SetBackgroundVolumeID(channelNode.GetID())

        slicer.util.resetSliceViews()

    def sliceThreshold(self, channel, thresh, slice, rgb):

        """
        Peforms thresholding of "channel" given a threshold value "thresh" and slice window "slice" to be displayed in
        """

        # Delete any existing thresholded images
        existingThresholds = slicer.util.getNodesByClass("vtkMRMLScalarVolumeNode")

        array = slicer.util.arrayFromVolume(channel)

        arraySize = array.shape
        cloneArray = np.stack((array,) * 3, axis=-1)
        if rgb == "Red":
            cloneArray[:, :, :, 1] = 0
            cloneArray[:, :, :, 2] = 0
        elif rgb == "Green":
            cloneArray[:,:,:,0] = 0
            cloneArray[:,:,:,2] = 0
        else:
            cloneArray[:,:,:,0] = 0
            cloneArray[:,:,:,1] = 0

        threshVal = 255 - thresh
        cloneArray[cloneArray > threshVal] = 255

        # Create new vector volume in order to have 3-channel image
        imageSize = [arraySize[2], arraySize[1], 1]
        voxelType = vtk.VTK_UNSIGNED_CHAR
        imageOrigin = [0.0, 0.0, 0.0]
        imageSpacing = [1.0, 1.0, 1.0]
        imageDirections = [[-1, 0, 0], [0, -1, 0], [0, 0, 1]]
        fillVoxelValue = 0

        # Create an empty image volume, filled with fillVoxelValue
        imageData = vtk.vtkImageData()
        imageData.SetDimensions(imageSize)
        imageData.AllocateScalars(voxelType, 3)
        imageData.GetPointData().GetScalars().Fill(fillVoxelValue)

        # Create volume node
        # Needs to be a vector volume in order to show in colour
        name = channel.GetName()
        if ".ome" in name:
            name = name.replace(".ome", "")
        volumeScatNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLVectorVolumeNode", "Thresholded " + slice + " " + name)
        volumeScatNode.SetOrigin(imageOrigin)
        volumeScatNode.SetSpacing(imageSpacing)
        volumeScatNode.SetIJKToRASDirections(imageDirections)
        volumeScatNode.SetAndObserveImageData(imageData)
        volumeScatNode.CreateDefaultDisplayNodes()
        volumeScatNode.CreateDefaultStorageNode()

        voxels = slicer.util.arrayFromVolume(volumeScatNode)
        voxels[:] = cloneArray

        volumeScatNode.Modified()

        volumeScatNode.GetDisplayNode().AutoWindowLevelOff()
        volumeScatNode.GetDisplayNode().SetWindowLevel((arraySize[1] // 2), 127)

        # Set slice to show cloned, thresholded channel
        widget = slicer.app.layoutManager().sliceWidget(slice)
        widget.setSliceOrientation("Axial")
        logic = widget.sliceLogic()
        logic.GetSliceCompositeNode().SetBackgroundVolumeID(volumeScatNode.GetID())

        # Delete previous thresholded images
        for img in existingThresholds:
            if "Thresholded " + slice in img.GetName():
                slicer.mrmlScene.RemoveNode(img)

        slicer.util.resetSliceViews()

    def heatmapRun(self):

        """
        Create heatmap showing mean intensities of channels across all ROI's
        """

        # Delete any existing heatmap images
        existingHeatmaps = slicer.util.getNodesByClass("vtkMRMLScalarVolumeNode")

        for img in existingHeatmaps:
            if "Heatmap" in img.GetName():
                slicer.mrmlScene.RemoveNode(img)

        channelRows = []
        roiColumns = []

        # Get list of all channels
        allChannels = slicer.util.getNodesByClass("vtkMRMLScalarVolumeNode")

        # Create dictionary of each channel with its respective ROI
        shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
        parentDict = {}
        for channel in allChannels:
            itemId = shNode.GetItemByDataNode(channel)   # Channel
            parent = shNode.GetItemParent(itemId)    # ROI
            roiName = shNode.GetItemName(parent)
            channelName = shNode.GetItemName(itemId)
            if re.findall(r"_[0-9]\b", channelName) != []:
                channelName = channelName[:-2]
            if roiName == "Scene":
                roiName = "ROI"
            # Check if the specific channel was selected
            if roiName in selectedRoi and channelName in selectedChannel:
                parentDict[itemId] = roiName
                if channelName not in channelRows:
                    channelRows.append(channelName)
                if roiName not in roiColumns:
                    roiColumns.append(roiName)
        # Create empty matrix of mean intensities
        meanIntensities = np.full((len(roiColumns), len(channelRows)), 0.00)

        # Fill meanIntensities matrix with proper values
        for i in parentDict:
            # Get array of channel
            channelName = shNode.GetItemName(i)
            channelNode = slicer.util.getNode(channelName)
            channelArray = slicer.util.arrayFromVolume(channelNode)
            # Get mean intensity of channel
            sumIntens = np.sum(channelArray)
            nonZeroes = np.where(channelArray != 0)
            numNonZeroes = nonZeroes[1].shape[0]
            meanIntens = float(sumIntens) / float(numNonZeroes)
            # Update meanIntensities matrix with this value
            if re.findall(r"_[0-9]\b", channelName) != []:
                channelName = channelName[:-2]
            rowPos = channelRows.index(channelName)
            columnPos = roiColumns.index(parentDict[i])
            meanIntensities[columnPos, rowPos] = round(meanIntens, 2)
        # Run helper function
        HypModuleLogic().heatmapRunHelper(channelRows, roiColumns, meanIntensities)
        return True

    def heatmapRunHelper(self, channelRows, roiColumns, meanIntensities):

        # Install necessary libraries
        try:
            import matplotlib
        except ModuleNotFoundError:
            import pip
            pip_install("matplotlib")
            import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from pylab import savefig

        # Create heatmap
        # plt.rcParams.update({'font.size': 6})
        fig, ax = plt.subplots(figsize=(20,10))

        ax.set_xticks(np.arange(len(channelRows)))
        ax.set_yticks(np.arange(len(roiColumns)))

        ax.set_xticklabels(channelRows)
        ax.set_yticklabels(roiColumns)

        plt.setp(ax.get_xticklabels(), rotation = 45, ha = "right",
                 rotation_mode = "anchor")

        # Loop through data and create text annotations
        if len(channelRows) < 30:
            for i in range(len(roiColumns)):
                for j in range(len(channelRows)):
                    text = ax.text(j, i, meanIntensities[i,j],
                                   ha = "center", va = "center", color = "w")

        ax.set_title("Heatmap of Mean Intensities")

        # Add colour bar to heatmap
        im = ax.imshow(meanIntensities)
        cbar = ax.figure.colorbar(im)
        cbar.ax.set_ylabel("Mean Intensity", rotation = -90, va = "bottom")

        # Display heatmap
        savefig("heatmap.jpg")
        heatmapImg = sitk.ReadImage("heatmap.jpg")
        heatmapArray = sitk.GetArrayFromImage(heatmapImg)
        arraySize = heatmapArray.shape
        plt.close()
        # Create new volume "Heatmap"
        imageSize = [arraySize[1], arraySize[0], 1]
        voxelType = vtk.VTK_UNSIGNED_CHAR
        imageOrigin = [0.0, 0.0, 0.0]
        imageSpacing = [1.0, 1.0, 1.0]
        imageDirections = [[-1, 0, 0], [0, -1, 0], [0, 0, 1]]
        fillVoxelValue = 0

        # Create an empty image volume, filled with fillVoxelValue
        imageData = vtk.vtkImageData()
        imageData.SetDimensions(imageSize)
        imageData.AllocateScalars(voxelType, 3)
        imageData.GetPointData().GetScalars().Fill(fillVoxelValue)

        # Create volume node
        # Needs to be a vector volume in order to show in colour
        volumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLVectorVolumeNode", "Heatmap")
        volumeNode.SetOrigin(imageOrigin)
        volumeNode.SetSpacing(imageSpacing)
        volumeNode.SetIJKToRASDirections(imageDirections)
        volumeNode.SetAndObserveImageData(imageData)
        volumeNode.CreateDefaultDisplayNodes()
        volumeNode.CreateDefaultStorageNode()

        voxels = slicer.util.arrayFromVolume(volumeNode)
        voxels[:] = heatmapArray

        volumeNode.Modified()
        volumeNode.GetDisplayNode().AutoWindowLevelOff()
        volumeNode.GetDisplayNode().SetWindowLevel((arraySize[1]//8), 127)

        slicer.util.setSliceViewerLayers(background=volumeNode, foreground=None)

        # Set slice view to display Red window only
        lm = slicer.app.layoutManager()
        lm.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpRedSliceView)

        # Reset field of view to show entire image
        slicer.util.resetSliceViews()

        # pm = qt.QPixmap("heatmap.png")
        # imgWidget = qt.QLabel()
        # imgWidget.setPixmap(pm)
        # imgWidget.setScaledContents(True)
        # imgWidget.show()
        # return True


    def saveHeatmapChannelImg(self):

        fileName = "heatmap on channel.png"
        viewNodeID = 'vtkMRMLSliceNodeRed'
        import ScreenCapture
        cap = ScreenCapture.ScreenCaptureLogic()
        view = cap.viewFromNode(slicer.mrmlScene.GetNodeByID(viewNodeID))
        pathName = os.getcwd() + '\\' + fileName
        cap.captureImageFromView(view, pathName)
        import subprocess
        subprocess.Popen(r'explorer /select,' + pathName)


# def analysisRunAlt(self, imageHistogramSelect):
#     import matplotlib
#     import matplotlib.pyplot as plt
#     matplotlib.use("Agg")
#     array = slicer.util.arrayFromVolume(imageHistogramSelect)
#     nbins = 50
#     histogram = plt.hist(array, nbins)
#     plt.plot(histogram)
#     plt.grid(True)
#     plt.title("Histogram")
#     plt.ylabel("Frequency")
#     plt.savefig("histogram.png")
#     pm = qt.QPixmap("histogram.png")
#     imageWidget = qt.QLabel()
#     imageWidget.setPixmap(pm)
#     imageWidget.setScaledContents(True)
#     imageWidget.show()


class HypModuleTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
        """
        slicer.mrmlScene.Clear(0)

    def runTest(self):
        """Run as few or as many tests as needed here.
        """
        self.setUp()
        self.test_HypModule1()

    def test_HypModule1(self):
        """ Ideally you should have several levels of tests.  At the lowest level
        tests should exercise the functionality of the logic with different inputs
        (both valid and invalid).  At higher levels your tests should emulate the
        way the user would interact with your code and confirm that it still works
        the way you intended.
        One of the most important features of the tests is that it should alert other
        developers when their changes will have an impact on the behavior of your
        module.  For example, if a developer removes a feature that you depend on,
        your test should break so they know that the feature is needed.
        """

        self.delayDisplay("Starting the test")
        #
        # first, get some data
        #
        import SampleData
        SampleData.downloadFromURL(
            nodeNames='FA',
            fileNames='FA.nrrd',
            uris='http://slicer.kitware.com/midas3/download?items=5767')
        self.delayDisplay('Finished with download and loading')

        volumeNode = slicer.util.getNode(pattern="FA")
        logic = HypModuleLogic()
        self.assertIsNotNone(logic.hasImageData(volumeNode))
        self.delayDisplay('Test passed!')

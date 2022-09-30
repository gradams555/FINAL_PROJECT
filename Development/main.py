# George Adams
# September 30, 2022
# Main code for processing market value data

import os, sys
import qgis
import qgis.core

from PyQt5.QtWidgets import QApplication, QMainWindow, QStyle, QFileDialog, QDialog, QMessageBox, QSizePolicy
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QDoubleValidator, QIntValidator
from PyQt5.QtCore import QVariant
from PyQt5.Qt import Qt

import overlay
import utilities
import main_gui


# ==========================================
# create app and main window
# =========================================



qgis_prefix = os.getenv("QGIS_PREFIX_PATH")
qgis.core.QgsApplication.setPrefixPath(qgis_prefix, True)
qgs = qgis.core.QgsApplication([], False)
qgs.initQgis()

app = QApplication(sys.argv)
# set up main window
mainWindow = QMainWindow()
ui = main_gui.Ui_MainWindow()
ui.setupUi(mainWindow)

layer_base = None
layer_comparison = None
layer_overlay = None
layer_result_file = None
layer_overlay_result_file = None

# =======================================
# GUI event handler and related functions
# =======================================

def selectBaseShapefile():
    global layer_base
    """open file dialog to select exising shapefile and if accepted, update GUI accordingly"""
    select_file, _ = QFileDialog.getOpenFileName(mainWindow, "Select shapefile", "", "Shapefile (*.shp)")
    if select_file:
        ui.baseLE.setText(select_file)
        layer_base = qgis.core.QgsVectorLayer(select_file)
        updateBaseCB()
        updateBaseParamCB()

def selectComparisonShapefile():
    global layer_comparison
    """open file dialog to select exising shapefile and if accepted, update GUI accordingly"""
    select_file, _ = QFileDialog.getOpenFileName(mainWindow, "Select shapefile", "", "Shapefile (*.shp)")
    if select_file:
        ui.comparisonLE.setText(select_file)
        layer_comparison = qgis.core.QgsVectorLayer(select_file)
        updateComparisonCB()
        updateComparisonParamCB()

def selectOverlayShapefile():
    global layer_overlay
    """open file dialog to select exising shapefile and if accepted, update GUI accordingly"""
    select_file, _ = QFileDialog.getOpenFileName(mainWindow, "Select shapefile", "", "Shapefile (*.shp)")
    if select_file:
        ui.overlayLE.setText(select_file)
        layer_overlay = qgis.core.QgsVectorLayer(select_file)
        #==>updateOverlayCB()

def selectNewResultGPKGfile():
    global layer_result_file
    """open file dialog to creaete new shapefile and if accepted, update GUI accordingly"""
    new_file, _ = QFileDialog.getSaveFileName(mainWindow,"Save new GeoPackage as", ""," (*.gpkg)")
    if new_file:
        ui.resultLE.setText(new_file)
        layer_result_file = new_file


def selectNewOverlayResultGPKGfile():
    global layer_overlay_result_file
    """open file dialog to creaete new shapefile and if accepted, update GUI accordingly"""
    new_file, _ = QFileDialog.getSaveFileName(mainWindow,"Save new GeoPackage as", ""," (*.gpkg)")
    if new_file:
        ui.resultOverlayLE.setText(new_file)
        layer_overlay_result_file = new_file

def resultToggle():
    if ui.resultCkB.isChecked():
        ui.resultLE.setEnabled(True)
        ui.resultTB.setEnabled(True)
    else:
        ui.resultLE.setEnabled(False)
        ui.resultTB.setEnabled(False)

def resultOverlayToggle():
    if ui.resultOverlayCkB.isChecked():
        ui.resultOverlayLE.setEnabled(True)
        ui.resultOverlayTB.setEnabled(True)
    else:
        ui.resultOverlayLE.setEnabled(False)
        ui.resultOverlayTB.setEnabled(False)

def updateBaseParamCB():
    global layer_base
    # Update base combobox after base shapefile is selected
    ui.baseParamCB.clear()

    try:
        ui.baseParamCB.addItems(utilities.getNumericFields(layer_base))
    except Exception as e:
        QMessageBox.information(mainWindow, 'Operation failed - Update Base Parameter ComboBox',
                                'Obtaining parameter list failed with ' + str(e.__class__) + ': ' + str(e), QMessageBox.Ok)
        ui.statusbar.clearMessage()

def updateBaseCB():
    global layer_base
    # Update base combobox after base shapefile is selected
    ui.baseCB.clear()

    try:
        ui.baseCB.addItems(utilities.getAllFields(layer_base))
    except Exception as e:
        QMessageBox.information(mainWindow, 'Operation failed - Update Base Unique ID ComboBox',
                                'Obtaining field list failed with ' + str(e.__class__) + ': ' + str(e), QMessageBox.Ok)
        ui.statusbar.clearMessage()


def updateComparisonParamCB():
    global layer_comparison
    # Update base combobox after base shapefile is selected
    ui.comparisonParamCB.clear()

    try:
        ui.comparisonParamCB.addItems(utilities.getNumericFields(layer_base))
    except Exception as e:
        QMessageBox.information(mainWindow, 'Operation failed - Update Comparison Parameter ComboBox',
                                'Obtaining parameter list failed with ' + str(e.__class__) + ': ' + str(e), QMessageBox.Ok)
        ui.statusbar.clearMessage()

def updateComparisonCB():
    global layer_comparison
    # Update comparison combobox after base shapefile is selected
    ui.comparisonCB.clear()

    try:
        ui.comparisonCB.addItems(utilities.getAllFields(layer_base))
    except Exception as e:
        QMessageBox.information(mainWindow, 'Operation failed - Update Comparison Unique ID ComboBox',
                                'Obtaining field list failed with ' + str(e.__class__) + ': ' + str(e), QMessageBox.Ok)
        ui.statusbar.clearMessage()



def processData():
    ui.statusbar.showMessage('Processing has started... please wait!')
    dict_base = {}
    dict_comparison = {}
    dict_overlay = {}
    global layer_base
    global layer_comparison
    global layer_overlay
    global layer_result_file
    global layer_overlay_result_file

    if layer_base is None:
        ui.statusbar.showMessage('Exiting... select the base layer')
        return
    if layer_comparison is None:
        ui.statusbar.showMessage('Exiting... select the comparison layer')
        return
    if layer_overlay is None:
        ui.statusbar.showMessage('Exiting... select the overlay layer')
        return
    if ui.resultCkB.isChecked():
        if layer_result_file is None:
            ui.statusbar.showMessage('Exiting... select the layer result file')
            return
    if ui.resultOverlayCkB.isChecked():
        if layer_overlay_result_file is None:
            ui.statusbar.showMessage('Exiting... select the overlay layer result file')
            return

    #layer_base = qgis.core.QgsVectorLayer(
    #    r'C:\PENN_STATE\GEOG489\FINAL_PROJECT\Datasets\Hondo_Parcels_2019_Dissolve_4326.shp')

    #layer_comparison = qgis.core.QgsVectorLayer(
    #    r'C:\PENN_STATE\GEOG489\FINAL_PROJECT\Datasets\Hondo_Parcels_2022_Dissolve_4326.shp')
    #layer_overlay = qgis.core.QgsVectorLayer(r'C:\PENN_STATE\GEOG489\FINAL_PROJECT\Datasets\zoning_4326.shp')
    #layer_result_file = r'C:\PENN_STATE\GEOG489\FINAL_PROJECT\Results\market_value.gpkg'

    if ui.resultCkB.isChecked():
        layer_result = qgis.core.QgsVectorLayer('Polygon?crs=' + layer_comparison.crs().authid() +
                                            '&field='+ ui.comparisonCB.currentText()+':string(25)&field=OWNER_NAME:string(70)&field=PCT_CHANGE:double' \
                                            '&field=BASE_VALUE:double&field=NEW_VALUE:double',
                                            'results', 'memory')

    #layer_overlay_result_file = r'C:\PENN_STATE\GEOG489\FINAL_PROJECT\Results\overlay_result.gpkg'

    if ui.resultOverlayCkB.isChecked():
        layer_overlay_result = qgis.core.QgsVectorLayer('Polygon?crs=' + layer_overlay.crs().authid() +
                                                    '&field=ID:string(25)' \
                                                    '&field=DESC:string(80)' \
                                                    '&field=AVERAGE:double' \
                                                    '&field=MEDIAN:double',
                                                    'overlay_results', 'memory')

    for field in layer_base.fields():
        print(field.name())
        print(field.typeName())
        print(field.length())
        print(field.isNumeric())
        print('----------')

    for feature in layer_base.getFeatures():
        dict_base[str(feature[ui.baseCB.currentText()])] = feature

    print('Dictionary base length ' + str(len(dict_base)))

    print('')
    print('++++++++++++++')
    for field in layer_overlay.fields():
        print(field.name())
        print(field.typeName())
        print(field.length())
        print(field.isNumeric())
        print('----------')


    for feature in layer_comparison.getFeatures():
        dict_comparison[str(feature[ui.comparisonCB.currentText()])] = feature


    for feature in layer_overlay.getFeatures():
        dict_overlay[str(feature['gid'])] = overlay.Overlay(feature)





    # Find features in comparison layer that are in the base layer to evaluate the change in market value
    # As these feature are found create a new layer with the percentage change in market value.

    features_result = []

    for id_compare in dict_comparison:
        print(id_compare)
        #if id_compare == '1985':
        #    print('Found 1985')
        feature_comparison = dict_comparison[id_compare]
        if feature_comparison[ui.comparisonParamCB.currentText()] > 0:

            if id_compare in dict_base:
                #print(id_base)
                feature_base = dict_base[id_compare]

                #print(feature_base[ui.baseParamCB.currentText()])
                if feature_base[ui.baseParamCB.currentText()] > 0:
                    pct_change = 100 * (feature_comparison[ui.comparisonParamCB.currentText()] - feature_base[ui.baseParamCB.currentText()]) / feature_base[ui.baseParamCB.currentText()]
                    feature_new = qgis.core.QgsFeature()
                    feature_new.setAttributes([str(feature_comparison[ui.comparisonCB.currentText()]), feature_comparison['OWNER_NAME'],
                                          pct_change, feature_base[ui.baseParamCB.currentText()], feature_comparison[ui.comparisonParamCB.currentText()]])
                    feature_new.setGeometry(feature_comparison.geometry())
                    features_result.append(feature_new)

                    element = overlay.OverlayElement(str(feature_comparison[ui.comparisonCB.currentText()]), feature_comparison.geometry(),
                                                 feature_base[ui.baseParamCB.currentText()], feature_comparison[ui.comparisonParamCB.currentText()])
                    for id_overlay in dict_overlay:
                        if dict_overlay[id_overlay].feature.geometry().contains(feature_comparison.geometry().centroid()):
                            dict_overlay[id_overlay].addElement(element)

    if ui.resultCkB.isChecked():
        resultProvider = layer_result.dataProvider()
        resultProvider.addFeatures(features_result)
        print(len(features_result))


    overlay_result = []
    num_elements = 0

    for id_overlay in dict_overlay:
        num_elements += (len(dict_overlay[id_overlay].elements))
        print('Number of elements in Overlay: ' + str(id_overlay) + ' : ' + str((len(dict_overlay[id_overlay].elements))))

        feature_overlay = qgis.core.QgsFeature()
        dict_overlay[id_overlay].calculateAverage()
        dict_overlay[id_overlay].calculateMedian()
        feature_overlay.setAttributes([str(id_overlay), str(dict_overlay[id_overlay].feature["layer"]) +
                                                    ': ' +
                                                    str(dict_overlay[id_overlay].feature["label"]),
                                                    dict_overlay[id_overlay].average_change,
                                                    dict_overlay[id_overlay].median_change])
        feature_overlay.setGeometry(dict_overlay[id_overlay].feature.geometry())
        overlay_result.append(feature_overlay)

    if ui.resultOverlayCkB.isChecked():
        overlayProvider = layer_overlay_result.dataProvider()
        overlayProvider.addFeatures(overlay_result)

    print('Total elements: ' + str(num_elements))
    if ui.resultCkB.isChecked():
        qgis.core.QgsVectorFileWriter.writeAsVectorFormat(layer_result, layer_result_file, "utf-8", layer_comparison.crs(), "GPKG")
    if ui.resultOverlayCkB.isChecked():
        qgis.core.QgsVectorFileWriter.writeAsVectorFormat(layer_overlay_result, layer_overlay_result_file, "utf-8", layer_overlay.crs(), "GPKG")


# ==========================================
# connect signals
# ==========================================
ui.baseTB.clicked.connect(selectBaseShapefile)
ui.comparisonTB.clicked.connect(selectComparisonShapefile)
ui.overlayTB.clicked.connect(selectOverlayShapefile)
ui.resultTB.clicked.connect(selectNewResultGPKGfile)
ui.resultOverlayTB.clicked.connect(selectNewOverlayResultGPKGfile)
ui.runPB.clicked.connect(processData)
ui.resultCkB.clicked.connect(resultToggle)
ui.resultOverlayCkB.clicked.connect(resultOverlayToggle)
ui.baseLE.editingFinished.connect(updateBaseCB)
ui.baseLE.editingFinished.connect(updateBaseParamCB)
ui.comparisonLE.editingFinished.connect(updateComparisonCB)
ui.comparisonLE.editingFinished.connect(updateComparisonParamCB)

# =======================================
# run app
# =======================================
mainWindow.show()

qgs.exitQgis()
sys.exit(app.exec_())

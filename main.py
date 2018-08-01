#!/usr/bin/env python
from __future__ import print_function
from PyQt4 import QtGui, QtCore  # Import the PyQt4 module we'll need
from shutil import copyfile
import sys  # We need sys so that we can pass argv to QApplication
from subprocess import PIPE, Popen
import design  # This file holds our MainWindow and all design related things
import ReduceDictionary
import shlex
import math

# it also keeps events etc that we defined in Qt Designer
import os  # For listing filepath methods
import string

class MantidReduction(QtGui.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        # Explaining super is out of the scope of this article
        # So please google it if you're not familar with it
        # Simple reason why we use it here is that it allows us to
        # access variables, methods etc in the design.py file
        super(self.__class__, self).__init__()
        self.setupUi(self)  # This is defined in design.py file automatically
        # It sets up layout and widgets that are defined
        self.setDefaults()
        self.ConfigFileName_ledt.textChanged.connect(self.change_Configfile)
        self.ConfigFile_btn.clicked.connect(self.Configbrowse_file)  # When the button is pressed
        self.BackgroundFileName_ledt.textChanged.connect(self.change_file)
        self.BackgroundFile_btn.clicked.connect(self.browse_file)  # When the button is pressed
        self.UBFileName_ledt.textChanged.connect(self.change_UBfile)
        self.UBFile_btn.clicked.connect(self.UBbrowse_file)  # When the button is pressed
        self.instrument_cmbx.currentIndexChanged.connect(self.change_instrument)
        self.z_score_ledt.textChanged.connect(self.input_z_score)
        self.bkg_inner_radius_ledt.textChanged.connect(self.input_bkg_inner_radius)
        self.bkg_outer_radius_ledt.textChanged.connect(self.input_bkg_outer_radius)
        self.CalFileName_ledt.textChanged.connect(self.change_cal_file)
        self.CalFile_btn.clicked.connect(self.browse_cal_file)  # When the button is pressed
        self.spectraFileName_ledt.textChanged.connect(self.change_spectra_file)
        self.spectraFile_btn.clicked.connect(self.browse_spectra_file)  # When the button is pressed
        self.pred_minDSpacing_ledt.textChanged.connect(self.change_pred_minDSpacing)
        self.pred_maxDSpacing_ledt.textChanged.connect(self.change_pred_maxDSpacing)
        self.pred_minWavelength_ledt.textChanged.connect(self.change_pred_minWavelength)
        self.pred_maxWavelength_ledt.textChanged.connect(self.change_pred_maxWavelength)
        self.minDSpacing_ledt.textChanged.connect(self.change_minDSpacing)
        self.minWavelength_ledt.textChanged.connect(self.change_minWavelength)
        self.maxWavelength_ledt.textChanged.connect(self.change_maxWavelength)
        self.pointGroup_cmbx.currentIndexChanged.connect(self.change_pointGroup)
        self.laueGroup_cmbx.currentIndexChanged.connect(self.change_laueGroup)
        self.centering_cmbx.currentIndexChanged.connect(self.change_centering)
        self.sampleRadius_ledt.textChanged.connect(self.change_sampleRadius)
        self.molecularFormula_ledt.textChanged.connect(self.change_molecularFormula)
        self.expName_ledt.textChanged.connect(self.change_expName)
        self.runNums_ledt.textChanged.connect(self.change_runNums)
        self.Z_ledt.textChanged.connect(self.change_Z)
        self.unitCellVolume_ledt.textChanged.connect(self.change_unitCellVolume)
        self.splitThreshold_ledt.textChanged.connect(self.change_splitThreshold)
        self.maxQspace_ledt.textChanged.connect(self.change_maxQ)
        self.maxQspace_ledt_2.editingFinished.connect(self.change_maxQ2)
        self.numberPeaks_ledt.textChanged.connect(self.change_numPeaks)
        self.minABC_ledt.textChanged.connect(self.change_minABC)
        self.maxABC_ledt.textChanged.connect(self.change_maxABC)
        self.tolerance_ledt.textChanged.connect(self.change_tolerance)
        self.peakRadius_ledt.textChanged.connect(self.change_peakRadius)
        self.minIntensity_ledt.textChanged.connect(self.change_minIntensity)
        self.normToWavelength_ledt.textChanged.connect(self.change_normToWavelength)
        self.predictPeaks_chbx.stateChanged.connect(self.predict_peaks)  # When the button is pressed
        self.minIsigI_ledt.textChanged.connect(self.change_minIsigI)
        self.scaleFactor_ledt.textChanged.connect(self.change_scaleFactor)
        self.edgePixels_ledt.textChanged.connect(self.change_edgePixels)
        self.starting_batch_number_ledt.textChanged.connect(self.change_starting_batch_number)
        self.borderPixels_ledt.textChanged.connect(self.change_borderPixels)
        self.ellipse_size_specified_chbx.stateChanged.connect(self.ellipse_size)  # When the button is pressed
        self.dataDirectory_ledt.textChanged.connect(self.change_datadir)
        self.dataDirectory_btn.clicked.connect(self.browse_datadir)  # When the button is pressed
        self.PushButton_config.clicked.connect(self.accept)  # When the button is pressed
        self.PushButton_auto.clicked.connect(self.auto)  # When the button is pressed
        self.PushButton_run.clicked.connect(self.run)  # When the button is pressed

    def format_template(self, name, outfile, **kwargs):
        "This fills in the values for the template called 'name' and writes it to 'outfile'"
        template = open(name).read()
        formatter = string.Formatter()
        data = formatter.format(template, **kwargs)
        f = open(outfile, "w")
        try:
            f.write(data)
        finally:
            f.close()

    def setDefaults(self):
        self.molecularFormula = ""
        self.Z = str( 0.0)
        self.unitCellVolume = str( 0.0)
        self.sampleRadius = str( 0.0)
        self.centering = "P"
        self.laueGroup = "Triclinic"
        self.pointGroup = "-1"
        self.instrument = "TOPAZ"
        self.runNums = ""
        baseDir = os.environ['PWD']
        self.dataDirectory = baseDir[:baseDir.find("shared")]+"data"
        self.dataDirectory_ledt.setText(self.dataDirectory)
        self.expName = ""
        self.calFileName = "/SNS/TOPAZ/shared/calibrations/2018B/TOPAZ_2018B.DetCal"
        self.subtract_bkg = False
        self.backgroundFileName = "None"
        self.read_UB = False
        self.UBFileName = "None"
        self.maxQ = str(17.0)
        self.splitThreshold = str(80)
        self.edgePixels = str(0)
        self.numPeaksToFind = str( 500)
        self.abcMin = str( 5)
        self.abcMax = str( 12)
        self.tolerance = str( 0.12)
        self.predictPeaks = str( True)
        self.pred_minDSpacing = str( 0.499)
        self.pred_maxDSpacing = str( 11.0)
        self.pred_minWavelength = str( 0.4)
        self.pred_maxWavelength = str( 3.45)
        self.ellipse_size_specified = str( True)
        self.peakRadius = str( 0.11)
        self.bkg_inner_radius = str( 0.115)
        self.bkg_outer_radius = str( 0.14)
        self.spectraFileName='/SNS/TOPAZ/shared/calibrations/2018B/Spectrum_2mmBN_26600_26602.dat'
        self.normToWavelength = str(1.0)
        self.scaleFactor = str(0.05)
        self.minIntensity = str( 10)
        self.minIsigI = str(2.0)
        self.borderPixels = str(18)
        self.minDSpacing = str( 0.5)
        self.minWavelength = str( 0.4)
        self.maxWavelength = str( 3.5)
        self.z_score = str( 4.0)
        self.starting_batch_number = str( 1)

    def loadConfig(self, config_file_name):
        params_dictionary = ReduceDictionary.LoadDictionary( config_file_name )
        self.molecularFormula = str(params_dictionary[ "formulaString" ])
        self.molecularFormula_ledt.setText(self.molecularFormula)
        self.Z = str(float(params_dictionary[ "zParameter" ]))
        self.Z_ledt.setText(self.Z)
        self.unitCellVolume = str(float(params_dictionary[ "unitCellVolume" ]))
        self.unitCellVolume_ledt.setText(self.unitCellVolume)
        self.sampleRadius = str(float(params_dictionary.get("sampleRadius",'1.0')))
        self.sampleRadius_ledt.setText(self.sampleRadius)
        self.centering = str(params_dictionary[ "centering" ])
        self.centering_cmbx.setCurrentIndex(self.centering_cmbx.findText(self.centering, QtCore.Qt.MatchFixedString))
        self.laueGroup = str(params_dictionary[ "cell_type" ])
        self.laueGroup_cmbx.setCurrentIndex(self.laueGroup_cmbx.findText(self.laueGroup, QtCore.Qt.MatchFixedString))
        self.pointGroup = str(params_dictionary["pg_symbol"])
        self.pointGroup_cmbx.setCurrentIndex(self.pointGroup_cmbx.findText(self.pointGroup, QtCore.Qt.MatchFixedString))
        self.instrument = str(params_dictionary[ "instrument_name" ])
        self.instrument_cmbx.setCurrentIndex(self.instrument_cmbx.findText(self.instrument, QtCore.Qt.MatchFixedString))
        file = open(config_file_name)
        for line in file:
          line = line.strip();
          line = line.rstrip();
          if (not line.startswith('#')) and len(line) > 2:
            words = shlex.split(line)
            if len(words) > 1:
              if words[0] == "run_nums":
                self.runNums = words[1]
        self.runNums = str(self.runNums).strip('[]')
        self.runNums = self.runNums.replace(" ", "")
        self.runNums = self.runNums.replace("'", "")
        self.runNums_ledt.setText(self.runNums)
        #self.dataDirectory=str(params_dictionary[ "data_directory" ])
        #self.dataDirectory_ledt.setText(self.dataDirectory)
        #Do not copy experiment name so you will not overwrite previous data
        #self.expName = str(params_dictionary[ "exp_name" ])
        self.expName_ledt.setText(self.expName)
        self.calFileName = str(params_dictionary[ "calibration_file_1" ])
        self.CalFileName_ledt.setText(self.calFileName)
        self.subtract_bkg = params_dictionary[ "subtract_bkg" ]
        self.backgroundFileName = str(params_dictionary[ "no_sample_event_nxs_fname" ])
        self.BackgroundFileName_ledt.setText(self.backgroundFileName)
        self.read_UB = params_dictionary[ "read_UB" ]
        self.UBFileName = str(params_dictionary[ "UB_filename" ])
        self.UBFileName_ledt.setText(self.UBFileName)
        self.maxQ = str(params_dictionary.get('Qmax', "20"))
        self.maxQspace_ledt.setText(self.maxQ)
        self.splitThreshold = str(params_dictionary[ "split_threshold" ])
        self.splitThreshold_ledt.setText(self.splitThreshold)
        self.edgePixels = str(params_dictionary[ "n_bad_edge_pixels" ])
        self.edgePixels_ledt.setText(self.edgePixels)
        self.numPeaksToFind = str(params_dictionary[ "num_peaks_to_find" ])
        self.numberPeaks_ledt.setText(self.numPeaksToFind)
        self.abcMin = str(params_dictionary[ "min_d" ])
        self.minABC_ledt.setText(self.abcMin)
        self.abcMax = str(params_dictionary[ "max_d" ])
        self.maxABC_ledt.setText(self.abcMax)
        self.tolerance = str(params_dictionary[ "tolerance" ])
        self.tolerance_ledt.setText(self.tolerance)
        self.predictPeaks = params_dictionary[ "integrate_predicted_peaks" ]
        self.predictPeaks_chbx.setChecked(self.predictPeaks)
        self.pred_minDSpacing = str(params_dictionary[ "min_pred_dspacing" ])
        self.pred_minDSpacing_ledt.setText(self.pred_minDSpacing)
        self.pred_maxDSpacing = str(params_dictionary[ "max_pred_dspacing" ])
        self.pred_maxDSpacing_ledt.setText(self.pred_maxDSpacing)
        self.pred_minWavelength = str(params_dictionary[ "min_pred_wl" ])
        self.pred_minWavelength_ledt.setText(self.pred_minWavelength)
        self.pred_maxWavelength = str(params_dictionary[ "max_pred_wl" ])
        self.pred_maxWavelength_ledt.setText(self.pred_maxWavelength)
        self.ellipse_size_specified = params_dictionary[ "ellipse_size_specified" ]
        self.ellipse_size_specified_chbx.setChecked(self.ellipse_size_specified)
        self.peakRadius = str(params_dictionary[ "peak_radius" ])
        self.peakRadius_ledt.setText(self.peakRadius)
        self.bkg_inner_radius = str(params_dictionary[ "bkg_inner_radius" ])
        self.bkg_inner_radius_ledt.setText(self.bkg_inner_radius)
        self.bkg_outer_radius = str(params_dictionary[ "bkg_outer_radius" ])
        self.bkg_outer_radius_ledt.setText(self.bkg_outer_radius)
        self.spectraFileName = str(params_dictionary["spectraFile"])
        self.spectraFileName_ledt.setText(self.spectraFileName)
        self.normToWavelength = str(float(params_dictionary["normToWavelength"]))
        self.normToWavelength_ledt.setText(self.normToWavelength)
        self.scaleFactor = str(float(params_dictionary["scaleFactor"]))
        self.scaleFactor_ledt.setText(self.scaleFactor)
        self.minIntensity = str(float(params_dictionary["intiMin"]))
        self.minIntensity_ledt.setText(self.minIntensity)
        self.minIsigI = str(float(params_dictionary["minIsigI"]))
        self.minIsigI_ledt.setText(self.minIsigI)
        self.borderPixels = str(int(params_dictionary["numBorderCh"]))
        self.borderPixels_ledt.setText(self.borderPixels)
        self.minDSpacing = str(float(params_dictionary["dMin"]))
        self.minDSpacing_ledt.setText(self.minDSpacing)
        self.minWavelength = str(float(params_dictionary["wlMin"]))
        self.minWavelength_ledt.setText(self.minWavelength)
        self.maxWavelength = str(float(params_dictionary["wlMax"]))
        self.maxWavelength_ledt.setText(self.maxWavelength)
        self.z_score = str(float(params_dictionary["z_score"]))
        self.z_score_ledt.setText(self.z_score)
        self.starting_batch_number = str(int(params_dictionary.get("starting_batch_number",'1')))
        self.starting_batch_number_ledt.setText(self.starting_batch_number)

    def change_instrument(self):
        self.instrument = self.instrument_cmbx.currentText()

    def change_laueGroup(self):
        self.laueGroup = self.laueGroup_cmbx.currentText()
        self.pointGroup_cmbx.clear()
        list1 = []
        if self.laueGroup == "Triclinic":
            list1 = [
                self.tr('-1'),
                self.tr('1'),
                ]
        elif self.laueGroup == "Monoclinic":
            list1 = [
                self.tr('2/m'),
                self.tr('2'),
                self.tr('m'),
                self.tr('112'),
                self.tr('112/m'),
                self.tr('11m'),
                ]
        elif self.laueGroup == "Orthorhombic":
            list1 = [
                self.tr('mmm'),
                self.tr('222'),
                self.tr('mm2'),
                self.tr('2mm'),
                self.tr('m2m'),
                ]
        elif self.laueGroup == "Tetragonal":
            list1 = [
                self.tr('4/m'),
                self.tr('4/mmm'),
                self.tr('-4'),
                self.tr('-42m'),
                self.tr('-4m2'),
                self.tr('4'),
                self.tr('422'),
                self.tr('4mm'),
                ]
        elif self.laueGroup == "Trigonal - Rhombohedral":
            list1 = [
                self.tr('-3'),
                self.tr('-3m'),
                self.tr('3'),
                self.tr('32'),
                self.tr('3m'),
                self.tr('-3 r'),
                self.tr('-31m'),
                self.tr('-3m r'),
                self.tr('-3m1'),
                self.tr('3 r'),
                self.tr('312'),
                self.tr('31m'),
                self.tr('32 r'),
                self.tr('321'),
                self.tr('3m r'),
                self.tr('3m1'),
                ]
        elif self.laueGroup == "Hexagonal":
            list1 = [
                self.tr('6/m'),
                self.tr('6/mmm'),
                self.tr('6'),
                self.tr('-6'),
                self.tr('622'),
                self.tr('6mm'),
                self.tr('-62m'),
                self.tr('-6m2'),
                ]
        elif self.laueGroup == "Cubic":
            list1 = [
                self.tr('m-3'),
                self.tr('m-3m'),
                self.tr('23'),
                self.tr('432'),
                self.tr('-43m'),
                ]
        self.pointGroup_cmbx.addItems(list1)


    def change_pointGroup(self):
        self.pointGroup = self.pointGroup_cmbx.currentText()

    def change_centering(self):
        self.centering = self.centering_cmbx.currentText()
        self.laueGroup_cmbx.clear()
        list1 = []
        if self.centering == "P":
            list1 = [
                self.tr('Triclinic'),
                self.tr('Monoclinic'),
                self.tr('Orthorhombic'),
                self.tr('Tetragonal'),
                self.tr('Trigonal - Rhombohedral'),
                self.tr('Hexagonal'),
                self.tr('Cubic'),
                ]
        elif self.centering == "I":
            list1 = [
                self.tr('Tetragonal'),
                self.tr('Monoclinic'),
                self.tr('Cubic'),
                self.tr('Orthorhombic'),
                ]
        elif self.centering == "A":
            list1 = [
                self.tr('Monoclinic'),
                self.tr('Orthorhombic'),
                ]
        elif self.centering == "B":
            list1 = [
                self.tr('Monoclinic'),
                self.tr('Orthorhombic'),
                ]
        elif self.centering == "C":
            list1 = [
                self.tr('Monoclinic'),
                self.tr('Orthorhombic'),
                ]
        elif self.centering == "F":
            list1 = [
                self.tr('Orthorhombic'),
                self.tr('Cubic'),
                ]
        elif self.centering == "Robv":
            list1 = [
                self.tr('Trigonal - Rhombohedral'),
                ]
        elif self.centering == "Rrev":
            list1 = [
                self.tr('Trigonal - Rhombohedral'),
                ]
        self.laueGroup_cmbx.addItems(list1)

    def input_z_score(self):
        self.z_score = self.toDouble(self.z_score_ledt.text())

    def input_bkg_inner_radius(self):
        self.bkg_inner_radius = self.toDouble(self.bkg_inner_radius_ledt.text())

    def input_bkg_outer_radius(self):
        self.bkg_outer_radius = self.toDouble(self.bkg_outer_radius_ledt.text())

    def change_Configfile(self):
        self.ConfigFileName = self.ConfigFileName_ledt.text()
        if self.ConfigFileName != "None":
            self.loadConfig(self.ConfigFileName)

    def change_UBfile(self):
        self.UBFileName = str(self.UBFileName_ledt.text())
        if self.UBFileName != "None" and self.UBFileName != "":
            self.read_UB = True
        else:
            self.read_UB = False
            self.UBFileName = "None"

    def change_spectra_file(self):
        self.spectraFileName = self.spectraFileName_ledt.text()

    def change_file(self):
        self.backgroundFileName = self.BackgroundFileName_ledt.text()
        if self.backgroundFileName != "None" and self.backgroundFileName != "":
            self.subtract_bkg = True
        else:
            self.subtract_bkg = False
            self.backgroundFileName = "None"

    def change_cal_file(self):
        self.calFileName = self.CalFileName_ledt.text()
        if self.calFileName == "":
            self.calFileName = "None"

    def change_datadir(self):
        self.dataDirectory = self.dataDirectory_ledt.text()
        if self.dataDirectory == "":
            self.dataDirectory = "None"

    def Configbrowse_file(self):
        self.ConfigFileName = QtGui.QFileDialog.getOpenFileName(self, 'Open File', '', '*.config') # Filename line
        if self.ConfigFileName:
            self.ConfigFileName_ledt.setText(self.ConfigFileName)

    def UBbrowse_file(self):
        self.UBFileName = QtGui.QFileDialog.getOpenFileName(self, 'Open File', '', '*.mat') # Filename line
        if self.UBFileName:
            self.UBFileName_ledt.setText(self.UBFileName)

    def browse_spectra_file(self):
        self.spectraFileName = QtGui.QFileDialog.getOpenFileName(self, 'Open File', '', '*.dat') # Filename line
        if self.spectraFileName:
            self.spectraFileName_ledt.setText(self.spectraFileName)

    def browse_file(self):
        self.backgroundFileName = QtGui.QFileDialog.getOpenFileName(self, 'Open File', '', '*.nxs *.h5') # Filename line
        if self.backgroundFileName:
            self.BackgroundFileName_ledt.setText(self.backgroundFileName)

    def browse_cal_file(self):
        self.calFileName = QtGui.QFileDialog.getOpenFileName(self, 'Open File', '', '*.DetCal') # Filename line
        if self.calFileName:
            self.CalFileName_ledt.setText(self.calFileName)

    def browse_datadir(self):
        self.dataDirectory = QtGui.QFileDialog.getExistingDirectory(self, 'Select Directory', '', options=QtGui.QFileDialog.ShowDirsOnly)
        if self.dataDirectory:
            self.dataDirectory_ledt.setText(self.dataDirectory)

    def change_pred_minDSpacing(self):
        self.pred_minDSpacing = self.toDouble(self.pred_minDSpacing_ledt.text())

    def change_pred_maxDSpacing(self):
        self.pred_maxDSpacing = self.toDouble(self.pred_maxDSpacing_ledt.text())

    def change_pred_minWavelength(self):
        self.pred_minWavelength = self.toDouble(self.pred_minWavelength_ledt.text())

    def change_pred_maxWavelength(self):
        self.pred_maxWavelength = self.toDouble(self.pred_maxWavelength_ledt.text())

    def change_minDSpacing(self):
        self.minDSpacing = self.toDouble(self.minDSpacing_ledt.text())

    def change_minWavelength(self):
        self.minWavelength = self.toDouble(self.minWavelength_ledt.text())

    def change_maxWavelength(self):
        self.maxWavelength = self.toDouble(self.maxWavelength_ledt.text())

    def change_sampleRadius(self):
        self.sampleRadius = self.toDouble(self.sampleRadius_ledt.text())

    def change_molecularFormula(self):
        self.molecularFormula = self.molecularFormula_ledt.text()

    def change_expName(self):
        self.expName = self.expName_ledt.text()

    def change_runNums(self):
        self.runNums = str(self.runNums_ledt.text())

    def change_Z(self):
        self.Z = self.toDouble(self.Z_ledt.text())

    def change_unitCellVolume(self):
        self.unitCellVolume = self.toDouble(self.unitCellVolume_ledt.text())

    def change_splitThreshold(self):
        temp = self.splitThreshold_ledt.text()
        self.splitThreshold = int(temp)

    def change_maxQ(self):
        self.maxQ = self.toDouble(self.maxQspace_ledt.text())

    def change_maxQ2(self):
        #Dmin is specified instead of Qmax
        self.maxQ = 2*math.pi/self.toDouble(self.maxQspace_ledt_2.text())

    def toDouble(self, temp):
        if temp.contains('.') or temp.contains("e"):
            result = float(temp)
        else:
            temp_int = int(temp)
            result = float(temp_int)
        return result

    def predict_peaks(self, state):
        if state == QtCore.Qt.Checked:
            self.predictPeaks = True
            self.pred_minDSpacing_ledt.setEnabled(True)
            self.pred_maxDSpacing_ledt.setEnabled(True)
            self.pred_minWavelength_ledt.setEnabled(True)
            self.pred_maxWavelength_ledt.setEnabled(True)
        else:
            self.predictPeaks = False
            self.pred_minDSpacing_ledt.setDisabled(True)
            self.pred_maxDSpacing_ledt.setDisabled(True)
            self.pred_minWavelength_ledt.setDisabled(True)
            self.pred_maxWavelength_ledt.setDisabled(True)

    def ellipse_size(self, state):
        if state == QtCore.Qt.Checked:
            self.ellipse_size_specified = True
        else:
            self.ellipse_size_specified = False

    def change_numPeaks(self):
        temp = self.numberPeaks_ledt.text()
        self.numPeaksToFind = int(temp)

    def change_minABC(self):
        self.abcMin = self.toDouble(self.minABC_ledt.text())

    def change_maxABC(self):
        self.abcMax = self.toDouble(self.maxABC_ledt.text())

    def change_tolerance(self):
        self.tolerance = self.toDouble(self.tolerance_ledt.text())

    def change_peakRadius(self):
        self.peakRadius = self.toDouble(self.peakRadius_ledt.text())

    def change_minIntensity(self):
        self.minIntensity = self.toDouble(self.minIntensity_ledt.text())

    def change_normToWavelength(self):
        self.normToWavelength = self.toDouble(self.normToWavelength_ledt.text())

    def change_minIsigI(self):
        self.minIsigI = self.toDouble(self.minIsigI_ledt.text())

    def change_starting_batch_number(self):
        temp = self.starting_batch_number_ledt.text()
        self.starting_batch_number = int(temp)

    def change_edgePixels(self):
        temp = self.edgePixels_ledt.text()
        self.edgePixels = int(temp)

    def change_borderPixels(self):
        temp = self.borderPixels_ledt.text()
        self.borderPixels = int(temp)

    def change_scaleFactor(self):
        self.scaleFactor = self.toDouble(self.scaleFactor_ledt.text())

    def reject(self):
        print ("script has been killed")
        self.proc.kill()
        
    def accept(self):
        #Generate config file 
        baseDir = os.environ['PWD']
        outDir = baseDir[:baseDir.find("shared")]+"shared/"+self.expName
        print ("Working directory: ",outDir)
        pg = self.pointGroup
        print ("Point group: ",pg)
        kw = {
            "molecularFormula": self.molecularFormula,
            "Z": self.Z,
            "unitCellVolume": self.unitCellVolume,
            "sampleRadius": self.sampleRadius,
            "instrument": self.instrument,
            "calFileName": self.calFileName,
            "maxQ": self.maxQ,
            "split_threshold": self.splitThreshold,
            "backgroundFileName": self.backgroundFileName,
            "subtract_bkg": self.subtract_bkg,
            "outputDirectory": outDir,
            "data_directory": self.dataDirectory,
            "UB_filename": self.UBFileName,
            "read_UB": self.read_UB,
            "centering": self.centering,
            "cell_type": self.laueGroup,
            "numPeaksToFind": self.numPeaksToFind,
            "abcMin": self.abcMin,
            "abcMax": self.abcMax,
            "tolerance": self.tolerance,
            "predictPeaks": self.predictPeaks,
            "min_pred_dspacing": self.pred_minDSpacing,
            "max_pred_dspacing": self.pred_maxDSpacing,
            "min_pred_wl": self.pred_minWavelength,
            "max_pred_wl": self.pred_maxWavelength,
            "peak_radius": self.peakRadius,
            "bkg_inner_radius": self.bkg_inner_radius,
            "bkg_outer_radius": self.bkg_outer_radius,
            "ellipse_size_specified": self.ellipse_size_specified,
            "n_bad_edge_pixels": self.edgePixels,
            "exp_name": self.expName,
            "run_nums": self.runNums,
            "spectraFileName": self.spectraFileName,
            "normToWavelength": self.normToWavelength,
            "minIsigI": self.minIsigI,
            "numBorderCh": self.borderPixels,
            "minIntensity": self.minIntensity,
            "min_dspacing": self.minDSpacing,
            "scaleFactor": self.scaleFactor,
            "min_wl": self.minWavelength,
            "max_wl": self.maxWavelength,
            "pg_symbol": pg,
            "z_score": self.z_score,
            "starting_batch_number": self.starting_batch_number

        }

        templatePath = "./template.config"
        self.path = self.expName+".config"
        self.format_template(templatePath, self.path, **kw)
        print ("Wrote new config file: ",self.path)

    def auto(self):
        baseDir = os.environ['PWD']
        autoConfig = baseDir[:baseDir.find("shared")]+"shared/autoreduce/autoreduce.config"
        copyfile(self.path, autoConfig)

        with open(autoConfig, 'r') as file :
          filedata = file.read()
        filedata = filedata.replace('shared/'+self.expName, 'shared/autoreduce')
        with open(autoConfig, 'w') as file:
          file.write(filedata)
        print ("Copied config file: ",autoConfig)

    def run(self):
        self.accept()
        self.proc = Popen(['/usr/bin/python','topaz_reduction.py', str(self.path)])
        print ("Finished reduction")

def main():
    app = QtGui.QApplication(sys.argv)  # A new instance of QApplication
    form = MantidReduction()  # We set the form to be our MantidReduction (design)
    form.show()  # Show the form
    app.exec_()  # and execute the app
    os.system('stty sane')


if __name__ == '__main__':  # if we're running file directly and not importing it
    main()  # run the main function

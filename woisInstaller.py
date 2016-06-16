"""
***************************************************************************
   woisInstaller.py
-------------------------------------
    Copyright (C) 2014 TIGER-NET (www.tiger-net.org)

***************************************************************************
* This installer is part of the Water Observation Information System (WOIS)  *
* developed under the TIGER-NET project funded by the European Space      *
* Agency as part of the long-term TIGER initiative aiming at promoting    *
* the use of Earth Observation (EO) for improved Integrated Water         *
* Resources Management (IWRM) in Africa.                                  *
*                                                                         *
* WOIS is a free software i.e. you can redistribute it and/or modify      *
* it under the terms of the GNU General Public License as published       *
* by the Free Software Foundation, either version 3 of the License,       *
* or (at your option) any later version.                                  *
*                                                                         *
* WOIS is distributed in the hope that it will be useful, but WITHOUT ANY *
* WARRANTY; without even the implied warranty of MERCHANTABILITY or       *
* FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License   *
* for more details.                                                       *
*                                                                         *
* You should have received a copy of the GNU General Public License along *
* with this program.  If not, see <http://www.gnu.org/licenses/>.         *
***************************************************************************
"""

from PyQt4 import QtCore, QtGui
from installerGUI import installerWelcomeWindow, beamInstallWindow, beamPostInstallWindow, snapInstallWindow, snapPostInstallWindow
from installerGUI import osgeo4wInstallWindow, rInstallWindow, postgreInstallWindow, postgisInstallWindow
from installerGUI import mapwindowInstallWindow, mwswatInstallWindow, mwswatPostInstallWindow, swateditorInstallWindow, finishWindow
from installerGUI import extractingWaitWindow, copyingWaitWindow, uninstallInstructionsWindow, rPostInstallWindow
from installerGUI import CANCEL,SKIP,NEXT
import sys
import os
import errno
import shutil
import subprocess
import ctypes
from ctypes import wintypes
import re
from tempfile import NamedTemporaryFile
from zipfile import ZipFile
from distutils import dir_util

class woisInstaller():

    def __init__(self):
        self.util = Utilities()

    def runInstaller (self):
        ########################################################################
        # welcome window with license
        self.dialog =  installerWelcomeWindow()
        res = self.showDialog()

        if res == NEXT:
            # select installation files for 32 or 64 bit install
            if self.dialog.osComboBox.itemText(self.dialog.osComboBox.currentIndex()) == "32 bit":
                is32bit = True
                installationsDir = "Installations_x32"
                osgeo4wInstall = os.path.join(installationsDir, "osgeo4w-setup.bat")
                beamInstall = os.path.join(installationsDir, "beam_5.0_win32_installer.exe")
                snapInstall = os.path.join(installationsDir, "esa-snap_sentinel_windows-x32_3_0.exe")
                rInstall = os.path.join(installationsDir, "R-3.1.3-win.exe")
                postgreInstall = os.path.join(installationsDir, "postgresql-9.3.6-2-windows.exe")
                postgisInstall = os.path.join(installationsDir, "postgis-bundle-pg93x32-setup-2.1.5-1.exe")
                mapwindowInstall = os.path.join(installationsDir, "MapWindowx86Full-v488SR-installer.exe")
                mwswatInstall = os.path.join(installationsDir, "MWSWAT2009.exe")
                swateditorInstall = "MWSWAT additional software\\SwatEditor_Install\\Setup.exe"
            else:
                is32bit = False
                installationsDir = "Installations_x64"
                osgeo4wInstall = os.path.join(installationsDir, "osgeo4w-setup.bat")
                beamInstall = os.path.join(installationsDir, "beam_5.0_win64_installer.exe")
                snapInstall = os.path.join(installationsDir, "esa-snap_sentinel_windows-x64_3_0.exe")
                rInstall = os.path.join(installationsDir, "R-3.1.3-win.exe")
                postgreInstall = os.path.join(installationsDir, "postgresql-9.3.6-2-windows-x64.exe")
                postgisInstall = os.path.join(installationsDir, "postgis-bundle-pg93x64-setup-2.1.5-2.exe")
                mapwindowInstall = os.path.join(installationsDir, "MapWindowx86Full-v488SR-installer.exe")
                mwswatInstall = os.path.join(installationsDir, "MWSWAT2009.exe")
                swateditorInstall = "MWSWAT additional software\\SwatEditor_Install\\Setup.exe"
            # select default installation directories for 32 or 64 bit install
            if is32bit:
                osgeo4wDefaultDir = "C:\\OSGeo4W"
                snapDefaultDir = "C:\\Program Files\\snap"
                beamDefaultDir = "C:\\Program Files\\beam-5.0"
                mapwindowDefaultDir = "C:\\Program Files\\MapWindow"
                rDefaultDir = "C:\\Program Files\\R\\R-3.1.3"
            else:
                osgeo4wDefaultDir = "C:\\OSGeo4W64"
                snapDefaultDir = "C:\\Program Files\\snap"
                beamDefaultDir = "C:\\Program Files\\beam-5.0"
                mapwindowDefaultDir = "C:\\Program Files (x86)\\MapWindow"
                rDefaultDir = "C:\\Program Files\\R\\R-3.1.3"

        elif res == CANCEL:
            del self.dialog
            return
        else:
            self.unknownActionPopup()

        ########################################################################
        # Information about uninstalling old version
        self.dialog = uninstallInstructionsWindow();
        res = self.showDialog()
        if res == CANCEL:
            del self.dialog
            return

        ########################################################################
        # Install OSGeo4W (QGIS, OTB, SAGA, GRASS)

        self.dialog = osgeo4wInstallWindow();
        res = self.showDialog()

        # run the OSGeo4W installation here as an outside process
        if res == NEXT:
            self.util.execSubprocess(osgeo4wInstall)
            # copy the plugins
            dstPath = os.path.join(os.path.expanduser("~"),".qgis2","python")
            srcPath = os.path.join("QGIS WOIS plugins", "plugins.zip")
            # try to delete old plugins before copying the new ones to avoid conflicts
            self.util.deleteDir(os.path.join(dstPath, 'plugins', 'processing'))
            self.util.deleteDir(os.path.join(dstPath, 'plugins', 'processing_gpf'))
            self.util.deleteDir(os.path.join(dstPath, 'plugins', 'photo2shape'))
            self.util.deleteDir(os.path.join(dstPath, 'plugins', 'processing_workflow'))
            self.util.deleteDir(os.path.join(dstPath, 'plugins', 'processing_SWAT'))
            self.util.deleteDir(os.path.join(dstPath, 'plugins', 'openlayers_plugin'))
            self.util.deleteDir(os.path.join(dstPath, 'plugins', 'pointsamplingtool'))
            self.util.deleteDir(os.path.join(dstPath, 'plugins', 'temporalprofiletool'))
            self.util.deleteDir(os.path.join(dstPath, 'plugins', 'valuetool'))
            self.dialog = extractingWaitWindow(self.util, srcPath, dstPath) # show dialog because it might take some time on slower computers
            self.showDialog()
            # copy scripts and models
            dstPath = os.path.join(os.path.expanduser("~"),".qgis2","processing")
            srcPath = os.path.join("QGIS WOIS plugins", "scripts_and_models.zip")
            self.dialog = extractingWaitWindow(self.util, srcPath, dstPath) # show dialog because it might take some time on slower computers
            self.showDialog()
            # activate plugins and processing providers
            self.util.activatePlugins()
            self.util.activateProcessingProviders(osgeo4wDefaultDir)
        elif res == SKIP:
            pass
        elif res == CANCEL:
            del self.dialog
            return
        else:
            self.unknownActionPopup()


        ########################################################################
        # Install BEAM

        self.dialog = beamInstallWindow();
        res = self.showDialog()

        # run the BEAM installation here as an outside process
        if res == NEXT:
            self.util.execSubprocess(beamInstall)
            #self.dialog =  beamPostInstallWindow(beamDefaultDir);
            #res = self.showDialog()
        elif res == SKIP:
            pass
        elif res == CANCEL:
            del self.dialog
            return
        else:
            self.unknownActionPopup()

        # ask for post-installation even if user has skipped installation
        self.dialog =  beamPostInstallWindow(beamDefaultDir);
        res = self.showDialog()

        # copy the additional BEAM modules and set the amount of memory to be used with GPT
        if res == NEXT:
            dirPath = str(self.dialog.dirPathText.toPlainText())
            dstPath = os.path.join(dirPath,"modules")
            srcPath = "BEAM additional modules"
            self.dialog = copyingWaitWindow(self.util, srcPath, dstPath) # show dialog because it might take some time on slower computers
            self.showDialog()
            self.util.activateBEAMplugin(dirPath)

            # Temporary fix for https://github.com/TIGER-NET/Processing-GPF/issues/1, until new version of BEAM is out.
            # When that happens also remove beam-meris-radiometry-5.0.1.jar from "BEAM additional modules"
            #self.util.deleteFile(os.path.join(dstPath, "beam-meris-radiometry-5.0.jar"))
            #self.util.deleteFile(os.path.join(dstPath, "beam-meris-case2-regional-1.6.jar"))
        elif res == SKIP:
            pass
        elif res == CANCEL:
            del self.dialog
            return
        else:
            self.unknownActionPopup()

        ########################################################################
        # Install Snap Toolbox

        self.dialog = snapInstallWindow();
        res = self.showDialog()

        # run the Snap installation here as an outside process
        if res == NEXT:
            self.util.execSubprocess(snapInstall)
            #self.dialog =  snapPostInstallWindow(snapDefaultDir);
            #res = self.showDialog()
        elif res == SKIP:
            pass
        elif res == CANCEL:
            del self.dialog
            return
        else:
            self.unknownActionPopup()

        # ask for post-installation even if user has skipped installation
        self.dialog = snapPostInstallWindow(snapDefaultDir)
        res = self.showDialog()

        # Set the amount of memory to be used with NEST GPT
        if res == NEXT:
            dirPath = str(self.dialog.dirPathText.toPlainText())
            dstPath = os.path.join(os.path.expanduser("~"), ".snap")
            srcPath = "SNAP additional modules"
            self.util.copyFiles(srcPath, dstPath)
            #self.dialog = copyingWaitWindow(self.util, srcPath, dstPath) # show dialog because it might take some time on slower computers
            #self.showDialog()

            # There is a bug in snap installer so the gpt file has to be
            # modified for 32 bit installation
            if is32bit:
                self.util.removeIncompatibleJavaOptions(os.path.join(dirPath, 'bin', 'gpt.vmoptions'))
            self.util.activateSNAPplugin(dirPath)
        elif res == SKIP:
            pass
        elif res == CANCEL:
            del self.dialog
            return
        else:
            self.unknownActionPopup()


        ########################################################################
        # Install R

        self.dialog = rInstallWindow();
        res = self.showDialog()

        # run the R installation here as an outside process
        if res == NEXT:
            self.util.execSubprocess(rInstall)
            #self.dialog = rPostInstallWindow(rDefaultDir)
            #res = self.showDialog()
        elif res == SKIP:
            pass
        elif res == CANCEL:
            del self.dialog
            return
        else:
            self.unknownActionPopup()

        # ask for post-installation even if user has skipped installation
        self.dialog = rPostInstallWindow(rDefaultDir)
        res = self.showDialog()

        # Copy the R additional libraries
        if res == NEXT:
            dirPath = str(self.dialog.dirPathText.toPlainText())
            dstPath = os.path.join(dirPath,"library")
            srcPath = "R additional libraries"
            self.dialog = extractingWaitWindow(self.util, os.path.join(srcPath, "libraries.zip"), dstPath) # show dialog because it might take some time on slower computers
            self.showDialog()
            if is32bit:
                self.util.activateRplugin(dirPath, "false")
            else:
                self.util.activateRplugin(dirPath, "true")
        elif res == SKIP:
            pass
        elif res == CANCEL:
            del self.dialog
            return
        else:
            self.unknownActionPopup()

        ########################################################################
        # Install PostGIS

        self.dialog = postgreInstallWindow();
        res = self.showDialog()

        # run the postgresql installer as an outside process
        if res == NEXT:
            self.util.execSubprocess(postgreInstall)
            self.dialog = postgisInstallWindow();
            res = self.showDialog()
        elif res == SKIP:
            pass
        elif res == CANCEL:
            del self.dialog
            return
        else:
            self.unknownActionPopup()

        # run the postgis installer as an outside process
        if res == NEXT:
            self.util.execSubprocess(postgisInstall)
        elif res == SKIP:
            pass
        elif res == CANCEL:
            del self.dialog
            return
        else:
            self.unknownActionPopup()

        ########################################################################
        # Install MapWindow, SWAT and PEST

        self.dialog = mapwindowInstallWindow();
        res = self.showDialog()

        # run the MapWindow installer as an outside process
        if res == NEXT:
            self.util.execSubprocess(mapwindowInstall)
            self.dialog = mwswatInstallWindow();
            res = self.showDialog()
        elif res == SKIP:
            pass
        elif res == CANCEL:
            del self.dialog
            return
        else:
            self.unknownActionPopup()

        # run the MWSWAT installer as an outside process
        if res == NEXT:
            self.util.execSubprocess(mwswatInstall)
            self.dialog = swateditorInstallWindow();
            res = self.showDialog()
        elif res == SKIP:
            pass
        elif res == CANCEL:
            del self.dialog
            return
        else:
            self.unknownActionPopup()

        # run the SWAT editor installer as an outside process
        if res == NEXT:
            self.util.execSubprocess(swateditorInstall)
            self.dialog = mwswatPostInstallWindow(mapwindowDefaultDir);
            res = self.showDialog()
        elif res == SKIP:
            pass
        elif res == CANCEL:
            del self.dialog
            return
        else:
            self.unknownActionPopup()

        if res == NEXT:
            # copy the DTU customised MWSWAT 2009 installation
            dirPath = str(self.dialog.dirPathText.toPlainText())
            mwswatPath = os.path.join(dirPath,"Plugins","MWSWAT2009")
            dstPath = os.path.join(mwswatPath,'swat2009DtuEnvVers0.2')
            srcPath = "MWSWAT additional software\\swat2009DtuEnvVers0.2"
            self.dialog = copyingWaitWindow(self.util, srcPath, dstPath) # show dialog because it might take some time on slower computers
            self.showDialog()

            # copy and rename the customised MWSWAT exe
            if os.path.isfile(os.path.join(mwswatPath,"swat2009rev481.exe_old")):
                os.remove(os.path.join(mwswatPath,"swat2009rev481.exe_old"))
            os.rename(os.path.join(mwswatPath,"swat2009rev481.exe"), os.path.join(mwswatPath,"swat2009rev481.exe_old"))
            self.util.copyFiles(os.path.join(dstPath, "swat2009DtuEnv.exe"), mwswatPath)
            if os.path.isfile(os.path.join(mwswatPath,"swat2009rev481.exe")):
                os.remove(os.path.join(mwswatPath,"swat2009rev481.exe"))
            os.rename(os.path.join(mwswatPath,"swat2009DtuEnv.exe"), os.path.join(mwswatPath, "swat2009rev481.exe"))
            # copy the modified database file
            self.util.copyFiles("MWSWAT additional software\\mwswat2009.mdb", mwswatPath)
            # copy PEST
            self.dialog = copyingWaitWindow(self.util, "MWSWAT additional software\\PEST", os.path.join(mwswatPath,"PEST")) # show dialog because it might take some time on slower computers
            self.showDialog()
            # activate the plugin
            self.util.activateSWATplugin(dirPath)
        elif res == SKIP:
            pass
        elif res == CANCEL:
            del self.dialog
            return
        else:
            self.unknownActionPopup()

        # Finish
        self.dialog = finishWindow();
        self.showDialog()
        del self.dialog

    def showDialog(self):
        return(self.dialog.exec_())

    def unknownActionPopup(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setText("Unknown action chosen in the previous installation step. Ask the developer to check the installation script!\n\n Quitting installation")
        msgBox.exec_()


    ##########################################
    # helper functions

class Utilities(QtCore.QObject):
    finished = QtCore.pyqtSignal()

    def __init__(self):

        QtCore.QObject.__init__(self)
        # QGIS and processing settings
        self.qsettings = QtCore.QSettings("QGIS", "QGIS2")

    def execSubprocess(self, command):
        # command should be a path to an exe file so check if it exists
        if not os.path.isfile(command):
            msgBox = QtGui.QMessageBox()
            msgBox.setText("Could not find the installation file for this component!\n\n Skipping to next component")
            msgBox.exec_()
            #self.dialog.action = SKIP
            return

        proc = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                ).stdout
        for line in iter(proc.readline, ""):
            pass

    def deleteFile(self, filePath):
        try:
            os.remove(filePath)
        except:
            pass

    def deleteDir(self, dirPath):
        try:
            shutil.rmtree(dirPath, ignore_errors = True)
        except:
            pass

    def copyFiles(self, srcPath, dstPath, checkDstParentExists = True):

        # a simple check to see if we are copying to the right directory by making sure that
        # its parent exists
        if checkDstParentExists:
            if not os.path.isdir(os.path.dirname(dstPath)):
                msgBox = QtGui.QMessageBox()
                msgBox.setText("Could not find the destination directory!\n\n No files were copied.")
                msgBox.exec_()
                self.finished.emit()
                return

        # checkWritePremissions alsoe creates the directory if it doesn't exist yet
        if not self.checkWritePermissions(dstPath):
            msgBox = QtGui.QMessageBox()
            msgBox.setText("You do not have permissions to write to destination directory!\n\n No files were copied.\n\n"+
                           "Re-run the installer with administrator privileges or manually copy files from "+srcPath+
                           " to "+dstPath+" after the installation process is over.")
            msgBox.exec_()
            self.finished.emit()
            return

        # for directories copy the whole directory recursively
        if os.path.isdir(srcPath):
            dir_util.copy_tree(srcPath, dstPath)
        # for files create destination directory is necessary and copy the file
        elif os.path.isfile(srcPath):
            shutil.copy(srcPath, dstPath)
        else:
            msgBox = QtGui.QMessageBox()
            msgBox.setText("Cannot find the source directory!\n\n No files were copied.")
            msgBox.exec_()

        self.finished.emit()

    def unzipArchive(self, archivePath, dstPath):
        if not os.path.isfile(archivePath):
            msgBox = QtGui.QMessageBox()
            msgBox.setText("Could not find the archive!\n\n No files were extracted.")
            msgBox.exec_()
            self.finished.emit()
            return

        # checkWritePremissions also creates the directory if it doesn't exist yet
        if not self.checkWritePermissions(dstPath):
            msgBox = QtGui.QMessageBox()
            msgBox.setText("You do not have permissions to write to destination directory!\n\n No files were copied.\n\n"+
                           "Re-run the installer with administrator privileges or manually unzip files from "+archivePath+
                           " to "+dstPath+" after the installation process is over.")
            msgBox.exec_()
            self.finished.emit()
            return

        archive = ZipFile(archivePath)
        archive.extractall(dstPath)
        archive.close()
        self.finished.emit()

    def checkWritePermissions(self, dstPath):
        try:
            if not os.path.isdir(dstPath):
                os.makedirs(dstPath)
            fp = open(os.path.join(dstPath,"test"), 'w')
        except IOError as e:
            if e.errno == errno.EACCES:
                return False
            else:
                return False
        else:
            fp.close()
            try:
                os.remove(os.path.join(dstPath,"test"))
            except:
                pass
            return True

    def removeIncompatibleJavaOptions(self, batFilePath):
        # Make sure the snap batch file exists in the given directory
        if not os.path.isfile(batFilePath):
            msgBox = QtGui.QMessageBox()
            msgBox.setText("Could not find the batch file!\n\n Could not modify Java VM options.")
            msgBox.exec_()
            return

        # In the batch file remove the "-XX:+UseLoopPredicate" option which doesn't work with 32 bit installation.
        # First do this in a temp file and then copy the temp file to the correct dir
        tempFile = NamedTemporaryFile(delete=False)
        tempFilePath = tempFile.name
        tempFile.close()
        with open(tempFilePath, 'w') as outfile, open(batFilePath, 'r') as infile:
            for line in infile:
                line = re.sub(r"-XX:\+UseLoopPredicate ", "", line)
                outfile.write(line)
        tempDir = os.path.dirname(tempFilePath)
        if os.path.isfile(os.path.join(tempDir,"gpt.bat")):
            os.remove(os.path.join(tempDir,"gpt.bat"))
        os.rename(tempFilePath, os.path.join(tempDir,"gpt.bat"))
        shutil.copy(os.path.join(tempDir,"gpt.bat"), batFilePath)

    def setQGISSettings(self, name, value):
        self.qsettings.setValue(name, value)

    def activatePlugins(self):
        self.setQGISSettings("PythonPlugins/processing_workflow", "true")
        self.setQGISSettings("PythonPlugins/openlayers_plugin", "true")
        self.setQGISSettings("PythonPlugins/photo2shape", "true")
        self.setQGISSettings("PythonPlugins/pointsamplingtool", "true")
        self.setQGISSettings("PythonPlugins/processing", "true")
        self.setQGISSettings("PythonPlugins/temporalprofiletool", "true")
        self.setQGISSettings("PythonPlugins/valuetool", "true")
        self.setQGISSettings("plugins/zonalstatisticsplugin", "true")

    def activateProcessingProviders(self,osgeo4wDefaultDir):
        self.setQGISSettings("Processing/configuration/ACTIVATE_GRASS70", "false")
        self.setQGISSettings("Processing/configuration/ACTIVATE_GRASS", "true")
        self.setQGISSettings("Processing/configuration/ACTIVATE_MODEL", "true")
        self.setQGISSettings("Processing/configuration/ACTIVATE_OTB", "true")
        self.setQGISSettings("Processing/configuration/ACTIVATE_QGIS", "true")
        self.setQGISSettings("Processing/configuration/ACTIVATE_SAGA", "true")
        self.setQGISSettings("Processing/configuration/ACTIVATE_SCRIPT", "true")
        self.setQGISSettings("Processing/configuration/ACTIVATE_WORKFLOW", "true")
        self.setQGISSettings("Processing/configuration/GRASS_LOG_COMMANDS", "true")
        self.setQGISSettings("Processing/configuration/GRASS_LOG_CONSOLE", "true")
        self.setQGISSettings("Processing/configuration/SAGA_LOG_COMMANDS", "true")
        self.setQGISSettings("Processing/configuration/SAGA_LOG_CONSOLE", "true")
        self.setQGISSettings("Processing/configuration/USE_FILENAME_AS_LAYER_NAME", "true")
        # GRASS_FOLDER depends on GRASS version and is not updated automatically so it should
        # be set to the highest GRASS version present in the GRASS folder
        try:
            grassFolder = os.path.join(osgeo4wDefaultDir, 'apps', 'grass')
            grassFolder = os.path.join(grassFolder, next(os.walk(grassFolder))[1][-1])
            self.setQGISSettings("Processing/configuration/GRASS_FOLDER", grassFolder)
        except:
            pass

    def activateBEAMplugin(self, dirPath):
        self.setQGISSettings("PythonPlugins/processing_gpf", "true")
        self.setQGISSettings("Processing/configuration/ACTIVATE_BEAM", "true")
        self.setQGISSettings("Processing/configuration/BEAM_FOLDER", dirPath)

    def activateSNAPplugin(self, dirPath):
        self.setQGISSettings("PythonPlugins/processing_gpf", "true")
        self.setQGISSettings("Processing/configuration/ACTIVATE_SNAP", "true")
        self.setQGISSettings("Processing/configuration/SNAP_FOLDER", dirPath)

    def activateRplugin(self, dirPath, use64):
        self.setQGISSettings("Processing/configuration/ACTIVATE_R", "true")
        self.setQGISSettings("Processing/configuration/R_FOLDER", dirPath)
        self.setQGISSettings("Processing/configuration/R_USE64", use64)

    def activateSWATplugin(self, dirPath):
        self.setQGISSettings("PythonPlugins/processing_SWAT", "true")
        self.setQGISSettings("Processing/configuration/ACTIVATE_WG9HM", "true")
        self.setQGISSettings("Processing/configuration/MAPWINDOW_FOLDER", dirPath)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    installer = woisInstaller()
    # Fix to make sure that runInstaller is executed in the app event loop
    def _slot_installer():
        QtCore.SLOT(installer.runInstaller())
    QtCore.QTimer.singleShot(200, _slot_installer)
    app.exec_()


#!/usr/bin/env python3

import argparse
import logging
import logging.handlers
import json
import time
import os
import sys

from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QDialog, QStatusBar, QLabel, QFileDialog, QPushButton, QHBoxLayout
from PyQt5 import uic
from PyQt5 import QtCore, QtGui
from PIL import Image

from config import *
from constants import *
from steganography import *
from progressBar import *

# *******************************************
# Program history.
# 0.1   MDC 09/03/2021  Original.
# *******************************************

# *******************************************
# TODO List
#
# *******************************************

# Program version.
progVersion = "0.1"

# Program date (for About dialog).
progDate = "2021"

# Create configuration values class object.
config = Config('picCoder.json')

# *******************************************
# Create logger.
# Use rotating log files.
# *******************************************
logger = logging.getLogger('picCoder')
logger.setLevel(config.DebugLevel)
handler = logging.handlers.RotatingFileHandler('picCoder.log', maxBytes=config.LogFileSize, backupCount=config.LogBackups)
handler.setFormatter(logging.Formatter(fmt='%(asctime)s.%(msecs)03d [%(name)s] [%(levelname)-8s] %(message)s', datefmt='%Y%m%d-%H:%M:%S', style='%'))
logging.Formatter.converter = time.localtime
logger.addHandler(handler)

# Log program version.
logger.info(f'Program version : {progVersion}')

# *******************************************
# Determine resource path being the relative path to the resource file.
# The resource path changes when built for an executable.
# *******************************************
def res_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath('.')
    resPath = os.path.join(base_path, relative_path)
    return resPath

# *******************************************
# picCoder class
# *******************************************
class UI(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(UI, self).__init__()
        uic.loadUi(res_path("picCoder.ui"), self)

        # Set window icon.
        iconG = QtGui.QIcon()
        iconG.addPixmap(QtGui.QPixmap(res_path("./resources/about.png")), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.setWindowIcon(iconG)

        # Attach to the open (single file) menu item.
        self.actionOpenFile.triggered.connect(self.openFile)
        self.haveOpenPic = False

        # Attach to the save image menu item.
        self.actionSaveCodedImage.triggered.connect(self.saveFile)
        self.haveEmbededPic = False

        # Attach to the embed file menu item.
        self.actionEmbedFile.triggered.connect(self.embedFile)

        # Attach to the embed comment menu item.
        self.actionEmbedComment.triggered.connect(self.embedComment)

        # Attach to the Quit menu item.
        self.actionQuit.triggered.connect(app.quit)

        # Attach to the About menu item.
        self.actionAbout.triggered.connect(self.about)

        # Attach to the Change Log menu item.
        self.actionChangeLog.triggered.connect(self.changeLog)

        # Initial statusbar message.
        self.statusBar.showMessage("Initialising...", 2000)
        self.getFileBtn.clicked.connect(self.getEmbeddedFile)

        # Create progress bar for exports.
        self.progressBar = ProgressBar(config)
 
        # Setup menu items visibility.
        self.checkMenuItems()

        # Show appliction window.
        self.show()

    # *******************************************
    # Check state of menu items.
    # *******************************************
    def checkMenuItems(self):
        self.actionEmbedFile.setEnabled(self.haveOpenPic)
        self.actionEmbedComment.setEnabled(self.haveOpenPic)
        self.actionSaveCodedImage.setEnabled((self.haveOpenPic and self.haveEmbededPic))

    # *******************************************
    # Open File control selected.
    # Displays file browser to select a single pic.
    # *******************************************
    def openFile(self):
        logger.debug("User selected Open Image menu control.")

        # Configure and launch file selection dialog.
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Select PNG image file...")
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
        dialog.setFileMode(QFileDialog.ExistingFiles)
        dialog.setViewMode(QFileDialog.Detail)
        dialog.setNameFilters(["Picture files (*.png)"])

        # If have filename(s) then open.
        if dialog.exec_():
            filenames = dialog.selectedFiles()

            # If have a filename then open.
            if filenames[0] != "":
                logger.info(f'Selected picture file : {filenames[0]}')

                # Create picCoded image object.
                self.stegPic = Steganography(config, logger, self, filenames[0])

                # Displaying image statusbar message.
                self.statusBar.showMessage(f'Image file: {filenames[0]}...', 2000)
                self.picImageLbl.setPixmap(self.stegPic.bitmap.scaled(self.picImageLbl.width(), self.picImageLbl.height(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
                self.picImageLbl.adjustSize()
                self.picImageLbl.show()

                # Set the text associated with the label (according to whether it is encoded or not).
                fileDetails = filenames[0]
                if self.stegPic.picCoded == False:
                    # Hide the extract file button.
                    self.getFileBtn.hide()
                    self.picDetailsLbl.setStyleSheet(f'background-color: {config.PicRendering["PicCodedBgCol"]}; border: 3px solid {config.PicRendering["PicCodedBorderColDef"]};')
                else:
                    # Add details of embedded data.
                    if self.stegPic.picCodeType == CodeType.CODETYPE_FILE.value:
                        fileDetails += (f'\nImage contains embedded file : {self.stegPic.embeddedFileName}')
                        # Show the button to extract the embedded file.
                        self.getFileBtn.show()
                        self.getFileBtn.setText("Extract Embedded File")
                        self.getFileBtn.setStyleSheet(f'background-color: {config.PicRendering["PicCodedButton"]};')
                    # Put special border around the picCoded image filename.
                    self.picDetailsLbl.setStyleSheet(f'background-color: {config.PicRendering["PicCodedBgCol"]}; border: 3px solid {config.PicRendering["PicCodedBorderColCoded"]};')

                # Set flag to indicate we have an open pic to play with.
                self.haveOpenPic = True

                # Update image file details label.
                self.picDetailsLbl.setText(f'{fileDetails}')

                # Update menu item visibility.
                self.checkMenuItems()

            else:
                logger.debug("No picture files selected.")

    # *******************************************
    # Embed File control selected.
    # Displays file browser to select a file to embed into the current pic.
    # *******************************************
    def embedFile(self):
        logger.debug("User selected Embed File menu control.")

        # Configure and launch file selection dialog.
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Select file to embed into image...")
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
        dialog.setFileMode(QFileDialog.ExistingFiles)
        dialog.setViewMode(QFileDialog.Detail)
        dialog.setNameFilters(["Any file (*.*)"])

        # If have filename(s) then open.
        if dialog.exec_():
            filenames = dialog.selectedFiles()

            # If have a filename then open.
            if filenames[0] != "":
                logger.info(f'Selected file to embed : {filenames[0]}')

                # Need to do a quick check of gile size, as might not fit or look right.
                # Size of file to embed.
                fileSize = os.path.getsize(filenames[0])
                # PicCoder overhead size
                extraInfo = len(PROGCODE) + CODETYPEBYTES + NAMELENBYTES + len(filenames[0]) + LENBYTES
                # Maximum space availablefrom PIL import Image for embedding.
                maxSpace = self.stegPic.picBytes
                embedRatio = fileSize / maxSpace
                # Warning if file to embed is more than a certain ratio.
                if embedRatio > config.MaxEmbedRatio:
                    logger.warning(f'File to embed exceeds maximum ratio : {embedRatio:.3f}')
                else:
                    # Proceed to embedding file into image.
                    self.stegPic.toEmbedFilePath = filenames[0]
                    self.stegPic.toEmbedFileSize = fileSize
                    self.stegPic.embedFileToImage()

                    # Set flag for image save control.
                    self.haveEmbededPic = True

        # Update menu item visibility.
        self.checkMenuItems()

    # *******************************************
    # Embed Comment control selected.
    # Start comment thread or add to comment thread.
    # *******************************************
    def embedComment(self):
        logger.debug("User selected Embed Comment menu control.")

    # *******************************************
    # Save File control selected.
    # Displays file browser to safe current (embedded) pic.
    # *******************************************
    def saveFile(self):
        logger.debug("User selected Save Image menu control.")
        self.stegPic.image.save('rat.png', 'PNG')

    # *******************************************
    # Calback for extract embedded file button.
    # *******************************************
    def getEmbeddedFile(self):
        logger.debug("User selected control to extract embedded file.")

        # Get filename parts.
        fnParts = os.path.splitext(self.stegPic.embeddedFileName)

        # Configure and launch file selection dialog.
        dialog = QFileDialog(self, directory = self.stegPic.embeddedFileName)
        dialog.setWindowTitle("Select file to save embedded file to...")
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setNameFilter(fnParts[1])
        dialog.setDefaultSuffix(fnParts[1])
        dialog.setViewMode(QFileDialog.List)
        dialog.setAcceptMode(QFileDialog.AcceptSave)

        # If returned filename then open/create.
        if dialog.exec_():
            filenames = dialog.selectedFiles()

            # If have a filename then open.
            if filenames[0] != "":
                logger.info(f'Selected file to save to : {filenames[0]}')

                # Call method to extract embedded file.
                self.stegPic.saveEmbeddedFile(filenames[0])

                # If the image is a picture we can display it as well.
                eObj = Image.open(filenames[0])
                try:
                    imgType = eObj.format
                    logger.debug(f'Embedded file is image type : {imgType}')
                    # Launch dialog box to show the embedded inage.
                    self.showDisplayedImage(filenames[0])
                except:
                    logger.debug("Embedded file is not an image file.")

    # *******************************************
    # About control selected.
    # Displays an "About" dialog box.
    # *******************************************
    def about(self):
        logger.debug("User selected About menu control.")

        # Create about dialog.        
        AboutDialog(progVersion, progDate)

    # *******************************************
    # Change Log control selected.
    # Displays a "Change Log" dialog box.
    # *******************************************
    def changeLog(self):
        logger.debug("User selected Change Log menu control.")

        # Create about dialog.        
        ChangeLogDialog()

    # *******************************************
    # Displaying embedded image dialog.
    # *******************************************
    def showDisplayedImage(self, imgFile):
        logger.debug(f'Displaying embedded image : {imgFile}')

        # Create embedded image dialog.        
        EmbeddedImageDialog(imgFile)

# *******************************************
# Embedded image dialog class.
# *******************************************
class EmbeddedImageDialog(QDialog):
    def __init__(self, imgFile, parent=None):
        super(EmbeddedImageDialog, self).__init__()
        uic.loadUi(res_path("embeddedPic.ui"), self)

        # Show the change log.
        self.showEmbeddedImage(imgFile)

    # *******************************************
    # Displays embedded image in dialog box.
    # *******************************************
    def showEmbeddedImage(self, imgFile):

        # Set dialog window icon.
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(res_path("./resources/about.png")))
        self.setWindowIcon(icon)

        # Create bitmap for display.
        bitmap = QtGui.QPixmap(imgFile)
        picWidth = bitmap.width()
        picHeight = bitmap.height()

        # Display bitmap.
        self.pictureLbl.setPixmap(bitmap.scaled(picWidth, picHeight, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        self.pictureLbl.adjustSize()
        self.pictureLbl.show()
        # Update image file details label.
        self.pictureNameLbl.setText(f'{imgFile}')

        # Show dialog.
        self.exec_()

# *******************************************
# About dialog class.
# *******************************************
class AboutDialog(QDialog):
    def __init__(self, version, aboutDate):
        super(AboutDialog, self).__init__()
        uic.loadUi(res_path("about.ui"), self)

        self.showAbout(version, aboutDate)

    # *******************************************
    # Displays an "About" dialog box.
    # *******************************************
    def showAbout(self, version, aboutDate):
        # Set dialog window icon.
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(res_path("./resources/about.png")))
        self.setWindowIcon(icon)

        # Update version information.
        self.versionLbl.setText("Version : {0:s}".format(version))

        # Update program date information.
        self.dateLbl.setText("(MDC : {0:s})".format(aboutDate))

        # Update dialog icon.
        self.aboutIcon.setPixmap(QtGui.QPixmap(res_path("./resources/about.png")))

        # Show dialog.
        self.exec_()

# *******************************************
# Change Log dialog class.
# *******************************************
class ChangeLogDialog(QDialog):
    def __init__(self):
        super(ChangeLogDialog, self).__init__()
        uic.loadUi(res_path("changeLog.ui"), self)

        # Show the change log.
        self.showChangeLog()

    # *******************************************
    # Displays a "Change Log" dialog box.
    # *******************************************
    def showChangeLog(self):

        # Set dialog window icon.
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(res_path("./resources/about.png")))
        self.setWindowIcon(icon)

        # Update change log.
        self.changeLogText.textCursor().insertHtml("<h1><b>CHANGE LOG</b></h1><br>")
        self.changeLogText.textCursor().insertHtml("<h2><b>Version 0.1</b></h2>")
        self.changeLogText.textCursor().insertHtml("<ul>" \
            "<li>Initial draft release.</li>" \
            "</ul>")

        # Scroll to top so that changes for most recent version are visible.
        self.changeLogText.moveCursor(QtGui.QTextCursor.Start)
        self.changeLogText.ensureCursorVisible()

        # Show dialog.
        self.exec_()

# *******************************************
app = QApplication(sys.argv)
picCoder = UI()
app.exec_()
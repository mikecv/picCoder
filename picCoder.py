#!/usr/bin/env python3

import argparse
import logging
import logging.handlers
import json
import datetime
import time
import os
import sys

from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QDialog, QStatusBar, QLabel, QFileDialog, QPushButton, QHBoxLayout, QVBoxLayout, QMessageBox
from PyQt5 import uic
from PyQt5 import QtCore, QtGui, QtWidgets
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
# Display image with embedded file in separate window so that you can see what it looks like before saving.
# Add support for embedded text messaging.
# Add message entry to conversation dialog; currently messages are hardcoded when created (testing).
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
        self.picDetailsLbl.setHidden(True)
        self.getEmbeddedDataBtn.setHidden(True)

        # Attach to the save image menu item.
        self.actionSaveCodedImage.triggered.connect(self.saveFile)
        self.haveEmbededPic = False

        # Attach to the embed file menu item.
        self.actionEmbedFile.triggered.connect(self.embedFile)

        # Attach to the start conversation menu item.
        self.actionStartConversation.triggered.connect(self.startConversation)

        # Attach to the Quit menu item.
        self.actionQuit.triggered.connect(app.quit)

        # Attach to the About menu item.
        self.actionAbout.triggered.connect(self.about)

        # Attach to the Change Log menu item.
        self.actionChangeLog.triggered.connect(self.changeLog)

        # Initial statusbar message.
        self.statusBar.showMessage("Initialising...", 2000)

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
        self.actionStartConversation.setEnabled(self.haveOpenPic)
        self.actionSaveCodedImage.setEnabled((self.haveOpenPic and self.haveEmbededPic))
        self.picDetailsLbl.setHidden(not self.haveOpenPic)

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
                    self.picDetailsLbl.setStyleSheet(f'background-color: {config.PicRendering["PicCodedBgCol"]}; border: 3px solid {config.PicRendering["PicCodedBorderColDef"]};')
                    self.getEmbeddedDataBtn.hide()
                else:
                    # Add details of embedded data.
                    if self.stegPic.picCodeType == CodeType.CODETYPE_FILE.value:
                        fileDetails += (f'\nImage contains embedded file : {self.stegPic.embeddedFileName}')
                        # Show the button to extract the embedded file.
                        self.getEmbeddedDataBtn.setText("Extract Embedded File")
                        self.getEmbeddedDataBtn.setStyleSheet(f'background-color: {config.PicRendering["PicCodedButton"]};')
                        self.getEmbeddedDataBtn.show()
                        # Attach callback to get embedded file button.
                        # Need to disconnect first in case already connected to previous image.
                        try:
                            self.getEmbeddedDataBtn.clicked.disconnect()
                        except TypeError:
                            pass
                        self.getEmbeddedDataBtn.clicked.connect(self.getEmbeddedFile)
                    elif self.stegPic.picCodeType == CodeType.CODETYPE_TEXT.value:
                        fileDetails += (f'\nImage contains embedded conversation.')
                        # Show the button to extract the embedded file.
                        self.getEmbeddedDataBtn.setText("Open Embedded Conversation")
                        self.getEmbeddedDataBtn.setStyleSheet(f'background-color: {config.PicRendering["PicCodedButton"]};')
                        self.getEmbeddedDataBtn.show()
                        # Attach callback to open the embedded conversation button.
                        # Need to disconnect first in case already connected to previous image.
                        try:
                            self.getEmbeddedDataBtn.clicked.disconnect()
                        except TypeError:
                            pass
                        self.getEmbeddedDataBtn.clicked.connect(self.openEmbeddedConversation)
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

                # Need to do a quick check of file size, as might not fit or look right.
                # Size of file to embed.
                fileSize = os.path.getsize(filenames[0])
                logger.info(f'Selected file to embed has filesize : {fileSize}')
                # PicCoder embeded data size.
                extraInfo = len(PROGCODE) + CODETYPEBYTES + NAMELENBYTES + len(filenames[0]) + LENBYTES
                # Maximum space available from PIL import Image for embedding.
                maxSpace = self.stegPic.picBytes
                embedRatio = (fileSize + extraInfo) / maxSpace
                # Warning if file to embed is more than a certain ratio.
                if embedRatio > config.MaxEmbedRatio:
                    logger.warning(f'Data to embed exceeds maximum ratio : {embedRatio:.3f}')
                    showPopup("Warning", "picCoder Embedding File", "File to embed would exceed allowed embedding ratio.")
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
    # Start conversation control selected.
    # *******************************************
    def startConversation(self):
        logger.debug("User selected start conversation menu control.")

        self.newConversation = Conversation()

        # Temporary messages for testing.
        self.newConversation.addMsg(config.MyHandle, "This is a starting conversation message.", "29-05-2021 12:57:31")
        self.newConversation.addMsg("Bill", "This is Bill's message.", "29-05-2021 12:58:12")
        self.newConversation.addMsg("Bill", "This is a second of Bill's message at the same time.", "29-05-2021 12:58:23")
        self.newConversation.addMsg("Bill", "Believe it or not Bill is at it again.", "29-05-2021 12:59:14")
        self.newConversation.addMsg(config.MyHandle, "Another message from me at the same time.", "30-05-2021 07:26:12")
        self.newConversation.addMsg(config.MyHandle, "Another message from me but at a much later time.", "30-05-2021 07:26:20")
        self.newConversation.addMsg(config.MyHandle, "Another message from me but at a much later time.")
        self.newConversation.addMsg("Berty Beetle", "Who is this new guy sending a message?\nHaven't heard from him before.")

        ConversationDialog(self.newConversation)

        # Set flag for image save control.
        self.haveConversation = True

        # Update menu item visibility.
        self.checkMenuItems()

    # *******************************************
    # Embed Conversation control selected.
    # Embeds current conversation into the current pic.
    # *******************************************
    def embedConversation(self):
        logger.debug("User selected Embed Conversation menu control.")

        # # Need to do a quick check of conversation size, as might not fit or look right.
        # # Size of conversation to embed.
        # convLength = 0
        # for msg in self.newConversation.messages:
        #     convLength += NUMSMSBYTES
        #     convLength += NAMELENBYTES
        #     convLength += len(msg.writer)
        #     convLength += TIMELENBYTES
        #     convLength += len(msg.msgTime)
        #     convLength += SMSLENBYTES
        #     convLength += len(msg.msgText)

        # # PicCoder embeded data size.
        # embedData = len(PROGCODE) + CODETYPEBYTES + NUMSMSBYTES + convLength
        # # Maximum space available from PIL import Image for embedding.
        # maxSpace = self.stegPic.picBytes
        # embedRatio = embedData / maxSpace
        # # Warning if embedded data to embed is more than a certain ratio.
        # if embedRatio > config.MaxEmbedRatio:
        #     logger.warning(f'Data to embed exceeds maximum ratio : {embedRatio:.3f}')
        #     showPopup("Warning", "picCoder Embedding Conversation", "Conversation to embed would exceed allowed embedding ratio.")
        # else:
        #     # Embed conversation.
        #     logger.debug(f'Embedding conversion.')
        #     self.stegPic.embedConversationIntoImage(self.newConversation)

    # *******************************************
    # Save File control selected.
    # Displays file browser to safe current (embedded) pic.
    # *******************************************
    def saveFile(self):
        logger.debug("User selected Save Image menu control.")

        # Configure and launch file selection dialog.
        dialog = QFileDialog(self, directory = self.stegPic.embeddedFileName)
        dialog.setWindowTitle("Select file to save picCoded image to...")
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setViewMode(QFileDialog.List)
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setNameFilters(["Picture files (*.png)"])

        # If returned filename then open/create.
        if dialog.exec_():
            filenames = dialog.selectedFiles()

            # If have a filename then open.
            if filenames[0] != "":
                logger.info(f'Selected file to save to : {filenames[0]}')

                try:
                    self.stegPic.image.save(filenames[0], 'PNG')
                except:
                    logger.error("Failed to save picCoded image to file.")

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
        dialog.setNameFilters([f'{fnParts[1][1:]} files (*{fnParts[1]})'])
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
                try:
                    eObj = Image.open(filenames[0])
                    imgType = eObj.format
                    logger.debug(f'Embedded file is image type : {imgType}')
                    # Launch dialog box to show the embedded inage.
                    self.showDisplayedImage(filenames[0])
                except:
                    logger.info("Embedded file is not an image file.")
                    showPopup("Info", "picCoder File Extraction", "Embedded file saved.\nEmbedded file is not an image, open with associated application.")

    # *******************************************
    # Calback for open embedded conversation button.
    # *******************************************
    def openEmbeddedConversation(self):
        logger.debug("User selected control to opem embedded conversation.")

        # Show the conversation dialog.
        ConversationDialog(self.stegPic.conversation)

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

        # Display bitmap.
        self.pictureLbl.setPixmap(bitmap.scaled(self.pictureLbl.width(), self.pictureLbl.height(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        self.pictureLbl.adjustSize()
        self.pictureLbl.show()
        # Update image file details label.
        self.pictureNameLbl.setText(f'{imgFile}')

        # Show dialog.
        self.exec_()

# *******************************************
# Conversation dialog class.
# *******************************************
class ConversationDialog(QDialog):
    def __init__(self, smsConv, parent=None):
        super(ConversationDialog, self).__init__()
        uic.loadUi(res_path("messenger.ui"), self)

        # Show the change log.
        self.showConversation(smsConv)

    # *******************************************
    # Displays embedded image in dialog box.
    # *******************************************
    def showConversation(self, conv):

        # Set dialog window icon.
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(res_path("./resources/about.png")))
        self.setWindowIcon(icon)

        numSMSes = conv.numMessages()
        for idx, msg in enumerate(conv.messages):

            # Flag to include write and timestamp.
            incWriter = True

            # Group messages using cornered outlines if messages from the same writer are within a certain time.
            # Get time and writer of this message.
            thisTime = datetime.datetime.strptime(msg.msgTime, "%d-%m-%Y %H:%M:%S")
            thisWriter = msg.writer
            # Get time and writer of next message.
            if (idx != (numSMSes - 1)):
                nextWriter = conv.messages[idx + 1].writer
                nextTime = datetime.datetime.strptime(conv.messages[idx + 1].msgTime, "%d-%m-%Y %H:%M:%S")

            # Top of top message is rounded.
            if idx == 0:
                topRadius = config.SmsRender["BubbleRadius"]
            else:
                # If message is by same writer AND within certain time of previous message the top is not rounded.
                if (thisWriter == prevWriter) and ((thisTime - prevTime).total_seconds() < config.SmsRender["SameMsgTime"]):
                    topRadius = 0
                    incWriter = False
                # Else top is rounded.
                else:
                    topRadius = config.SmsRender["BubbleRadius"]
            # Bottom of bottom message is rounded.
            if idx == (numSMSes - 1):
                botRadius = config.SmsRender["BubbleRadius"]
            else:
                # If message is by same writer AND within certain time of next message the not rounded.
                if (msg.writer == nextWriter) and ((nextTime - thisTime).total_seconds() < config.SmsRender["SameMsgTime"]):
                    botRadius = 0
                else:
                    botRadius = config.SmsRender["BubbleRadius"]

            # Update time and writer of previous message.
            prevTime = thisTime
            prevWriter = thisWriter

            hBox = QHBoxLayout()

            # If there are newline characters in the text string they won't be rendered in the conversation messages
            # which use html format. Need to replace newlines with break tokens.
            messageText = "<br>".join(msg.msgText.split("\n"))

            if incWriter == True:
                lbl = QLabel(f'<b>{msg.writer} : {msg.msgTime}</b><br><br>{messageText}', self)
            else:
                lbl = QLabel(f'{messageText}', self)

            # Set label with and wordwrapping, and restrict expanding to vertical only.
            lbl.setFixedWidth(config.SmsRender["TextWidth"])
            lbl.setWordWrap(True)
            lbl.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.MinimumExpanding)

            # Add label to horizontal layout.
            # Pad out so my messages on the right, others on the left.
            if msg.writer == config.MyHandle:
                hBox.addStretch()
                lbl.setStyleSheet(f'border : 3px solid {config.SmsRender["MeSMSBorderCol"]}; background : {config.SmsRender["MeSMSBkGrndCol"]}; padding :10px;'
                            f'border-top-left-radius : {topRadius}px;'
                            f'border-top-right-radius : {topRadius}px;'
                            f'border-bottom-left-radius : {botRadius}px;'
                            f'border-bottom-right-radius : {botRadius}px'
                        )
                hBox.addWidget(lbl)
            else:
                lbl.setStyleSheet(f'border : 3px solid {config.SmsRender["ThemSMSBorderCol"]}; background : {config.SmsRender["ThemSMSBkGrndCol"]}; padding :10px;'
                            f'border-top-left-radius : {topRadius}px;'
                            f'border-top-right-radius : {topRadius}px;'
                            f'border-bottom-left-radius : {botRadius}px;'
                            f'border-bottom-right-radius : {botRadius}px'
                        )
                hBox.addWidget(lbl)
                hBox.addStretch()

            # Add horizontal layout containing the label to vertical layout.
            self.verticalLayout.addLayout(hBox)
        # Add a stretch widget at the bottom to consume space.
        self.verticalLayout.addStretch()

        # Couple scroll area to layout contents.
        self.scrollAreaWidgetContents.setLayout(self.verticalLayout)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

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
# Pop-up message box.
# *******************************************
def showPopup(puType, title, msg, info="", details=""):

    # Create pop-up message box.
    # Mandatory title and message.
    # Optional information and details.
    mb = QMessageBox()
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap(res_path("./resources/about.png")))
    mb.setWindowIcon(icon)
    if (puType == "Info"):
        mb.setIcon(QMessageBox.Information)
    elif (puType == "Warning"):
        mb.setIcon(QMessageBox.Warning)
    mb.setText(msg)
    if (info != ""):
        mb.setInformativeText(info)
    mb.setWindowTitle(title)
    if (details != ""):
        mb.setDetailedText(details)

    # Show message box.
    mb.exec_()

# *******************************************
app = QApplication(sys.argv)
picCoder = UI()
app.exec_()
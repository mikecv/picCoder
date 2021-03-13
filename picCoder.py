#!/usr/bin/env python3

import argparse
import logging
import logging.handlers
import json
import time
import os
import sys

from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog
# from PyQt5.QtWidgets import  QFileDialog, QColorDialog, QLabel, QPushButton, QMessageBox, qApp
from PyQt5 import uic
from PyQt5 import QtCore, QtGui

from config import *

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
logger.info("Program version : {0:s}".format(progVersion))

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

        # Attach to the Quit menu item.
        self.actionQuit.triggered.connect(app.quit)

        # Attach to the About menu item.
        self.actionAbout.triggered.connect(self.about)

        # Show appliction window.
        self.show()

        # Attach to the Change Log menu item.
        self.actionChangeLog.triggered.connect(self.changeLog)

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
# Create UI
# *******************************************
app = QApplication(sys.argv)
picCoder = UI()
app.exec_()
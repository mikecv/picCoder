#!/usr/bin/env python3

from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5 import uic
from PyQt5 import QtCore, QtGui
import os

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
# Progress bar class. 
# *******************************************
class ProgressBar(QDialog):
    # Constructor
    def __init__(self, config):
        super(ProgressBar, self).__init__()

        # Set up the progress bar dialog.
        uic.loadUi("progressBar.ui", self)

        # Initialise progress bar.
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)

    # *******************************************
    # Method to set note in progress bar.
    # *******************************************
    def setNote(self, note):
        # Process events to make progress bar responsive.
        QApplication.processEvents()
        self.progBarNote.setText(note)
        self.show()

    # *******************************************
    # Method to set progress in the progress bar.
    # *******************************************
    def setProgress(self, progress):
        # Process events to make progress bar responsive.
        QApplication.processEvents()
        self.progressBar.setValue(progress)
        self.show()

    # *******************************************
    # Displays the progress bar.
    # *******************************************
    def showProgressBar(self):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(res_path("./resources/about.png")))
        self.setWindowIcon(icon)

        # Show dialog.
        self.show()

    # *******************************************
    # Hide the progress bar.
    # *******************************************
    def hideProgressBar(self):
        self.done(0)

#!/usr/bin/env python3

from PyQt5.QtWidgets import QDialog
from PyQt5 import uic
from PyQt5 import QtCore, QtGui
import os
import sys

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
# Embedded image dialog class.
# *******************************************
class EmbeddedImageDialog(QDialog):
    def __init__(self, imgFile, parent=None):
        super(EmbeddedImageDialog, self).__init__()
        uic.loadUi(res_path("embeddedPic.ui"), self)

        # Show the embedded image.
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

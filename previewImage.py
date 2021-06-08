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
# Preview image dialog class.
# Displays preview of embedded image.
# *******************************************
class PreviewImageDialog(QDialog):
    def __init__(self, picImage, parent=None):
        super(PreviewImageDialog, self).__init__()
        uic.loadUi(res_path("picPreview.ui"), self)

        # Show the embedded image.
        self.showImagePreview(picImage)

    # *******************************************
    # Displays preview of image with embedded data in dialog box.
    # This is so that user can preview before deciding to save.
    # *******************************************
    def showImagePreview(self, picImage):

        # Set dialog window icon.
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(res_path("./resources/about.png")))
        self.setWindowIcon(icon)

        # Create bitmap for display.
        bitmap = QtGui.QPixmap.fromImage(picImage)

        # Display bitmap.
        self.pictureLbl.setPixmap(bitmap.scaled(self.pictureLbl.width(), self.pictureLbl.height(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        self.pictureLbl.adjustSize()
        self.pictureLbl.show()

        # Show dialog.
        self.exec_()

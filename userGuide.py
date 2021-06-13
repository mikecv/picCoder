#!/usr/bin/env python3

from PyQt5.QtWidgets import QDialog
from PyQt5 import QtCore, uic
from PyQt5 import QtGui
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
# User Guide dialog class.
# *******************************************
class UserGuideDialog(QDialog):
    def __init__(self):
        super(UserGuideDialog, self).__init__()
        uic.loadUi(res_path("userGuide.ui"), self)

        # Set dialog window icon.
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(res_path("./resources/about.png")))
        self.setWindowIcon(icon)

        # Display the User Guide file.
        self.helpBrowser.setSource(QtCore.QUrl.fromLocalFile(res_path("./resources/userGuide.html")))

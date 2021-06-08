#!/usr/bin/env python3

from PyQt5.QtWidgets import QDialog
from PyQt5 import uic
from PyQt5 import QtGui, QtWidgets
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
# Password Entry dialog class.
# *******************************************
class PasswordDialog(QDialog):
    def __init__(self):
        super(PasswordDialog, self).__init__()
        uic.loadUi(res_path("password.ui"), self)

        # Set dialog window icon.
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(res_path("./resources/about.png")))
        self.setWindowIcon(icon)

        # Obfuscate password
        self.passwordEntry.setEchoMode(QtWidgets.QLineEdit.Password)

        # Connect to dialog buttons.
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    # *******************************************
    # Get users password entry.
    # *******************************************
    def getPassword(self):

        # If user selecs accepts entry, then return.
        if self.exec_() == QDialog.Accepted:
            # Get password.
            ok = True
            password = self.passwordEntry.text()
            return ok, password
        # Every other entry is concerned not accepting entry.
        else:
            # Clear password.
            self.passwordEntry.clear()
            ok = False
            password = ""
            return ok, password

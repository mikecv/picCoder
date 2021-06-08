#!/usr/bin/env python3

from PyQt5.QtWidgets import QMessageBox
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
# Pop-up message box.
# *******************************************
def showPopup(puType, title, msg, info="", details=""):

    # *******************************************
    # Create pop-up message box.
    # Mandatory title and message.
    # Optional information and details.
    # *******************************************

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

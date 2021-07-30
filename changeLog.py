#!/usr/bin/env python3

from PyQt5.QtWidgets import QDialog
from PyQt5 import uic
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
# Change Log dialog class.
# *******************************************
class ChangeLogDialog(QDialog):
    def __init__(self):
        super(ChangeLogDialog, self).__init__()
        uic.loadUi(res_path("changeLog.ui"), self)

        # Set dialog window icon.
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(res_path("./resources/about.png")))
        self.setWindowIcon(icon)

        # Update change log.
        self.changeLogText.textCursor().insertHtml("<h1><b>CHANGE LOG</b></h1><br>")
        self.changeLogText.textCursor().insertHtml("<h2><b>Version 0.3</b></h2>")
        self.changeLogText.textCursor().insertHtml("<ul>" \
            "<li>Made size of conversation text configurable. Configuration version up to 2.</li>" \
            "<li>Fixed dialog names.</li>" \
            "<li>Fixed bug with export of conversation with non-Unicode text.</li>" \
            "<li>Added approximate embedding capacity for image to status bar.</li>" \
            "</ul><br>")
        self.changeLogText.textCursor().insertHtml("<h2><b>Version 0.2</b></h2>")
        self.changeLogText.textCursor().insertHtml("<ul>" \
            "<li>Changed message edit box to be plain text.</li>" \
            "<li>Added some support for message text in other than Unicode text.</li>" \
            "<li>Changed blank user handle to \"Unknown\" and then notified user to change configuration.</li>" \
            "<li>Reworked exporting of conversation and added description to User Guide.</li>" \
            "</ul><br>")
        self.changeLogText.textCursor().insertHtml("<h2><b>Version 0.1</b></h2>")
        self.changeLogText.textCursor().insertHtml("<ul>" \
            "<li>Initial draft release.</li>" \
            "</ul>")

        # Scroll to top so that changes for most recent version are visible.
        self.changeLogText.moveCursor(QtGui.QTextCursor.Start)
        self.changeLogText.ensureCursorVisible()

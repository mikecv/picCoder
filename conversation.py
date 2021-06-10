#!/usr/bin/env python3

from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLabel
from PyQt5 import uic
from PyQt5 import QtGui, QtWidgets
import datetime
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
# Conversation dialog class.
# *******************************************
class ConversationDialog(QDialog):
    def __init__(self, logger, config, conversation):
        super(ConversationDialog, self).__init__()
        uic.loadUi(res_path("messenger.ui"), self)

        # Initialise application logger and config.
        self.logger = logger
        self.config = config

        # Initialise class conversation object.
        self.conversation = conversation

        # Set dialog window icon.
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(res_path("./resources/about.png")))
        self.setWindowIcon(icon)

        # Set conversation dialog icons.
        iconS = QtGui.QIcon()
        iconS.addPixmap(QtGui.QPixmap(res_path("./resources/send.png")))
        self.sendButton.setIcon(iconS)
        iconC = QtGui.QIcon()
        iconC.addPixmap(QtGui.QPixmap(res_path("./resources/clear.png")))
        self.clearButton.setIcon(iconC)

        # Connect callbacks to message buttons.
        self.sendButton.setEnabled(True)
        self.sendButton.clicked.connect(self.sendClicked)
        self.clearButton.setEnabled(True)
        self.clearButton.clicked.connect(self.clearClicked)

        # Couple scroll area to layout contents.
        self.scrollAreaWidgetContents.setLayout(self.verticalLayout)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

    # *******************************************
    # Populate messages in conversation.
    # *******************************************
    def populateMessages(self):

        # Clear the dialog.
        self.clearConversationLayout()

        # Populate messages in the layout.
        numSMSes = self.conversation.numMessages()
        self.logger.debug(f'Populating conversation with messages : {numSMSes}')

        # Add a stretch widget at the top to consume space and push messages to the bottom.
        self.verticalLayout.addStretch()

        # Loop through messages.
        for idx, msg in enumerate(self.conversation.messages):

            # Flag to include write and timestamp.
            incWriter = True

            # Group messages using cornered outlines if messages from the same writer are within a certain time.
            # Get time and writer of this message.
            thisTime = datetime.datetime.strptime(msg.msgTime, "%d-%m-%Y %H:%M:%S")
            thisWriter = msg.writer
            # Get time and writer of next message.
            if (idx != (numSMSes - 1)):
                nextWriter = self.conversation.messages[idx + 1].writer
                nextTime = datetime.datetime.strptime(self.conversation.messages[idx + 1].msgTime, "%d-%m-%Y %H:%M:%S")

            # Top of top message is rounded.
            if idx == 0:
                topRadius = self.config.SmsRender["BubbleRadius"]
            else:
                # If message is by same writer AND within certain time of previous message the top is not rounded.
                if (thisWriter == prevWriter) and ((thisTime - prevTime).total_seconds() < self.config.SmsRender["SameMsgTime"]):
                    topRadius = 0
                    incWriter = False
                # Else top is rounded.
                else:
                    topRadius = self.config.SmsRender["BubbleRadius"]
            # Bottom of bottom message is rounded.
            if idx == (numSMSes - 1):
                botRadius = self.config.SmsRender["BubbleRadius"]
            else:
                # If message is by same writer AND within certain time of next message the not rounded.
                if (msg.writer == nextWriter) and ((nextTime - thisTime).total_seconds() < self.config.SmsRender["SameMsgTime"]):
                    botRadius = 0
                else:
                    botRadius = self.config.SmsRender["BubbleRadius"]

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
            lbl.setFixedWidth(self.config.SmsRender["TextWidth"])
            lbl.setWordWrap(True)
            lbl.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.MinimumExpanding)

            # Add label to horizontal layout.
            # Pad out so my messages on the right, others on the left.
            if msg.writer == self.config.MyHandle:
                hBox.addStretch()
                lbl.setStyleSheet(f'border : 3px solid {self.config.SmsRender["MeSMSBorderCol"]}; background : {self.config.SmsRender["MeSMSBkGrndCol"]}; padding :10px;'
                            f'border-top-left-radius : {topRadius}px;'
                            f'border-top-right-radius : {topRadius}px;'
                            f'border-bottom-left-radius : {botRadius}px;'
                            f'border-bottom-right-radius : {botRadius}px'
                        )
                hBox.addWidget(lbl)
            else:
                lbl.setStyleSheet(f'border : 3px solid {self.config.SmsRender["ThemSMSBorderCol"]}; background : {self.config.SmsRender["ThemSMSBkGrndCol"]}; padding :10px;'
                            f'border-top-left-radius : {topRadius}px;'
                            f'border-top-right-radius : {topRadius}px;'
                            f'border-bottom-left-radius : {botRadius}px;'
                            f'border-bottom-right-radius : {botRadius}px'
                        )
                hBox.addWidget(lbl)
                hBox.addStretch()
            
            # Add horizontal layout containing the label to vertical layout.
            self.verticalLayout.addLayout(hBox)

        # Scroll to the bottom of the scroll area.
        self.scrollArea.verticalScrollBar().rangeChanged.connect(lambda: self.scrollArea.verticalScrollBar().setValue(self.scrollArea.verticalScrollBar().maximum()))

    # *******************************************
    # Clear coversation dialog of messages.
    # *******************************************
    def clearConversationLayout(self):

        self.logger.debug("Clearing conversation dialog of messages...")

        # Iterate through conversation layout and delete.
        # Deletes layouts and spacers that make up each message bubble.
        # Delete the message labels themselves.
        for i in reversed(range(self.verticalLayout.count())):
            item = self.verticalLayout.itemAt(i)
            if type(item) == QtWidgets.QHBoxLayout:
                for j in reversed(range(item.count())):
                    subItem = item.itemAt(j)
                    if type(subItem) == QtWidgets.QWidgetItem:
                        subItem.widget().setParent(None)
                    elif type(subItem) == QtWidgets.QSpacerItem:
                        item.layout().removeItem(subItem)
                self.verticalLayout.removeItem(item)

    # *******************************************
    # User clicked to send new message.
    # This adds the edit message to the conversation.
    # *******************************************
    def sendClicked(self):

        self.logger.debug("User selected send message control.")

        # Read contents of text edit box and add as new message to conversation.
        if self.messageEdit.toPlainText() != "":
            self.conversation.addMsg(self.config.MyHandle, self.messageEdit.toPlainText())

        # Repopulate conversation, now with additional message.
        self.populateMessages()

        # Clear the contents of the text edit box.
        self.messageEdit.clear()

    # *******************************************
    # User clicked to clear message.
    # This clears the edit message.
    # *******************************************
    def clearClicked(self):

        self.logger.debug("User selected clear message control.")

        # Clear the contents of the text edit box.
        self.messageEdit.clear()

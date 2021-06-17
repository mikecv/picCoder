#!/usr/bin/env python3

from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLabel
from PyQt5 import uic
from PyQt5 import QtCore, QtGui, QtWidgets
import datetime
import os
import sys
import random

from popup import *

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

        # Writer (handle) colours for rendering.
        self.handleColour = []

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

        # Get random colour for each different writer.
        self.updateWriterColours()

        # Add a stretch widget at the top to consume space and push messages to the bottom.
        self.verticalLayout.addStretch()

        # Loop through messages.
        for idx, msg in enumerate(self.conversation.messages):

            # Get the message bubble colours for this writer.
            borderCol, fillCol = self.getWriterColours(msg.writer)

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
                # If this message is by same writer AND within certain time of previous message the top of this message is not rounded.
                if (thisWriter == prevWriter) and ((thisTime - prevTime).total_seconds() < self.config.SmsRender["SameMsgTime"]):
                    topRadius = 0
                    incWriter = False
                # Else top of this message is rounded.
                else:
                    topRadius = self.config.SmsRender["BubbleRadius"]
            # Bottom of bottom message is rounded.
            if idx == (numSMSes - 1):
                botRadius = self.config.SmsRender["BubbleRadius"]
            else:
                # If this message is by same writer AND within certain time of next message the bottom of this message is not rounded.
                if (msg.writer == nextWriter) and ((nextTime - thisTime).total_seconds() < self.config.SmsRender["SameMsgTime"]):
                    botRadius = 0
                else:
                    botRadius = self.config.SmsRender["BubbleRadius"]

            # Update time and writer of this message as the new previous message.
            prevTime = thisTime
            prevWriter = thisWriter

            hBox = QHBoxLayout()

            # If there are newline characters in the text string they won't be rendered in the conversation messages
            # which use html format. Need to replace newlines with break tokens.
            messageText = "<br>".join(msg.msgText.split("\n"))

            lbl = QLabel("", self)
            lbl.setTextFormat(QtCore.Qt.RichText)
            if incWriter == True:
                lbl.setText(f'<b>{msg.writer} : {msg.msgTime}</b><br><br>{messageText}')
            else:
               lbl.setText(f'{messageText}')

            # Set label with and wordwrapping, and restrict expanding to vertical only.
            lbl.setFixedWidth(self.config.SmsRender["TextWidth"])
            lbl.setWordWrap(True)
            lbl.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.MinimumExpanding)

            # Add label to horizontal layout.
            # Pad out so my messages on the right, others on the left.
            if msg.writer == self.config.MyHandle:
                hBox.addStretch()
                lbl.setStyleSheet(f'border : 3px solid {borderCol}; background : {fillCol}; padding :10px;'
                            f'border-top-left-radius : {topRadius}px;'
                            f'border-top-right-radius : {topRadius}px;'
                            f'border-bottom-left-radius : {botRadius}px;'
                            f'border-bottom-right-radius : {botRadius}px'
                        )
                hBox.addWidget(lbl)
            else:
                lbl.setStyleSheet(f'border : 3px solid {borderCol}; background : {fillCol}; padding :10px;'
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
    # Go through conversation and update list of
    # writer handles and assign them a random colour.
    # Colours not guaranteed to be unique but doesn't mattter too much.
    # *******************************************
    def updateWriterColours(self):

        # Use randomly generated colours for border and fill.
        # Restrict ranges so that borders are darker than fill.
        bcol = lambda: random.randint(0, self.config.SmsRender["BorderColMax"])
        fcol = lambda: random.randint(self.config.SmsRender["FillColMin"], 255)

        # Go through messages looking for different writers.
        for idx, msg in enumerate(self.conversation.messages):
            # Check if handle already allocated a colour.
            if next((i for i, v in enumerate(self.handleColour) if v[0] == msg.writer), None) == None:
                # Find a colour for the handle, border and fill.
                borderCol = f'#{bcol():02x}{bcol():02x}{bcol():02x}'
                fillCol = f'#{fcol():02x}{fcol():02x}{fcol():02x}'
                # Add new handle and colours to list.
                self.handleColour.append([msg.writer, borderCol, fillCol])

    # *******************************************
    # Get colours for particular writr handle.
    # *******************************************
    def getWriterColours(self, handle):
        for idx, wdet in enumerate(self.handleColour):
            if wdet[0] == handle:
                return wdet[1], wdet[2]

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

        # Size of conversation is restricted by emedded data ratio as applicable to embedding files.
        # Have further restriction on number of messages in a conversation,
        # This restriction is so that application in its current design is responsive.
        if self.conversation.numMessages() == self.config.MaxMessages:
            self.logger.warning(f'Message not sent as would exceed message limit: {self.config.MaxMessages}')
            showPopup("Warning", "Sending Message", f'Message not sent as would exceed message limit of {self.config.MaxMessages} messages.')

            # Clear the contents of the text edit box.
            self.messageEdit.clear()
        else:

            # Read contents of text edit box and add as new message to conversation.
            if self.messageEdit.toPlainText != "":
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

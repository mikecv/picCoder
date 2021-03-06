#!/usr/bin/env python3

from PyQt5 import QtGui
import datetime
import os

from constants import *
from utils import *

# *******************************************
# Consealing and retrieving data in/from image pixel colour.
# Require a lossless pixel format to be able to retrieve data from image.
#
# Data encoded into the image:
# "PICCODER"    - Indicates that the image is encodded.
# <Passorded>   - PASSWDYNBYTES bytes, indicates if password protected, 0=No, 1=Yes.
# <PassWdLen>   - PASSWDLENBYTES bytes, the length of the password.
# <Password>    - <PassWdLen> bytes, the password.
#
# Depending on the <CodeType> the format of the encoded data is different.
#
# <CodeType> = CODETYPE_FILE indicates a file is embedded, with the following format:
# <NameLength>  - NAMELENBYTES bytes, indicates the length of the file name (including path).
# <FileName>    - <NameLength> bytes, the path and filename of the embedded file.
# <FileLength>  - LENBYTES bytes, indicates the length of the embedded file.
# <File>        - <FileLength> bytes, the actual embedded file.
#
# <CodeType> = CODETYPE_TEXT indicates a text conversion is embedded, with the following format:
# <NumTexts>    - NUMSMSBYTES bytes, indicates the number of text messages in the file.
#               - Repeat the following for each text message.
# <TextNum>     - NUMSMSBYTES bytes, indicates the number of this text messages, starts from 1.
# <NameLength>  - NAMELENBYTES bytes, indicates the length of this message's writer name.
# <Name>        - <NameLength> bytes, the name of the writer of this message.
# <TimeLength>  - TIMELENBYTES bytes, the length of the message timestamp.
# <MsgTime>     - <TimeLength> bytes, the timestamp of this message.
# <MsgLength>   - SMSLENBYTES bytes, indicates the length of the message.
# <Message>     - <MsgLength> bytes, the actual message text.
#
# Data is stored in the RGB colour data of pixels.
# Bit by bit the data is stored by ROW, then by COLUMN, then by colour bit starting with the LSB.
# One bit of each pixel for one colour is encoded before encoding in the next colour.
# When all colours (RGB) are encoded for one bit for every pixel the process repeats for the next bit.
# There is a limit to the number of bits that should be encoded ti avoid too much colour distortion of the
# image after it has been encoded.
# *******************************************

# *******************************************
# Text message class
# *******************************************
class TextMessage():   
    def __init__(self, writer, msgText, msgTime=None):

        self.writer = writer
        self.msgText = msgText
        if msgTime == None:
            self.msgTime = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        else:
            self.msgTime = msgTime
    
    # *******************************************
    # Overriding print() output.
    # *******************************************
    def __str__(self):
        return(
            f'Writer : {self.writer}\n'
            f'Time stamp :  {self.msgTime}\n'
            f'Message :  {self.msgText}\n'
        )

# *******************************************
# Conversation class
# *******************************************
class Conversation():   
    def __init__(self):

        self.messages = []

    # *******************************************
    # Add another message to the conversation.
    # *******************************************
    def addMsg(self, writer, msgText, msgTime=None):
        # Create message and add to list of messages.
        self.messages.append(TextMessage(writer, msgText, msgTime))

    # *******************************************
    # Return number of messages in the conversation.
    # *******************************************
    def numMessages(self):
        return (len(self.messages))

    # *******************************************
    # Clear all messages in the conversation.
    # *******************************************
    def clearMessages(self):
        self.messages = []

# *******************************************
# Steganography image class
# *******************************************
class Steganography():   
    def __init__(self, config, log, data):

        self.cfg = config
        self.log = log
        self.data = data

        self.log.debug("Steganography class constructor.")

        # Initialise picture file
        self.picFile = ""

        # Default image flags.
        self.picCoded = False
        self.picCodeType = CodeType.CODETYPE_NONE
        self.picPassword = False
        self.password = ""
        self.picCodeNameLen = 0

        # Initialise parameters for embedded file.
        self.embeddedFilePath = ""
        self.embeddedFileName = ""
        self.embeddedFileSize = 0
        self.toEmbedFilePath = ""
        self.toEmbedFileSize = 0

        # Initialise approximate embedding capacity of image.
        self.capacity = 0

        # Initialise conversation to accept embedded conversation.
        self.conversation = Conversation()

        # Initialise image file read parameters.
        self.row = 0
        self.col = 0
        self.plane = 0
        self.bit = 0
        self.bytesRead = 0
        self.bytesWritten = 0
        self.codeBytes = []

    # *******************************************
    # Load an image to analyze.
    # *******************************************
    def loadNewImage(self, picFile):

        # Initislise conversation in case image has embedded conversation.
        self.conversation.clearMessages()

        # Image to open and read/store data from/to.
        self.picFile = picFile
        self.log.debug(f'Opening image file for analysis : {self.picFile}')
        self.bitmap = QtGui.QPixmap(picFile)
        self.image = QtGui.QImage(picFile)

        # Get image information.
        self.picWidth = self.bitmap.width()
        self.picHeight = self.bitmap.height()
        self.colCount = self.bitmap.colorCount()
        # Qt returns 0 for colour count of 32.
        if self.colCount == 0:
            self.colCount = 32
        # Only support 3 colour planes.
        self.colPlanes = 3
        self.log.debug(f'Image width : {self.picWidth}; height : {self.picHeight}; colour count : {self.colCount}; colour planes : {self.colPlanes}')

        # Calclulate maximum space for embedding, i.e. every pixel, every colour, every bit.
        self.picBytes = self.picWidth * self.picHeight * 3
        self.log.debug(f'Absolute maximimum space for embedding (Bytes) : {self.picBytes}')

        # Initialise image file read parameters.
        self.row = 0
        self.col = 0
        self.plane = 0
        self.bit = 0
        self.bytesRead = 0
        self.bytesWritten = 0
        self.codeBytes = []

        # Check approximate embedding capacity of image.
        self.calcEmbeddingCapacity()

        # Check if image file is picCode encoded.
        self.checkForCode()

        # If is a picCoded image, then need to get type and associated data.
        if self.picCoded:
            self.getpicCodedData()

    # *******************************************
    # Check embedding capacity of image.
    # Embedding capacity is approximate as preamble is not fixed.
    # *******************************************
    def calcEmbeddingCapacity(self):
        self.log.info(f'Calculating image embedding capacity for embed ratio : {self.cfg.MaxEmbedRatio}')

        # Embedding capacity pixels * colours * colourBits * MaxEmbedRatio / 8 bitsPerByte
        self.capacity = int(self.picWidth * self.picHeight * 3 * self.cfg.MaxEmbedRatio)
        self.log.debug(f'Approximate embedding capacity, including preamble (Bytes) : {self.capacity}')

    # *******************************************
    # Check if picture file is encoded.
    # Only checks the coding header.
    # *******************************************
    def checkForCode(self):
        self.log.info("Checking image for picCoder preamble...")

        # Check if file even large enough to hold a code.
        self.fileSize = os.path.getsize(self.picFile)
        if self.fileSize < (len(PROGCODE) + LENBYTES):
            self.log.warning(f'File too small to be picCode encoded : {self.fileSize}')
        else:
            # Read from image file to see if it contains the header code.
            bytesToRead = len(PROGCODE)
            self.readDataFromImage(bytesToRead)
            # Check if we read the expected number of bytes.
            if (self.bytesRead != bytesToRead):
                self.log.error(f'Expected bytes : {bytesToRead}; bytes read : {self.bytesRead}')
            else:
                # Check if the code matches the expected picCoder code.
                progCode = ""
                try:
                    progCode = self.codeBytes.decode('utf-8')
                except:
                    self.log.debug("Failed to read header code from image.")

                if progCode == PROGCODE:
                    # Yes! We have a picCoded image.
                    self.log.info("Image file contains header code.")
                    self.picCoded = True
                    # Check if the embedded file has password protection.
                    bytesToRead = PASSWDYNBYTES
                    self.readDataFromImage(bytesToRead)
                    # Check if we read the expected number of bytes.
                    if (self.bytesRead != bytesToRead):
                        self.log.error(f'Expected bytes : {bytesToRead}; bytes read : {self.bytesRead}')
                    else:
                        self.picPassword = bool(int(self.codeBytes.decode('utf-8')))
                        self.log.info(f'Image file has password protection : {self.picPassword}')
                        # Get the length of the password.
                        bytesToRead = PASSWDLENBYTES
                        self.readDataFromImage(bytesToRead)
                        # Check if we read the expected number of bytes.
                        if (self.bytesRead != bytesToRead):
                            self.log.error(f'Expected bytes : {bytesToRead}; bytes read : {self.bytesRead}')
                        else:
                            self.picPwdLen = int(self.codeBytes.decode('utf-8'))
                            self.log.debug(f'Password length : {self.picPwdLen}')
                            # Get the password.
                            bytesToRead = self.picPwdLen
                            self.readDataFromImage(bytesToRead)
                            # Check if we read the expected number of bytes.
                            if (self.bytesRead != bytesToRead):
                                self.log.error(f'Expected bytes : {bytesToRead}; bytes read : {self.bytesRead}')
                            else:
                                self.password = self.codeBytes.decode('utf-8')
                                self.log.debug("Image password (or not) read.")
                else:
                    self.log.debug("Image file did not contain a valid header code.")

    # *******************************************
    # Read picCoded data from image.
    # *******************************************
    def getpicCodedData(self):

        # Read the data type field.
        bytesToRead = CODETYPEBYTES
        self.readDataFromImage(bytesToRead)
        # Check if we read the expected number of bytes.
        if (self.bytesRead != bytesToRead):
            self.log.error(f'Expected bytes : {bytesToRead}; bytes read : {self.bytesRead}')
        else:
            self.picCodeType = int(self.codeBytes.decode('utf-8'))
            self.log.info(f'Image file has embedded data of type : {self.picCodeType}')

            # Get data based on embedded data type:
 
            # ********************************************************
            # Text conversation.
            # ********************************************************
            if self.picCodeType == CodeType.CODETYPE_TEXT.value:
                # Image has an embedded conversation.
                # Read the number of messages in the convesation.
                bytesToRead = NUMSMSBYTES
                self.readDataFromImage(bytesToRead)
                # Check if we read the expected number of bytes.
                if (self.bytesRead != bytesToRead):
                    self.log.error(f'Expected bytes : {bytesToRead}; bytes read : {self.bytesRead}')
                else:
                    numMsgs = int(self.codeBytes.decode('utf-8'))
                    self.log.info(f'Image file has embedded conversion with number of messages : {numMsgs}')
                    for idx in range(numMsgs):
                        # Read the number of this message.
                        bytesToRead = NUMSMSBYTES
                        self.readDataFromImage(bytesToRead)
                        # Check if we read the expected number of bytes.
                        if (self.bytesRead != bytesToRead):
                            self.log.error(f'Expected bytes : {bytesToRead}; bytes read : {self.bytesRead}')
                        else:
                            msgNum = int(self.codeBytes.decode('utf-8'))
                            # Check if message number is incrementing correctly.
                            if msgNum != (idx+1):
                                self.log.error(f'Message number out of sequence, expected : {idx+1}, read : {msgNum}')
                                break
                            else:
                                self.log.info(f'Processing message number : {msgNum}')
                                # Read the length of the writers name of this message.
                                bytesToRead = NAMELENBYTES
                                self.readDataFromImage(bytesToRead)
                                # Check if we read the expected number of bytes.
                                if (self.bytesRead != bytesToRead):
                                    self.log.error(f'Expected bytes : {bytesToRead}; bytes read : {self.bytesRead}')
                                else:
                                    lenWriter = int(self.codeBytes.decode('utf-8'))
                                    # Read the name of the writer of this message.
                                    bytesToRead = lenWriter
                                    self.readDataFromImage(bytesToRead)
                                    # Check if we read the expected number of bytes.
                                    if (self.bytesRead != bytesToRead):
                                        self.log.error(f'Expected bytes : {bytesToRead}; bytes read : {self.bytesRead}')
                                    else:
                                        nameWriter = self.codeBytes.decode('utf-8')
                                        self.log.info(f'Message from writer : {nameWriter}')
                                        # Read the length of the timestamp of this message.
                                        bytesToRead = TIMELENBYTES
                                        self.readDataFromImage(bytesToRead)
                                        # Check if we read the expected number of bytes.
                                        if (self.bytesRead != bytesToRead):
                                            self.log.error(f'Expected bytes : {bytesToRead}; bytes read : {self.bytesRead}')
                                        else:
                                            lenTime = int(self.codeBytes.decode('utf-8'))
                                            # Read the timestamp of this message.
                                            bytesToRead = lenTime
                                            self.readDataFromImage(bytesToRead)
                                            # Check if we read the expected number of bytes.
                                            if (self.bytesRead != bytesToRead):
                                                self.log.error(f'Expected bytes : {bytesToRead}; bytes read : {self.bytesRead}')
                                            else:
                                                msgTime = self.codeBytes.decode('utf-8')
                                                self.log.info(f'Message timestamp : {msgTime}')
                                                # Read the length of this message.
                                                bytesToRead = SMSLENBYTES
                                                self.readDataFromImage(bytesToRead)
                                                # Check if we read the expected number of bytes.
                                                if (self.bytesRead != bytesToRead):
                                                    self.log.error(f'Expected bytes : {bytesToRead}; bytes read : {self.bytesRead}')
                                                else:
                                                    lenMsg = int(self.codeBytes.decode('utf-8'))
                                                    # Read the timestamp of this message.
                                                    bytesToRead = lenMsg
                                                    self.readDataFromImage(bytesToRead)
                                                    # Check if we read the expected number of bytes.
                                                    if (self.bytesRead != bytesToRead):
                                                        self.log.error(f'Expected bytes : {bytesToRead}; bytes read : {self.bytesRead}')
                                                    else:
                                                        self.log.debug(f'Message bytes : {self.bytesRead}')
                                                        msgText = self.codeBytes.decode('utf-8')

                                                        # Add message to conversion object.
                                                        self.conversation.addMsg(nameWriter, msgText, msgTime)

            # ********************************************************
            # Embedded file.
            # ********************************************************
            elif self.picCodeType == CodeType.CODETYPE_FILE.value:
                # Image has an embedded file.
                # Read the length of the filename.
                bytesToRead = NAMELENBYTES
                self.readDataFromImage(bytesToRead)
                # Check if we read the expected number of bytes.
                if (self.bytesRead != bytesToRead):
                    self.log.error(f'Expected bytes : {bytesToRead}; bytes read : {self.bytesRead}')
                else:
                    self.picCodeNameLen = int(self.codeBytes.decode('utf-8'))
                    self.log.info(f'Image file has embedded file with filename length : {self.picCodeNameLen}')
                    # Read the filename.
                    bytesToRead = self.picCodeNameLen
                    self.readDataFromImage(bytesToRead)
                    # Check if we read the expected number of bytes.
                    if (self.bytesRead != bytesToRead):
                        self.log.error(f'Expected bytes : {bytesToRead}; bytes read : {self.bytesRead}')
                    else:
                        self.embeddedFilePath = self.codeBytes.decode('utf-8')
                        self.log.info(f'Embedded file full path : {self.embeddedFilePath}')
                        head, self.embeddedFileName = os.path.split(self.embeddedFilePath)
                        self.log.info(f'Embedded file has filename : {self.embeddedFileName}')
                        # Now that we have the filename we can read the file size.
                        bytesToRead = LENBYTES
                        self.readDataFromImage(bytesToRead)
                        # Check if we read the expected number of bytes.
                        if (self.bytesRead != bytesToRead):
                            self.log.error(f'Expected bytes : {bytesToRead}; bytes read : {self.bytesRead}')
                        else:
                            self.embeddedFileSize = int(self.codeBytes.decode('utf-8'))
                            self.log.info(f'Embedded file has file size : {self.embeddedFileSize}')

            else:
                # Unsupported embedded data type.
                self.log.error("Unsupported coded data type.")

    # *******************************************
    # Read buffer of data from image file.
    # Continue reading from where we left off.
    # *******************************************
    def readDataFromImage(self, bytesToRead):

        # Initialise loop counters counters.
        bytesRead = 0
        rowCnt = self.row
        colCnt = self.col
        colPlane = self.plane
        bitsRead = self.bit

        # Initialise array to hold read data.
        self.codeBytes = bytearray()

        # Intialise colour bit mask.
        mask = 1 << bitsRead

        while bytesRead < bytesToRead:
            codeData = 0

            # Extract a byte worth of data.
            for bitCnt in range(0, 8):
                colPart = QtGui.QColor(self.image.pixel(colCnt, rowCnt)).getRgb()[colPlane]
                byteBit = colPart & mask
                byteBit = byteBit >> bitsRead
                codeData = codeData << 1
                codeData = codeData | byteBit                 
    
                # Point to next column.
                colCnt += 1
                if colCnt == self.picWidth:
                    colCnt = 0
                    rowCnt += 1
                    # If we have reached the end of the image then go
                    # back to the top and go to the text bit.
                    if rowCnt == self.picHeight:
                        rowCnt = 0
                        colPlane += 1
                        if colPlane == self.colPlanes:
                            colPlane = 0
                            # Used all colour planes so move to next bit.
                            bitsRead += 1
                            mask = mask <<  1
   
            # Append the character to the code byte array.
            self.codeBytes.append(codeData)
    
            # Increment characters read counter.
            bytesRead += 1

        # Update loop counters for next time.
        self.row = rowCnt
        self.col = colCnt
        self.plane = colPlane
        self.bit = bitsRead
        self.bytesRead = bytesRead

    # *******************************************
    # Image has embedded file.
    # Read the file data and save as file.
    # *******************************************
    def saveEmbeddedFile(self, saveToFilename):

        self.log.info(f'Saving embedded image to : {saveToFilename}')

        # Save the file data pointers so that they can be restored.
        # Need to do this so that we can save again if we have to.
        rowCntSave = self.row
        colCntSave = self.col
        colPlaneSave = self.plane
        bitCntSave = self.bit

        # Create progress bar and initialise.
        self.data.progressBar.setNote('Extracting file from image...')
        self.data.progressBar.showProgressBar()
        loopProgress = BYTESTACK / self.embeddedFileSize * 100.0
        codeProgress = 0.0

        self.data.progressBar.setProgress(int(codeProgress))

        # Open file to extract code to.
        try:
            self.log.info(f'Opening file to save to : {saveToFilename}')
            with open(saveToFilename, mode='wb') as cf:

                # Have the size of the embedded file, so can read the contents of the file.
                bytesToRead = self.embeddedFileSize

                # Read and write a hung of data at a time.
                # Update the progress as we go.
                while bytesToRead > 0:
                    if bytesToRead > BYTESTACK:
                        bytesThisRead = BYTESTACK
                        bytesToRead -= BYTESTACK
                    else:
                        bytesThisRead = bytesToRead
                        bytesToRead = 0

                    # Read the hunk of data.
                    self.readDataFromImage(bytesThisRead)

                    # Check if we read the expected number of bytes.
                    if (self.bytesRead != bytesThisRead):
                        self.log.error(f'Expected byte hunk : {bytesThisRead}; bytes read : {self.bytesRead}')
                    else:
                        self.log.debug("Writing embedded data hunk to file...")
                        # Open the file and write data to it.
                        try:
                            cf.write(self.codeBytes)

                            # Update the progress bar as we go along.
                            codeProgress += loopProgress
                            if codeProgress > 100.0:
                                codeProgress = 100.0
                            self.data.progressBar.setProgress(int(codeProgress))
                        except:
                            self.log.error(f'Failed to write code hunk to file.')
                            self.log.error(f'Exception returned : {str(e)}')       

            # Done so can hide the progress bar.
            self.data.progressBar.hideProgressBar()

        # Failed to open the file for writing.
        except Exception as e:
            self.log.error(f'Failed to open file to save to : {saveToFilename}')
            self.log.error(f'Exception returned : {str(e)}')       

        # Restore the file data pointers, so that we can save again if we have to.
        self.row = rowCntSave
        self.col = colCntSave
        self.plane = colPlaneSave
        self.bit = bitCntSave

    # *******************************************
    # Write data to image.
    # Continue writing from where we left off.
    # *******************************************
    def writeDataToImage(self, bytesToWrite):

        # Initialise loop counters counters.
        bytesWritten = 0
        rowCnt = self.row
        colCnt = self.col
        colPlane = self.plane
        bitWrite = self.bit

        # Initialise embedding space to True.
        noSpace = False

        # Intialise colour bit mask.
        colMask = 1 << bitWrite

        for byteData in bytesToWrite:
            # Mask for reading byte bits.
            # Start from MSB so in bit order in the image (assume 8 bit byte).
            mask = 128

            # Cycle through 8 bits in each byte.
            for bitCnt in range(0, 8):
                # Check if we have any more space to store data.
                if noSpace == True: break
    
                # Get next bit for byte in the array.
                if (byteData & mask) == 0:
                    mappedBit = 0
                else: mappedBit = 1
                mappedBit = mappedBit << bitWrite
    
                # Get current colour value, and modify with byte mapped bit.
                colPixel = QtGui.QColor(self.image.pixel(colCnt, rowCnt))
                colPart = colPixel.getRgb()[colPlane]
                colPartModified = (colPart & ~colMask) + mappedBit

                # Modify the colour plane component that we are up to.
                if colPlane == 0:
                    colPixel.setRed(colPartModified)
                elif colPlane == 1:
                    colPixel.setGreen(colPartModified)
                elif colPlane == 2:
                    colPixel.setBlue(colPartModified)
                # Update the pixel colour now that the colour component has been modified.
                self.image.setPixel(colCnt, rowCnt, colPixel.rgb())
                
                # Shift mask right (towards LSB).
                mask = mask >> 1
    
                # Point to next column.
                colCnt += 1
                if colCnt == self.picWidth:
                    colCnt = 0
                    rowCnt += 1
                    # If we have reached the end of the image then go
                    # back to the top and go to the text bit.
                    if rowCnt == self.picHeight:
                        rowCnt = 0
                        # Point to next colour plane.
                        # Take into account number of planes.
                        colPlane += 1
                        if colPlane == self.colPlanes:
                            colPlane = 0
                            # Used all colour planes so move to next bit.
                            bitWrite += 1
                            colMask = colMask << 1
                            if bitWrite == 8:
                                # No more pixels
                                noSpace = True
    
            # Increment characters read counter.
            bytesWritten += 1

        # Update loop counters for next time.
        self.row = rowCnt
        self.col = colCnt
        self.plane = colPlane
        self.bit = bitWrite
        self.bytesWritten = bytesWritten

    # *******************************************
    # Read file and embed into the current image.
    # Embed password if required.
    # *******************************************
    def embedFileToImage(self, passworded=False, pw=""):

        self.log.info(f'Embedding into image from file : {self.toEmbedFilePath}')

        # Create progress bar and initialise.
        self.data.progressBar.setNote('Embedding file into image...')
        self.data.progressBar.showProgressBar()
        loopProgress = BYTESTACK / self.toEmbedFileSize * 100.0
        codeProgress = 0.0

        self.data.progressBar.setProgress(int(codeProgress))

        # Initialise image file read parameters.
        self.row = 0
        self.col = 0
        self.plane = 0
        self.bit = 0
        self.bytesWritten = 0
        self.codeBytes = []

        # Open file to be embedded.
        try:
            self.log.info(f'Opening file to embed : {self.toEmbedFilePath}')
            with open(self.toEmbedFilePath, mode='rb') as cf:

                # Need to add picCoder encoding to image first.
                frmtString = ('%%s%%0%dd%%0%dd%%s%%0%dd%%0%dd%%s%%0%dd') % (PASSWDYNBYTES, PASSWDLENBYTES, CODETYPEBYTES,  NAMELENBYTES, LENBYTES)
                picCodeHdr = frmtString % (PROGCODE, int(passworded), len(pw), pw, CodeType.CODETYPE_FILE.value, len(self.toEmbedFilePath), self.toEmbedFilePath, self.toEmbedFileSize)

                self.log.info(f'Composed piCoder code to insert into image : {picCodeHdr}')
                self.log.info('Embedding picCoder encoding information into start of image.')
                self.writeDataToImage(bytearray(picCodeHdr, encoding='utf-8'))

                # Need to embed the actual file into the image.
                self.log.info('Embedding file into the image.')

                # Have the size of the file to embed, so can write the contents of the file.
                bytesToWrite = self.toEmbedFileSize

                # Read and write a hung of data at a time.
                # Update the progress as we go.
                while bytesToWrite > 0:
                    if bytesToWrite > BYTESTACK:
                        bytesThisWrite = BYTESTACK
                        bytesToWrite -= BYTESTACK
                    else:
                        bytesThisWrite = bytesToWrite
                        bytesToWrite = 0

                    try:
                        # Read the hunk of data from the file.
                        byteBuffer = cf.read(bytesThisWrite)
                        # And write the hunk into the image
                        self.writeDataToImage(byteBuffer)

                        # Check if we wrote the expected number of bytes.
                        if (self.bytesWritten != bytesThisWrite):
                            self.log.error(f'Expected byte hunk : {bytesThisWrite}; bytes written : {self.bytesWritten}')
                        else:
                            # Update the progress bar as we go along.
                            codeProgress += loopProgress
                            if codeProgress > 100.0:
                                codeProgress = 100.0
                            self.data.progressBar.setProgress(int(codeProgress))
                    except:
                        self.log.error(f'Failed to write code hunk to image.')
                        self.log.error(f'Exception returned : {str(e)}')       

                # Done so can hide the progress bar.
                self.data.progressBar.hideProgressBar()

        # Failed to open the file for reading.
        except Exception as e:
            self.log.error(f'Failed to open file to read from : {self.toEmbedFilePath}')
            self.log.error(f'Exception returned : {str(e)}')

    # *******************************************
    # Embed conversantion into the current image.
    # Embed password if required.
    # *******************************************
    def embedConversationIntoImage(self, passworded=False, pw=""):

        self.log.info(f'Embedding conversation into image.')

        # Create progress bar and initialise.
        msg = 0
        self.data.progressBar.setNote('Embedding conversation into image...')
        self.data.progressBar.showProgressBar()
        loopProgress = msg / len(self.conversation.messages) * 100.0
        codeProgress = 0.0

        self.data.progressBar.setProgress(int(codeProgress))

        # Initialise image file read parameters.
        self.row = 0
        self.col = 0
        self.plane = 0
        self.bit = 0
        self.bytesWritten = 0

        # Need to add picCoder encoding to image first.
        frmtString = ('%%s%%0%dd%%0%dd%%s%%0%dd%%0%dd') % (PASSWDYNBYTES, PASSWDLENBYTES, CODETYPEBYTES,  NUMSMSBYTES)
        picCodeHdr = frmtString % (PROGCODE, int(passworded), len(pw), pw, CodeType.CODETYPE_TEXT.value, len(self.conversation.messages))

        self.log.info(f'Composed piCoder code to insert into image : {picCodeHdr}')
        self.log.info('Embedding picCoder encoding information into start of image.')
        self.writeDataToImage(bytearray(picCodeHdr, encoding='utf-8'))

        for idx, msg in enumerate(self.conversation.messages):
            # Construct the message.
            # Use byte length of encoded string message so that full string is encoded in image.
            frmtString = ('%%0%dd%%0%dd%%s%%0%dd%%s%%0%dd%%s') % (NUMSMSBYTES, NAMELENBYTES, TIMELENBYTES, SMSLENBYTES)
            msgDetail = frmtString % ((idx+1), len(msg.writer), msg.writer, len(msg.msgTime), msg.msgTime, blen(msg.msgText), msg.msgText)
            self.log.info(f'Composed code for message  : {msgDetail}')
            self.log.info('Embedding message encoding data into image.')
            self.writeDataToImage(bytearray(msgDetail, encoding='utf-8'))

            # Update the progress bar as we go along.
            codeProgress += loopProgress
            if codeProgress > 100.0:
                codeProgress = 100.0
            self.data.progressBar.setProgress(int(codeProgress))

        # Done so can hide the progress bar.
        self.data.progressBar.hideProgressBar()

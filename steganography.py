#!/usr/bin/env python3

from PyQt5 import QtGui
import os

from constants import *

# *******************************************
# Steganography image class
# *******************************************
class Steganography():   
    def __init__(self, config, log, picFile):
        
        self.cfg = config
        self.log = log

        self.log.debug("Steganography class constructor.")

        self.picFile = picFile
        self.log.debug(f'Opening image file for analysis : {self.picFile}')
        self.bitmap = QtGui.QPixmap(picFile)
        self.image = QtGui.QImage(picFile)

        # Default image flags.
        self.picCoded = False
        self.picCodeType = CodeType.CODETYPE_NONE
        self.picCodeNameLen = 0
        self.embeddedFilePath = ""
        self.embeddedFileName = ""
        self.embeddedFileSize = 0

        # Get image information.
        self.picWidth = self.bitmap.width()
        self.picHeight = self.bitmap.height()
        self.picDepth = self.bitmap.defaultDepth()
        self.log.debug(f'Image width : {self.picWidth}; height : {self.picHeight}; default depth : {self.picDepth}')
        self.picColBits = self.picDepth // 3
        self.log.debug(f'Image colour bits : {self.picColBits}')

        # Initialise image file read parameters.
        self.row = 0
        self.col = 0
        self.plane = 0
        self.bit = 0
        self.bytesRead = 0
        self.codeBytes = []

        # Check if image file is picCode encoded.
        self.checkForCode()

        # If is a picCoded image, then need to get type and associated data.
        if self.picCoded:
            self.getpicCodedData()

    # *******************************************
    # Check if picture file is encoded.
    # Return true if has picCode conding.
    # Only checks the coding header.
    # *******************************************
    def checkForCode(self):

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
                    self.log.debug("Image file did not contain header code.")

                if progCode == PROGCODE:
                    # Yes! We have a picCoded image.
                    self.log.info("Image file contains header code.")
                    self.picCoded = True

    # *******************************************
    # Read picCoded data from image.
    # *******************************************
    def getpicCodedData(self):

        # Read the data type field.
        bytesToRead = CODETYPEBYTES
        self.readDataFromImage(CODETYPEBYTES)
        # Check if we read the expected number of bytes.
        if (self.bytesRead != bytesToRead):
            self.log.error(f'Expected bytes : {bytesToRead}; bytes read : {self.bytesRead}')
        else:
            self.picCodeType = int(self.codeBytes.decode('utf-8'))
            self.log.info(f'Image file has embedded data of type : {self.picCodeType}')

            # Get data based on embedded data type:
 
            # ********************************************************
            # Plain text.
            # ********************************************************
            if self.picCodeType == CodeType.CODETYPE_TEXT.value:
                pass

            # ********************************************************
            # Embedded file.
            # ********************************************************
            elif self.picCodeType == CodeType.CODETYPE_FILE.value:
                # Image has an embedded file.
                # Read the length of the filename.
                bytesToRead = NAMELENBYTS
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
                            # Read data and save the file.
                            # self.safeEmbeddedFile()

            # ********************************************************
            # Embedded image file.
            # ********************************************************
            elif self.picCodeType == CodeType.CODETYPE_PIC.value:
                pass

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
                colPart = QtGui.QColor(self.image.pixel(rowCnt, colCnt)).getRgb()[colPlane]
                byteBit = colPart & mask
                byteBit = byteBit >> bitsRead
                codeData = codeData << 1
                codeData = codeData | byteBit                 
    
                # Point to next colour plane.
                colPlane += 1
                if colPlane == 3: colPlane = 0
                
                # Point to next column.
                colCnt += 1
                if colCnt == self.picWidth:
                    colCnt = 0
                    rowCnt += 1
                    # If we have reached the end of the image then go
                    # back to the top and go to the text bit.
                    if rowCnt == self.picHeight:
                        rowCnt = 0
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
    def safeEmbeddedFile(self):

        # Have the size of the embedded file, so can read the contents of the file.
        bytesToRead = self.embeddedFileSize 
        self.readDataFromImage(bytesToRead)

        # Check if we read the expected number of bytes.
        if (self.bytesRead != bytesToRead):
            self.log.error(f'Expected bytes : {bytesToRead}; bytes read : {self.bytesRead}')
        else:
            self.log.debug("Writing embedded data to file...")
            # Open the file and write data to it.
            with open(self.embeddedFileName, mode='wb') as cf:
                cf.write(self.codeBytes)


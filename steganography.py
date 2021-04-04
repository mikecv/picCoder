#!/usr/bin/env python3

from PyQt5 import QtGui
import os

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
        self.codeBytes = []

        # Check if image file is picCode encoded.
        self.checkForCode()

    # *******************************************
    # Check if picture file is encoded.
    # Return true if has picCode conding.
    # Only checks the coding header.
    # *******************************************
    def checkForCode(self):

        # Check if file even large enough to hold a code.
        self.fileSize = os.path.getsize(self.picFile)
        if self.fileSize < (len(self.cfg.PicEncoding["ProgCode"]) + self.cfg.PicEncoding["LenBytes"]):
            self.log.warning(f'File too small to be picCode encoded : {self.fileSize}')
        else:
            # Read from image file to see if it contains the header code.
            self.readDataFromImage(len(self.cfg.PicEncoding["ProgCode"]))
            progCode = ""
            try:
                progCode = self.codeBytes.decode('utf-8')
            except:
                self.log.debug("Image file did not contain header code.")

            if progCode == self.cfg.PicEncoding["ProgCode"]:
                self.picCoded = True

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

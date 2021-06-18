#!/usr/bin/env python3

# *******************************************
# This file contains variables intended to be program constants.
# They should be constants as they relate to the code applied to images.
# *******************************************

from enum import Enum

# Program costants.
PROGCODE = "PICCODER"
LENBYTES = 10
NAMELENBYTES = 3
TIMELENBYTES = 3
CODETYPEBYTES = 1
PASSWDYNBYTES = 1
PASSWDLENBYTES = 2
NUMSMSBYTES = 3
SMSLENBYTES = 3
BYTESTACK = 50000

# Embedded code types.
class CodeType(Enum):
    CODETYPE_NONE = 0
    CODETYPE_FILE = 1
    CODETYPE_TEXT = 2

# Password limits.
PASSWDMINIMUM = 6
PASSWDMAXIMUM = 20

# Supported image types.
# Lower case.
ONLYIMAGES = [".png"]
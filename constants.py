#!/usr/bin/env python3

# This file contains variables intended to be program constants.
# They should be constants as they relate to the code applied to images.

from enum import Enum

# Program costants.
PROGCODE = "PICCODER"
LENBYTES = 8
NAMELENBYTES = 2
CODETYPEBYTES = 1
BYTESTACK = 50000

# Embedded code types.
class CodeType(Enum):
    CODETYPE_NONE = 0
    CODETYPE_TEXT = 0
    CODETYPE_FILE = 1
    CODETYPE_PIC = 2

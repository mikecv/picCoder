#!/usr/bin/env python3

# *******************************************
# Return byte length of encoded string.
# *******************************************
def blen(s):
    # Return byte length of string with utf-8 encoding.
    return len(s.encode('utf-8'))

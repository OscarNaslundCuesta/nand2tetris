"""
hjcError.py -- Error messages for Hack Jack compiler
"""

import sys

errorCount = 0

def Error(message, filename='', lineNumber=0, line=''):
    global errorCount
    _PrintError(message, filename, lineNumber, line)
    errorCount += 1
    if errorCount >= 100:
        FatalError ("Too many errors, compilation aborted.")

def _PrintError(message, filename='', lineNumber=0, line=''):
    """
    Print an error message and continue.
    """
    if filename != '' and lineNumber != 0:
        print('%s(%d): %s' % (filename, lineNumber, line))
        print('     '+message)
    else:
        print(message)
    print('')    

def FatalError(message, filename='', lineNumber=0, line=''):
    """
    Print an error message and abort.
    """
    _PrintError(message, filename, lineNumber, line)
    sys.exit(-1)

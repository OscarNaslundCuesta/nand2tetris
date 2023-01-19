# Copyright (C) 2011 Mark Armbrust.  Permission granted for educational use.
"""
hasmCode.py -- Code class for Hack computer assembler

See "The Elements of Computing Systems", by Noam Nisan and Shimon Schocken
"""

class Code(object):
##EGEN BYGGD DICTIONARY FÖR DEST OCH BINÄRA MOTSVARIGHETEN
    _destDict = {
            'M': '001',
            'D': '010',
            'MD': '011',
            'A': '100',
            'AM': '101',
            'AD': '110',
            'AMD': '111'
            }
    _compDict = {
            '0': '0101010',
            '1': '0111111',
            '-1': '0111010',
            'D': '0001100',
            'A': '0110000',
            '!D': '0001101',
            '!A': '0110001',
            '-D': '0001111',
            '-A': '0110011',
            'D+1': '0011111',
            'A+1': '0110111',
            'D-1': '0001110',
            'A-1': '0110010',
            'D+A': '0000010',
            'A+D': '0000010',
            'D-A': '0010011',
            'A-D': '0000111',
            'D&A': '0000000',
            'A&D': '0000000',
            'D|A': '0010101',
            'A|D': '0010101',
            'M': '1110000',
            '!M': '1110001',
            '-M': '1110011',
            'M+1': '1110111',
            'M-1': '1110010',
            'D+M': '1000010',
            'M+D': '1000010',
            'D-M': '1010011',
            'M-D': '1000111',
            'D&M': '1000000',
            'M&D': '1000000',
            'D|M': '1010101',
            'M|D': '1010101'
            }
    _jumpDict = {
            'JGT': '001',
            'JEQ': '010',
            'JGE': '011',
            'JLT': '100',
            'JNE': '101',
            'JLE': '110',
            'JMP': '111'
            }
    
    def __init__(self):
        """
        Constructor Code()
        """
        pass    

    def Dest(self, mnemonic):
        if len(mnemonic) == 0:
            return '000'                    #Om det inte finns dest --> null
        elif mnemonic in self._destDict:    #Om den finns i dictionaryn returna värdet
            return self._destDict[mnemonic]
        else:
            return None
################################################################
# To be completed:
#       Returns the binary code of the dest mnemonic. (3 bits)
#       Combination of AMD.
#       Returns None if the mnemonic cannot be decoded.
# Remove return None, and add your code.
################################################################


    def Comp(self, mnemonic):
        """
        Returns the binary code of the comp mnemonic. (7 bits)

        Returns None if the mnemonic cannot be decoded.
        """
        if mnemonic in self._compDict:
            return self._compDict[mnemonic]
        else:
            return None        

    def Jump(self, mnemonic):
        """
        Returns the binary code of the jump mnemonic. (3 bits)

        Returns None if the mnemonic cannot be decoded.
        """
        if len(mnemonic) == 0:
            return '000'
        elif mnemonic in self._jumpDict:
            return self._jumpDict[mnemonic]
        else:
            return None

"""
hjcVmWriter -- VmWriter class for Hack Jack compiler
"""

from Error import *

SEG_ARG     = 0
SEG_CONST   = 1
SEG_LOCAL   = 2
SEG_POINTER = 3
SEG_STATIC  = 4
SEG_TEMP    = 5
SEG_THAT    = 6
SEG_THIS    = 7

OP_ADD = 0
OP_AND = 1
OP_EQ  = 2
OP_GT  = 3
OP_LT  = 4
OP_NEG = 5
OP_NOT = 6
OP_OR  = 7
OP_SUB = 8

class VmWriter(object):
    def __init__(self, outputName, debug=False):
        """
        Open 'outputName' and gets ready to write it.
        """
        self.outputFile = open(outputName, 'w')
        self.debug = debug
        self.fnLineNumber = 0;
        

    def Close(self):
        """
        Closes the output file.
        """
        self.outputFile.close()


    def WriteComment(self, string):
        """
        Write a comment in the output file.
        """
        if string[0] != '/':
            string = ' ' + string
        self.outputFile.write('//' + string + '\n')


    def WritePush(self, segment, index):
        """
        Write a VM push command.
        """
        self._WriteCommand('push %s %d' % (self._SegName(segment), index))

    def WritePop(self, segment, index):
        """
        Write a VM pop command.
        """
        self._WriteCommand('pop %s %d' % (self._SegName(segment), index))
        


    def WriteArithmetic(self, command):
        """
        Write a VM aritmetic command.
        """
        self._WriteCommand('%s' % self._OpName(command))
        


    def WriteLabel(self, label):
        """
        Write a VM label command.
        """
        self._WriteCommand('label %s' % label, False)
        
        
        
    def WriteGoto(self, label):
        """
        Write a VM goto command.
        """
        self._WriteCommand('goto %s' % label)
        
        
        
    def WriteIf(self, label):
        """
        Write a VM if-goto command.
        """
        self._WriteCommand('if-goto %s' % label)
        


    def WriteCall(self, name, nArgs):
        """
        Write a VM call command.
        """
        self._WriteCommand('call %s %d' % (name, nArgs))
        
        
        
    def WriteFunction(self, name, nLocals):
        """
        Write a VM function command.
        """
        self.fnLineNumber = 0
        self._WriteCommand('function %s %d' % (name, nLocals))
        
        

    def WriteReturn(self):
        """
        Write a VM return command.
        """
        self._WriteCommand('return')
        


    def _SegName(self, segment):
        """
        Helper function to convert SEG_* to string.
        """
        return ('argument', 'constant', 'local', 'pointer', 'static', 'temp',
                'that', 'this')[segment]

        
    def _OpName(self, segment):
        """
        Helper function to convert OP_* to string.
        """
        return ('add', 'and', 'eq', 'gt', 'lt', 'neg', 'not', 'or',
                'sub')[segment]


    def _WriteCommand(self, command, number = True):
        self.outputFile.write(command)
        if self.debug and number:
            n = len(command)
            i = 8-n%8
            self.outputFile.write(' '*i)
            n += i
            while n < 24:
                self.outputFile.write(' '*8)
                n += 8
            self.outputFile.write('// %d' % self.fnLineNumber)
            self.fnLineNumber += 1
        self.outputFile.write('\n')

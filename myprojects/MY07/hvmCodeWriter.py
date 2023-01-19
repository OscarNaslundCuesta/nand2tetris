"""
hvmCodeWriter.py -- Code Writer class for Hack VM translator
"""

import os
from hvmCommands import *

debug = False

class CodeWriter(object):
    
    def __init__(self, outputName):
        """
        Open 'outputName' and gets ready to write it.
        """
        self.file = open(outputName, 'w')
        self.SetFileName(outputName)

        self.labelNumber = 0
        self.returnLabel = None
        self.callLabel = None
        self.cmpLabels = {}
        self.needHalt = True


    def Debug(self, value):
        """
        Set debug mode.
        Debug mode writes useful comments in the output stream.
        """
        global debug
        debug = value


    def Close(self):
        """
        Write a jmp $ and close the output file.
        """
        if self.needHalt:
            if debug:
                self.file.write('    // <halt>\n')
            label = self._UniqueLabel()
            self._WriteCode('@%s, (%s), 0;JMP' % (label, label))
        self.file.close()


    def SetFileName(self, fileName):
        """
        Sets the current file name to 'fileName'.
        Restarts the local label counter.

        Strips the path and extension.  The resulting name must be a
        legal Hack Assembler identifier.
        """
        if (debug):
            self.file.write('    // File: %s\n' % (fileName))
        self.fileName = os.path.basename(fileName)
        self.fileName = os.path.splitext(self.fileName)[0]
        self.functionName = None


    def Write(self, line):
        """
        Raw write for debug comments.
        """
        self.file.write(line + '\n')

    def _UniqueLabel(self):
        """
        Make a globally unique label.
        The label will be _sn where sn is an incrementing number.
        """
        self.labelNumber += 1
        return '_' + str(self.labelNumber)


    def _LocalLabel(self, name):
        """
        Make a function/module unique name for the label.
        If no function has been entered, the name will be
        FileName$$name. Otherwise it will be FunctionName$name.
        """
        if self.functionName != None:
            return self.functionName + '$' + name
        else:
            return self.fileName + '$$' + name


    def _StaticLabel(self, index):
        """
        Make a name for static variable 'index'.
        The name will be FileName.index
        """
        return self.fileName + '.' + str(index)    


    def _WriteCode(self, code):
        """
        Write the comma separated commands in 'code'.
        """
        code = code.replace(',', '\n').replace(' ', '')
        self.file.write(code + '\n')
        

 
        

    """"
    The functions to be implemented are found beyond this point 
    """
	
    """
    Parameters: 

    Result: 
    For push: Pushes the content of segment[index] onto the stack. It is a good idea to move the value to be pushed into a register first, 
    then push the content of the register to the stack.
    For pop: Pops the top of the stack into segment[index]. You may need to use a general purpose register (R13-R15) 
    to store some temporary results.
    Returns: 
    Nothing.

    Hint: Recall that there are 8 memory segments in the VM model, but only 5 of these exist in the assembly definition. 
    Also, not all 8 VM segments allow to perform both pop and push on them. Chapter 7.3 of the book explains memory segment mapping.
    Hint: Use pen and paper first. Figure out how to compute the address of segment[index] (except for constant). 
    Then figure out how you move the value of segment[index] into a register (by preference D). 
    Then figure out how to push a value from a register onto the stack. 

    Hint: For pop, you already know how to compute the address of segment[index]. 
    Store it in a temporary register (you can use R13 to R15 freely). 
    Then read the value from the top of the stack, adjust the top of the stack, and then store the value at the location 
    stored in the temporary register.
    """


    def WritePushPop(self, commandType, segment, index):
        #segment = arg1 (string)
        #index = arg2 (int)

        if commandType == 2: #if PUSH

            if segment == 'local':
                self._WriteCode(f'@LCL,D=M,@{index},A=A+D,D=M,@SP,A=M,M=D,@SP,M=M+1')

            elif segment == 'argument':
                self._WriteCode(f'@ARG,D=M,@{index},A=A+D,D=M,@SP,A=M,M=D,@SP,M=M+1')

            elif segment == 'this':
                self._WriteCode(f'@THIS,D=M,@{index},A=A+D,D=M,@SP,A=M,M=D,@SP,M=M+1')
            
            elif segment == 'that':
                self._WriteCode(f'@THAT,D=M,@{index},A=A+D,D=M,@SP,A=M,M=D,@SP,M=M+1')

            elif segment == 'constant':
                self._WriteCode(f'@{index},D=A,@SP,A=M,M=D,@SP,M=M+1')


            elif segment == 'static':
                fileName = self._StaticLabel(index)
                #self._WriteCode(f'@{fileName},D=M,@SP,AM=M-1,D=M,@R13,A=M,M=D')
                self._WriteCode(f'@{fileName},D=M,@SP,A=M,M=D,@SP,M=M+1')

            elif segment == 'temp': #ram 5+i
                self._WriteCode(f'@5,D=A,@{index},A=A+D,D=M,@SP,A=M,M=D,@SP,M=M+1')

            elif segment == 'pointer': #ram 3+i
                self._WriteCode(f'@3,D=A,@{index},A=A+D,D=M,@SP,A=M,M=D,@SP,M=M+1')


        elif commandType == 3: #if POP
            #base address + index
            if segment == 'local':
                self._WriteCode(f'@LCL,D=M,@{index},D=A+D,@R13,M=D,@SP,AM=M-1,D=M,@R13,A=M,M=D')

            elif segment == 'argument':
                self._WriteCode(f'@ARG,D=M,@{index},D=A+D,@R13,M=D,@SP,AM=M-1,D=M,@R13,A=M,M=D')

            elif segment == 'this':
                self._WriteCode(f'@THIS,D=M,@{index},D=A+D,@R13,M=D,@SP,AM=M-1,D=M,@R13,A=M,M=D')
            
            elif segment == 'that':
                self._WriteCode(f'@THAT,D=M,@{index},D=A+D,@R13,M=D,@SP,AM=M-1,D=M,@R13,A=M,M=D')
            
            
            elif segment == 'static':
                fileName = self._StaticLabel(index)
                self._WriteCode(f'@SP,AM=M-1,D=M,@{fileName},M=D')
            
            elif segment == 'temp': #ram 5+i
                self._WriteCode(f'@5,D=A,@{index},D=A+D,@R13,M=D,@SP,AM=M-1,D=M,@R13,A=M,M=D')

            elif segment == 'pointer': #ram 3+i
                self._WriteCode(f'@3,D=A,@{index},D=A+D,@R13,M=D,@SP,AM=M-1,D=M,@R13,A=M,M=D')


        """
        Write Hack code for 'commandType' (C_PUSH or C_POP).
        'segment' (string) is the segment name.
        'index' (int) is the offset in the segment.
	To be implemented as part of Project 6
	
	    For push: Pushes the content of segment[index] onto the stack. It is a good idea to move the value to be pushed into a register first, 
        then push the content of the register to the stack.

        For pop: Pops the top of the stack into segment[index]. You may need to use a general purpose register (R13-R15) 
        to store some temporary results.
        Hint: Recall that there are 8 memory segments in the VM model, but only 5 of these exist in the assembly definition. 
        Also, not all 8 VM segments allow to perform both pop and push on them. Chapter 7.3 of the book explains memory segment mapping.
        Hint: Use pen and paper first. Figure out how to compute the address of segment[index] (except for constant). 

        Then figure out how you move the value of segment[index] into a register (by preference D). 
        Then figure out how to push a value from a register onto the stack. 

        Hint: For pop, you already know how to compute the address of segment[index]. 
        Store it in a temporary register (you can use R13 to R15 freely). Then read the value from the top of the stack, 
        adjust the top of the stack, and then store the value at the location stored in the temporary register.

        """
        
    def WriteArithmetic(self, command):
        """
        Write Hack code for stack arithmetic 'command' (str).
	To be implemented as part of Project 6
	    
		Compiles the arithmetic VM command into the corresponding ASM code. 
        Recall that the operands (one or two, depending on the command) 
        are on the stack and the result of the operation should be placed on the stack.
        The unary and the logical and arithmetic binary operators are simple to compile. 
         The three comparison operators (EQ, LT and GT) do not exist in the assembly language. 
         The corresponding assembly commands are the conditional jumps JEQ, JLT and JGT. 
         You need to implement the VM operations using these conditional jumps. 
         You need two labels, one for the true condition 
         and one for the false condition and you have to put the correct result on the stack.
        """
        if command == T_ADD:    #addera två översta i stacken
            self._WriteCode('@SP,AM=M-1,D=M,@SP,AM=M-1,M=M+D,@SP,M=M+1')


        elif command == T_SUB:  #subtrahera 256-257
            self._WriteCode('@SP,AM=M-1,D=M,@SP,AM=M-1,M=M-D,@SP,M=M+1')

        #nu kan test köras
        elif command == T_NEG:
            self._WriteCode('@SP,AM=M-1,D=M,M=0,M=M-D,@SP,M=M+1')

        elif command == T_EQ:
            true = self._UniqueLabel()
            false = self._UniqueLabel()
            end = self._UniqueLabel()
            self._WriteCode(f'@SP,AM=M-1,D=M,@R13,M=D,@SP,AM=M-1,D=M,@R13,D=M-D,@{true},D;JEQ,@{false},0;JMP,({true}),@SP,A=M,M=-1,@{end},0;JMP,({false}),@SP,A=M,M=0,@{end},0;JMP,({end}),@SP,M=M+1')

        elif command == T_GT:
            true = self._UniqueLabel()
            false = self._UniqueLabel()
            end = self._UniqueLabel()
            self._WriteCode(f'@SP,AM=M-1,D=M,@R13,M=D,@SP,AM=M-1,D=M,@R13,D=D-M,@{true},D;JGT,@{false},D;JLE,({true}),@SP,A=M,M=-1,@{end},0;JMP,({false}),@SP,A=M,M=0,@{end},0;JMP,({end}),@SP,M=M+1')
            
        elif command == T_LT:   #only diff. (comp. to GT) is D=M-D
            true = self._UniqueLabel()
            false = self._UniqueLabel()
            end = self._UniqueLabel()
            self._WriteCode(f'@SP,AM=M-1,D=M,@R13,M=D,@SP,AM=M-1,D=M,@R13,D=M-D,@{true},D;JGT,@{false},D;JLE,({true}),@SP,A=M,M=-1,@{end},0;JMP,({false}),@SP,A=M,M=0,@{end},0;JMP,({end}),@SP,M=M+1')

        elif command == T_AND:
            self._WriteCode('@SP,AM=M-1,D=M,@SP,AM=M-1,M=D&M,@SP,M=M+1')

        elif command == T_OR:
            self._WriteCode('@SP,AM=M-1,D=M,@SP,AM=M-1,M=D|M,@SP,M=M+1')

        elif command == T_NOT:
            self._WriteCode('@SP,AM=M-1,M=!M,@SP,M=M+1')

        
    def WriteInit(self, sysinit = True):
        """
        Write the VM initialization code:
	To be implemented as part of Project 7
        """
        if (debug):
            self.file.write('    // Initialization code\n')


    def WriteLabel(self, label):
        """
        Write Hack code for 'label' VM command.
	To be implemented as part of Project 7

        """

    def WriteGoto(self, label):
        """
        Write Hack code for 'goto' VM command.
	To be implemented as part of Project 7
        """

    def WriteIf(self, label):
        """
        Write Hack code for 'if-goto' VM command.
	To be implemented as part of Project 7
        """
        

    def WriteFunction(self, functionName, numLocals):
        """
        Write Hack code for 'function' VM command.
	To be implemented as part of Project 7
        """


    def WriteReturn(self):
        """
        Write Hack code for 'return' VM command.
	To be implemented as part of Project 7
        """

    def WriteCall(self, functionName, numArgs):
        """
        Write Hack code for 'call' VM command.
	To be implemented as part of Project 7
        """

    

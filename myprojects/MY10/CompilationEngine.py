"""
hjcCompile.py -- CompileEngine class for Hack computer Jack compiler
"""

from Tokens import *
from JackTokenizer import *
from Symbol import *
from VmWriter import *
from XmlFile import *

"""
temp[0]
    do statement -- discard return value
    let statement -- expression value during subscript add
temp[1]
"""

class CompileEngine(object):
    def __init__(self, inputFileName, outputFileName, source=False,
                 xmlFileName=None):
        """
        Initializes the compilation of 'inputFileName' to 'outputFileName'.
        If 'source' is True, source code will be included as comments in the
            output.
        """
        self.vmWriter = VmWriter(outputFileName, source)
        self.inputFileName = inputFileName
        if (xmlFileName):
            self.xmlFile = XmlFile(xmlFileName)
        else:
            self.xmlFile = None
        self.tokenizer = Tokenizer(inputFileName, self.vmWriter, source, self.xmlFile)
        self.symbolTable = SymbolTable()
        self.uniqueNumber = 0
        self.xmlIndent = 0


    def Close(self):
        """
        Finalize the compilation ans close the output file.
        """
        self.vmWriter.Close()
        if (self.xmlFile):
            self.xmlFile.Close()
        

    def CompileClass(self):
        """
        Compiles <class> :=
            'class' <class-name> '{' <class-var-dec>* <subroutine-dec>* '}'

        The tokenizer is expected to be positionsed at the beginning of the
        file.
        """
        self._WriteXmlTag('<class>\n')

        self._NextToken()
        self._ExpectKeyword(KW_CLASS)
        self._WriteXml('keyword', 'class')
        self._NextToken()

        self.className = self._ExpectIdentifier()
        self._WriteXml('identifier', self.className)
        self._NextToken()
        
        self._ExpectSymbol('{')
        self._WriteXml('symbol', '{')
        self._NextToken()

        while True:
            if self.tokenizer.TokenType() != TK_KEYWORD:
                break
            if self.tokenizer.Keyword() not in (KW_STATIC, KW_FIELD):
                break
            self._CompileClassVarDec();

        while True:
            if self.tokenizer.TokenType() != TK_KEYWORD:
                break
            if self.tokenizer.Keyword() not in (KW_CONSTRUCTOR, KW_FUNCTION,
                                              KW_METHOD):
                break
            self._CompileSubroutine();

        self._ExpectSymbol('}')
        self._WriteXml('symbol', '}')
        
        self._WriteXmlTag('</class>\n')
        if self.tokenizer.Advance():
            self._RaiseError('Junk after end of class definition')


    def _CompileClassVarDec(self):
        """
        Compiles <class-var-dec> :=
            ('static' | 'field') <type> <var-name> (',' <var-name>)* ';'

        ENTRY: Tokenizer positioned on the initial keyword.
        EXIT:  Tokenizer positioned after final ';'.
        """
        self._WriteXmlTag('<classVarDec>\n')
        self._ExpectKeyword((KW_STATIC, KW_FIELD))
        if (self.tokenizer.Keyword() == KW_STATIC):
            variableKind = SYMK_STATIC
        else:
            variableKind = SYMK_FIELD
        self._WriteXml('keyword', self.tokenizer.KeywordStr())
        self._NextToken()
        
        if self.tokenizer.TokenType() == TK_KEYWORD:
            self._ExpectKeyword((KW_INT, KW_CHAR, KW_BOOLEAN))
            variableType = self.tokenizer.KeywordStr()
            self._WriteXml('keyword', variableType)
        else:
            variableType = self._ExpectIdentifier()
            self._WriteXml('identifier', variableType)

        self._NextToken()
        while True:
            variableName = self._ExpectIdentifier()
            self._WriteXml('identifier', variableName)
            
            self.symbolTable.Define(variableName, variableType, variableKind)
            varScope = self.symbolTable.ScopeOf(variableName)
            varType = self.symbolTable.TypeOf(variableName)
            varKind = self.symbolTable.KindOfStr(variableName)
            varIndex = self.symbolTable.IndexOf(variableName)
            self._WriteXml('SYMBOL-DEF', '%s.%s (%s %s) = %s' % (varScope, 
                variableName, varKind, varType, varIndex))
            
            self._NextToken()
            if self.tokenizer.TokenType() != TK_SYMBOL or \
                    self.tokenizer.Symbol() != ',':
                break
            self._WriteXml('symbol', self.tokenizer.Symbol())
            self._NextToken()

        self._ExpectSymbol(';')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()

        self._WriteXmlTag('</classVarDec>\n')
        


    def _CompileSubroutine(self):
        """
        Compiles <subroutine-dec> :=
            ('constructor' | 'function' | 'method') ('void' | <type>)
            <subroutine-name> '(' <parameter-list> ')' <subroutine-body>
            
        ENTRY: Tokenizer positioned on the initial keyword.
        EXIT:  Tokenizer positioned after <subroutine-body>.
        """
        self._WriteXmlTag('<subroutineDec>\n')
        self.subroutineType = self._ExpectKeyword((KW_CONSTRUCTOR, KW_FUNCTION,
                                              KW_METHOD))
        self._WriteXml('keyword', self.tokenizer.KeywordStr())
        self._NextToken()
        if self.tokenizer.TokenType() == TK_KEYWORD:
            returnType = self._ExpectKeyword((KW_INT, KW_CHAR, KW_BOOLEAN,
                                              KW_VOID))
            returnTypeName = None
            self._WriteXml('keyword', self.tokenizer.KeywordStr())
        else:
            returnTypeName = self._ExpectIdentifier()
            returnType = None
            self._WriteXml('identifier', self.tokenizer.Identifier())

        self._NextToken()
        self.subroutineName = self._ExpectIdentifier()
        self._WriteXml('identifier', self.tokenizer.Identifier())
        self._NextToken()

        self.symbolTable.StartSubroutine()
        self._WriteXml('SYMBOL-SUBROUTINE', self.tokenizer.Symbol())

        self._ExpectSymbol('(')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()

        if self.subroutineType == KW_METHOD:
            # argument 0 is 'this'
            self.symbolTable.Define('~this~', self.className, SYMK_ARG)

        self._CompileParameterList()
        
        self._ExpectSymbol(')')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()

        self._CompileSubroutineBody()
        self._WriteXmlTag('</subroutineDec>\n')


    def _CompileParameterList(self):
        """
        Compiles <parameter-list> :=
            ( <type> <var-name> (',' <type> <var-name>)* )?

        ENTRY: Tokenizer positioned on the initial keyword.
        EXIT:  Tokenizer positioned after <subroutine-body>.
        """
        self._WriteXmlTag('<parameterList>\n')
        
        while True:
            if self.tokenizer.TokenType() == TK_SYMBOL and \
                   self.tokenizer.Symbol() == ')':
                break;
            
            elif self.tokenizer.TokenType() == TK_KEYWORD:
                self._ExpectKeyword((KW_INT, KW_CHAR, KW_BOOLEAN))
                variableType = self.tokenizer.KeywordStr()
                self._WriteXml('keyword', variableType)
            else:
                variableType = self._ExpectIdentifier()
                self._WriteXml('identifier', variableType)
            self._NextToken();

            variableName = self._ExpectIdentifier();
            self._WriteXml('identifier', self.tokenizer.Identifier())

            self.symbolTable.Define(variableName, variableType, SYMK_ARG)
            varScope = self.symbolTable.ScopeOf(variableName)
            varType = self.symbolTable.TypeOf(variableName)
            varKind = self.symbolTable.KindOfStr(variableName)
            varIndex = self.symbolTable.IndexOf(variableName)
            self._WriteXml('SYMBOL-DEF', '%s.%s (%s %s) = %s' % (varScope, 
                variableName, varKind, varType, varIndex))
            
            self._NextToken();

            if self.tokenizer.TokenType() != TK_SYMBOL or \
                   self.tokenizer.Symbol() != ',':
                break
            self._WriteXml('symbol', self.tokenizer.Symbol())
            self._NextToken()
            
        self._WriteXmlTag('</parameterList>\n')
                

    def _CompileSubroutineBody(self):
        """
        Compiles <subroutine-body> :=
            '{' <var-dec>* <statements> '}'

        The tokenizer is expected to be positioned before the {
        ENTRY: Tokenizer positioned on the initial '{'.
        EXIT:  Tokenizer positioned after final '}'.
        """
        self._WriteXmlTag('<subroutineBody>\n')
        
        self._ExpectSymbol('{')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()

        while self.tokenizer.TokenType() == TK_KEYWORD and \
                self.tokenizer.Keyword() == KW_VAR:
            self._CompileVarDec()

        name = '%s.%s' % (self.className, self.subroutineName)
        self.vmWriter.WriteFunction(name, self.symbolTable.VarCount(SYMK_VAR))
        
        if self.subroutineType == KW_METHOD:
            # set this = arg[0]
            self.vmWriter.WritePush(SEG_ARG, 0)
            self.vmWriter.WritePop(SEG_POINTER, 0)
        elif self.subroutineType == KW_CONSTRUCTOR:
            # allocate and initialize this -- note that the OS chokes on
            # alloc(0) so we must alloc 1 word minimum.
            words = self.symbolTable.VarCount(SYMK_FIELD)
            if words == 0:
                words = 1
            self.vmWriter.WritePush(SEG_CONST, words)
            self.vmWriter.WriteCall('Memory.alloc', 1)
            self.vmWriter.WritePop(SEG_POINTER, 0)
        
        self._CompileStatements()

        self._ExpectSymbol('}')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()
        
        self._WriteXmlTag('</subroutineBody>\n')


    def _CompileVarDec(self):
        """
        Compiles <var-dec> :=
            'var' <type> <var-name> (',' <var-name>)* ';'

        ENTRY: Tokenizer positioned on the initial 'var'.
        EXIT:  Tokenizer positioned after final ';'.
        """
        self._WriteXmlTag('<varDec>\n')
        
        storageClass = self._ExpectKeyword(KW_VAR)
        self._WriteXml('keyword', self.tokenizer.KeywordStr())
        self._NextToken()
        
        if self.tokenizer.TokenType() == TK_KEYWORD:
            self._ExpectKeyword((KW_INT, KW_CHAR, KW_BOOLEAN))
            variableType = self.tokenizer.KeywordStr()
            self._WriteXml('keyword', variableType)
        else:
            variableType = self._ExpectIdentifier()
            self._WriteXml('identifier', variableType)
        self._NextToken()

        while True:
            variableName = self._ExpectIdentifier()
            self._WriteXml('identifier', self.tokenizer.Identifier())

            self.symbolTable.Define(variableName, variableType, SYMK_VAR)
            varScope = self.symbolTable.ScopeOf(variableName)
            varType = self.symbolTable.TypeOf(variableName)
            varKind = self.symbolTable.KindOfStr(variableName)
            varIndex = self.symbolTable.IndexOf(variableName)
            self._WriteXml('SYMBOL-DEF', '%s.%s (%s %s) = %s' % (varScope, 
                variableName, varKind, varType, varIndex))

            self._NextToken()
            
            if self.tokenizer.TokenType() != TK_SYMBOL or \
                    self.tokenizer.Symbol() != ',':
                break
            self._WriteXml('symbol', self.tokenizer.Symbol())
            self._NextToken()

        self._ExpectSymbol(';')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()
    
        self._WriteXmlTag('</varDec>\n')


    def _CompileStatements(self):
        """
        Compiles <statements> := (<let-statement> | <if-statement> |
            <while-statement> | <do-statement> | <return-statement>)*

        The tokenizer is expected to be positioned on the first statement
        ENTRY: Tokenizer positioned on the first statement.
        EXIT:  Tokenizer positioned after final statement.
        """
        self._WriteXmlTag('<statements>\n')

        while self.tokenizer.TokenType() == TK_KEYWORD:
            kw = self._ExpectKeyword((KW_DO, KW_IF, KW_LET, KW_RETURN, KW_WHILE))
            if kw == KW_DO:
                self._CompileDo()
            elif kw == KW_IF:
                self._CompileIf()
            elif kw == KW_LET:
                self._CompileLet()
            elif kw == KW_RETURN:
                self._CompileReturn()
            elif kw == KW_WHILE:
                self._CompileWhile()
            
        self._WriteXmlTag('</statements>\n')


    def _CompileLet(self):
        """
        Compiles <let-statement> :=
            'let' <var-name> ('[' <expression> ']')? '=' <expression> ';'

        ENTRY: Tokenizer positioned on the first keyword.
        EXIT:  Tokenizer positioned after final ';'.
        """
        self._WriteXmlTag('<letStatement>\n')

        self._ExpectKeyword(KW_LET)
        self._WriteXml('keyword', self.tokenizer.KeywordStr())
        self._NextToken()

        variableName = self._ExpectIdentifier()
        self._WriteXml('identifier', self.tokenizer.Identifier())
        self._NextToken()
        
        variableSubscript = False
        sym = self._ExpectSymbol('[=')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()

        if sym == '[':
            variableSubscript = True
            self._CompileExpression()
            # subscript on stack
            
            self._ExpectSymbol(']')
            self._WriteXml('symbol', self.tokenizer.Symbol())
            self._NextToken()
            
            self._ExpectSymbol('=')
            self._WriteXml('symbol', self.tokenizer.Symbol())
            self._NextToken()

        self._CompileExpression()
        # expression result on stack
        
        if not variableSubscript:
            variableKind = self.symbolTable.KindOf(variableName)
            if variableKind == None:
                self._RaiseError('identifier "%s" is undefined' % variableName)
            variableIndex = self.symbolTable.IndexOf(variableName)
            variableSegment = self._KindToSegment(variableKind)
            self.vmWriter.WritePop(variableSegment, variableIndex)
        else:
            self.vmWriter.WritePop(SEG_TEMP, 0)     # expression in temp[0]
            # subscript on stack
            self._AccessArray (variableName)
            # 'that' -> array entry
            self.vmWriter.WritePush(SEG_TEMP, 0)
            self.vmWriter.WritePop(SEG_THAT, 0)            
            
        self._ExpectSymbol(';')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()

        self._WriteXmlTag('</letStatement>\n')


    def _AccessArray (self, variableName):
        """
        Add pointer in 'variableName' to subscript on stack.
        Set 'that' pointer to array entry.
        """
        variableKind = self.symbolTable.KindOf(variableName)
        if variableKind == None:
            self._RaiseError('identifier "%s" is undefined' % variableName)
        variableIndex = self.symbolTable.IndexOf(variableName)
        variableSegment = self._KindToSegment(variableKind)

        self.vmWriter.WritePush(variableSegment, variableIndex)
        self.vmWriter.WriteArithmetic(OP_ADD)
        self.vmWriter.WritePop(SEG_POINTER, 1)  # &var[sub] in 'that'


    def _KindToSegment(self, kind):
        return (SEG_STATIC, SEG_THIS, SEG_ARG, SEG_LOCAL)[kind]


    def _CompileDo(self):
        """
        Compiles <do-statement> := 'do' <subroutine-call> ';'
        
        <subroutine-call> := (<subroutine-name> '(' <expression-list> ')') |
            ((<class-name> | <var-name>) '.' <subroutine-name> '('
            <expression-list> ')')

        <*-name> := <identifier>

        ENTRY: Tokenizer positioned on the first keyword.
        EXIT:  Tokenizer positioned after final ';'.
        """
        self._WriteXmlTag('<doStatement>\n')

        self._ExpectKeyword(KW_DO)
        self._WriteXml('keyword', self.tokenizer.KeywordStr())
        self._NextToken()

        self._CompileCall()

        self._ExpectSymbol(';')
        self._WriteXml('symbol', self.tokenizer.Symbol())

        self.vmWriter.WritePop(SEG_TEMP, 0)
        self._NextToken()

        self._WriteXmlTag('</doStatement>\n')


    def _CompileCall(self, subroutineName=None):
        """
        <subroutine-call> := (<subroutine-name> '(' <expression-list> ')') |
            ((<class-name> | <var-name>) '.' <subroutine-name> '('
            <expression-list> ')')

        <*-name> := <identifier>

        ENTRY: Tokenizer positioned on the first identifier.
             If 'subroutineName' is supplied, tokenizer is on the '.' or the '('
        EXIT:  Tokenizer positioned after final ';'.
        """
        objectName = None

        #class.function(blabla)

        #className|varName  (when tokenName doesnt exist)
        if subroutineName == None:  
            subroutineName = self._ExpectIdentifier() #subroutineName = class
            self._NextToken()


        self._WriteXml('identifier', subroutineName)
        
        # . eller (
        sym = self._ExpectSymbol('.(')
        self._WriteXml('symbol', self.tokenizer.Symbol()) # . eller (
        self._NextToken()
        
        if sym == '.':
            objectName = subroutineName #objectName = class
            subroutineName = self._ExpectIdentifier() #subroutineName = function
            self._WriteXml('identifier', self.tokenizer.Identifier()) #function
            self._NextToken()


            #Anteckningar
                #self.className() #HÄMTAR NAMN PÅ CLASS
            #each symbol NOT FOUND in the symbol tables can be assumed to be either
            #a subroutine name or a class name


            # (
            sym = self._ExpectSymbol('(')
            self._WriteXml('symbol', self.tokenizer.Symbol())
            self._NextToken()


            if self.symbolTable.IndexOf(objectName) != None:
                nArgs = 0
                if self.symbolTable.KindOf(objectName) == SYMK_VAR: #PUSH LOCAL
                    self.vmWriter.WritePush(SEG_LOCAL, self.symbolTable.IndexOf(objectName))
                    nArgs = 1
                elif self.symbolTable.KindOf(objectName) == SYMK_ARG: #PUSH ARGUMENT
                    self.vmWriter.WritePush(SEG_ARG, self.symbolTable.IndexOf(objectName))
                    nArgs = 1
                
                nArgs += self._CompileExpressionList()


                self.vmWriter.WriteCall(f"{self.symbolTable.TypeOf(objectName)}.{subroutineName}", nArgs)
            else:
                nArgs = self._CompileExpressionList()
                self.vmWriter.WriteCall(f"{objectName}.{subroutineName}", nArgs)

        else:
            nArgs = 0
            if self.subroutineType == KW_CONSTRUCTOR:   #PUSH POINTER 0
                self.vmWriter.WritePush(SEG_POINTER, 0)
                nArgs = 1
            nArgs += self._CompileExpressionList()
            self.vmWriter.WriteCall(f"{self.className}.{subroutineName}", nArgs)



        #5.6 11:30. Compiler generates no code - it creates the class level symbol table

        
        # )
        self._ExpectSymbol(')')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()
        

        
        


    def _CompileReturn(self):
        """
        Compiles <return-statement> :=
            'return' <expression>? ';'

        ENTRY: Tokenizer positioned on the first keyword.
        EXIT:  Tokenizer positioned after final ';'.
        """
        self._WriteXmlTag('<returnStatement>\n')
        self._ExpectKeyword(KW_RETURN)
        self._WriteXml('keyword', self.tokenizer.KeywordStr())
        self._NextToken()

        if self.tokenizer.TokenType() != TK_SYMBOL or \
               self.tokenizer.Symbol() != ';':
            self._CompileExpression()
            # expression result on stack
        else:
            self.vmWriter.WritePush(SEG_CONST, 0)

        self._ExpectSymbol(';')
        self._WriteXml('symbol', self.tokenizer.Symbol())

        self.vmWriter.WriteReturn()
        self._NextToken()
        
        self._WriteXmlTag('</returnStatement>\n')


    def _CompileIf(self):
        """
        Compiles <if-statement> :=
            'if' '(' <expression> ')' '{' <statements> '}' ( 'else'
            '{' <statements> '}' )?

        ENTRY: Tokenizer positioned on the first keyword.
        EXIT:  Tokenizer positioned after final '}'.
        """
        self._WriteXmlTag('<ifStatement>\n')

        self._ExpectKeyword(KW_IF)
        self._WriteXml('keyword', self.tokenizer.KeywordStr())
        self._NextToken()

        self._ExpectSymbol('(')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()

        self._CompileExpression()
        
        trueLabel = self._UniqueLabel()
        endIfLabel = self._UniqueLabel()
        elseLabel = self._UniqueLabel() #L3
        
        self.vmWriter.WriteIf(trueLabel)    #if goto L1        
        self.vmWriter.WriteGoto(endIfLabel) #goto L2       
        self.vmWriter.WriteLabel(trueLabel) #label L1      

        self._ExpectSymbol(')')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()

        self._ExpectSymbol('{')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()

        self._CompileStatements()
        
        
        
        self._ExpectSymbol('}')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()

        if self.tokenizer.Keyword() == KW_ELSE:
            self.vmWriter.WriteGoto(elseLabel) #goto L3 (goto the end)


        self.vmWriter.WriteLabel(endIfLabel) #label L2


        if self.tokenizer.Keyword() == KW_ELSE:
            self._ExpectKeyword(KW_ELSE) #edited
            self._WriteXml('keyword', 'else')
            self._NextToken()

            #copied --------------------------------------------------
            self._ExpectSymbol('{')
            self._WriteXml('symbol', self.tokenizer.Symbol())
            self._NextToken()

            self._CompileStatements()

            #VM-------------------------------------------------------
            self.vmWriter.WriteLabel(elseLabel) #label L3 (the end)
            
            #VM-------------------------------------------------------

            self._ExpectSymbol('}')
            self._WriteXml('symbol', self.tokenizer.Symbol())
            self._NextToken()

            #copied --------------------------------------------------

        
        self._WriteXmlTag('</ifStatement>\n')
        pass


    def _UniqueLabel(self):
        """
        Return a label that is unique in this compilation unit.
        """
        self.uniqueNumber += 1
        return 'L' + str(self.uniqueNumber)


    def _CompileWhile(self):
        """
        Compiles <while-statement> :=
            'while' '(' <expression> ')' '{' <statements> '}'

        ENTRY: Tokenizer positioned on the first keyword.
        EXIT:  Tokenizer positioned after final '}'.
        """
        self._WriteXmlTag('<whileStatement>\n')

        self._ExpectKeyword(KW_WHILE)
        self._WriteXml('keyword', self.tokenizer.KeywordStr())
        repeatLabel = self._UniqueLabel()
        self.vmWriter.WriteLabel(repeatLabel)
        self._NextToken()

        self._ExpectSymbol('(')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()

        self._CompileExpression()
        continueLabel = self._UniqueLabel()
        breakLabel = self._UniqueLabel()
        
        self.vmWriter.WriteIf(continueLabel)
        self.vmWriter.WriteGoto(breakLabel)
        self.vmWriter.WriteLabel(continueLabel)

        self._ExpectSymbol(')')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()

        self._ExpectSymbol('{')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()

        self._CompileStatements()
        self.vmWriter.WriteGoto(repeatLabel)
        self.vmWriter.WriteLabel(breakLabel)

        self._ExpectSymbol('}')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()
        
        self._WriteXmlTag('</whileStatement>\n')


    def _CompileExpression(self):
        """
        Compiles <expression> :=
            <term> (op <term)*

        The tokenizer is expected to be positioned on the expression.
        ENTRY: Tokenizer positioned on the expression.
        EXIT:  Tokenizer positioned after the expression.
        """
        self._WriteXmlTag('<expression>\n')

        self._CompileTerm()
        # first term on stack

        while (self.tokenizer.TokenType() == TK_SYMBOL and \
                self.tokenizer.Symbol() in '+-*/&|<>='):
            operator = self.tokenizer.Symbol()
            self._WriteXml('symbol', self.tokenizer.Symbol())
            self._NextToken()
               
            self._CompileTerm()
            # next term on stack

            if operator == '+':
                self.vmWriter.WriteArithmetic(OP_ADD)
            elif operator == '-':
                self.vmWriter.WriteArithmetic(OP_SUB)
            elif operator == '*':
                self.vmWriter.WriteCall('Math.multiply', 2)
            elif operator == '/':
                self.vmWriter.WriteCall('Math.divide', 2)
            elif operator == '&':
                self.vmWriter.WriteArithmetic(OP_AND)
            elif operator == '|':
                self.vmWriter.WriteArithmetic(OP_OR)
            elif operator == '<':
                self.vmWriter.WriteArithmetic(OP_LT)
            elif operator == '>':
                self.vmWriter.WriteArithmetic(OP_GT)
            elif operator == '=':
                self.vmWriter.WriteArithmetic(OP_EQ)
            # result on stack
        
        self._WriteXmlTag('</expression>\n')


    def _CompileTerm(self):
        """
        Compiles a <term> :=
            <int-const> | <string-const> | <keyword-const> | <var-name> |
            (<var-name> '[' <expression> ']') | <subroutine-call> |
            ( '(' <expression> ')' ) | (<unary-op> <term>)

        ENTRY: Tokenizer positioned on the term.
        EXIT:  Tokenizer positioned after the term.
        """
        self._WriteXmlTag('<term>\n')

        if self.tokenizer.TokenType() == TK_INT_CONST:
            self._WriteXml('integerConstant', str(self.tokenizer.IntVal()))
            self.vmWriter.WritePush(SEG_CONST, self.tokenizer.IntVal())
            self._NextToken()
            
        elif self.tokenizer.TokenType() == TK_STRING_CONST:
            self._WriteXml('stringConstant', self.tokenizer.StringVal())
            value = self.tokenizer.StringVal()

            self.vmWriter.WritePush(SEG_CONST, len(value))
            self.vmWriter.WriteCall('String.new', 1)
            # pointer to string on stack
            while len(value):
                self.vmWriter.WritePush(SEG_CONST, ord(value[0]))
                self.vmWriter.WriteCall('String.appendChar', 2)
                # pointer to string on stack
                value = value[1:]
            
            self._NextToken()
            
        elif self.tokenizer.TokenType() == TK_KEYWORD and \
                self.tokenizer.Keyword() in (KW_FALSE, KW_NULL, KW_THIS, KW_TRUE):
            self._WriteXml('keyword', self.tokenizer.KeywordStr())

            if self.tokenizer.Keyword() == KW_THIS:
                self.vmWriter.WritePush(SEG_POINTER, 0)
            else:
                self.vmWriter.WritePush(SEG_CONST, 0)
                if self.tokenizer.Keyword() == KW_TRUE:
                    self.vmWriter.WriteArithmetic(OP_NOT)
            
            self._NextToken()

        elif self.tokenizer.TokenType() == TK_SYMBOL and \
                self.tokenizer.Symbol() in '-~':
            self._WriteXml('symbol', self.tokenizer.Symbol())
            if self.tokenizer.Symbol() == '-':
                operator = OP_NEG
            else:
                operator = OP_NOT
            self._NextToken()
            
            self._CompileTerm()
            self.vmWriter.WriteArithmetic(operator)
            
        elif self.tokenizer.TokenType() == TK_SYMBOL and \
                self.tokenizer.Symbol() == '(':
            self._WriteXml('symbol', self.tokenizer.Symbol())
            self._NextToken()
            
            self._CompileExpression()
            # result of (expr) on stack
            
            self._ExpectSymbol(')')
            self._WriteXml('symbol', self.tokenizer.Symbol())
            self._NextToken()

        else:
            variable = self._ExpectIdentifier()
            self._NextToken()

            if self.tokenizer.TokenType() == TK_SYMBOL and \
                    self.tokenizer.Symbol() == '[':
                # identifier[expression]
                self._WriteXml('identifier', variable)
                self._WriteXml('symbol', self.tokenizer.Symbol())
                self._NextToken()
            
                self._CompileExpression()
                # subscript on stack
                self._AccessArray (variable)
                # 'that' -> array entry
                self.vmWriter.WritePush(SEG_THAT, 0)                            

                self._ExpectSymbol(']')
                self._WriteXml('symbol', self.tokenizer.Symbol())
                self._NextToken()
                
            elif self.tokenizer.TokenType() == TK_SYMBOL and \
                    self.tokenizer.Symbol() in '.(':
                # identifier(arglist)
                # identifier.identifier(arglist)
                self._CompileCall(variable)

            else:
                # identifier
                self._WriteXml('identifier', variable)

                variableKind = self.symbolTable.KindOf(variable)
                if variableKind == None:
                    self._RaiseError('identifier "%s" is undefined' % variable)
                variableIndex = self.symbolTable.IndexOf(variable)
                variableSegment = self._KindToSegment(variableKind)
                self.vmWriter.WritePush(variableSegment, variableIndex)
                
                # no self._NextToken() -- already there

        self._WriteXmlTag('</term>\n')


    def _CompileExpressionList(self):
        """
        Compiles <expression-list> :=
            (<expression> (',' <expression>)* )?

        ENTRY: Tokenizer positioned on the first expression.
        EXIT:  Tokenizer positioned after the last expression.

        Returns number of expressions parsed.
        """
        self._WriteXmlTag('<expressionList>\n')

        numExpr = 0
        while True:
            if self.tokenizer.TokenType() == TK_SYMBOL and \
                    self.tokenizer.Symbol() == ')':
                break
            
            self._CompileExpression()
            numExpr += 1
            
            if self.tokenizer.TokenType() != TK_SYMBOL or \
                    self.tokenizer.Symbol() != ',':
                break

            self._WriteXml('symbol', self.tokenizer.Symbol())
            self._NextToken()
        
        self._WriteXmlTag('</expressionList>\n')
        return numExpr


    
    def _WriteXmlTag(self, tag):
        if self.xmlFile:
            if '/' in tag:
                self.xmlIndent -= 1
            self.xmlFile.Write('  ' * self.xmlIndent)
            self.xmlFile.Write(tag)
            if '/' not in tag:
                self.xmlIndent += 1


    def _WriteXml(self, tag, value):
        if self.xmlFile:
            self.xmlFile.Write('  ' * self.xmlIndent)
            self.xmlFile.WriteXml(tag, value)


    def _ExpectKeyword(self, keywords):
        """
        Parse the next token.  It is expected to be one of 'keywords'.
        'keywords' may be a keywordID or a tuple of keywordIDs.

        Returns the keyword parsed or raises an error.
        """
        if not self.tokenizer.TokenType() == TK_KEYWORD:
            self._RaiseError('Expected '+self._KeywordStr(keywords)+', got '+
                             self.tokenizer.TokenTypeStr())
        if type(keywords) != tuple:
            keywords = (keywords,)
        if self.tokenizer.Keyword() in keywords:
            return self.tokenizer.Keyword()
        self._RaiseError('Expected '+self._KeywordStr(keywords)+', got '+
                         self._KeywordStr(self.tokenizer.Keyword()))


    def _ExpectIdentifier(self):
        """
        Parse the next token.  It is expected to be an identifier.

        Returns the identifier parsed or raises an error.
        """
        if not self.tokenizer.TokenType() == TK_IDENTIFIER:
            self._RaiseError('Expected <identifier>, got '+
                             self.tokenizer.TokenTypeStr())
        return self.tokenizer.Identifier()
        

    def _ExpectSymbol(self, symbols):
        """
        Parse the next token.  It is expected to be one of 'symbols'.
        'symbols' is a string of one or more legal symbols.

        Returns the symbol parsed or raises an error.
        """
        if not self.tokenizer.TokenType() == TK_SYMBOL:
            self._RaiseError('Expected '+self._SymbolStr(symbols)+', got '+
                             self.tokenizer.TokenTypeStr())
        if self.tokenizer.Symbol() in symbols:
            return self.tokenizer.Symbol()
        self._RaiseError('Expected '+self._SymbolStr(symbols)+', got '+
                         self._SymbolStr(self.tokenizer.Symbol()))
        'Keyword'

    def _RaiseError(self, error, fatal=True):
        if fatal:
            FatalError(error, self.inputFileName, self.tokenizer.LineNumber(),
                       self.tokenizer.LineStr())
        else:
            Error(error, self.inputFileName, self.tokenizer.LineNumber(),
                  self.tokenizer.LineStr())
        

    def _KeywordStr(self, keywords):
        if type(keywords) != tuple:
            return '"' + self.tokenizer.KeywordStr(keywords) + '"'
        ret = ''
        for kw in keywords:
            if len(ret):
                ret += ', '
            ret += '"' + self.tokenizer.KeywordStr(kw) + '"'
        if len(keywords) > 1:
            ret = 'one of (' + ret + ')'
        return ret
        
        
    def _SymbolStr(self, symbols):
        if type(symbols) != tuple:
            return '"' + symbols + '"'
        ret = ''
        for symbol in symbols:
            if len(ret):
                ret += ', '
            ret += '"' + symbol + '"'
        if len(symbols) > 1:
            ret = 'one of (' + ret + ')'
        return ret
        
        
    def _NextToken(self):
        if not self.tokenizer.Advance():
            self._RaiseError('Premature EOF')

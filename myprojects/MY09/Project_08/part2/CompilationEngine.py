"""
hjcCompile.py -- CompileEngine class for Hack computer Jack compiler
"""

from Tokens import *
from JackTokenizer import *
from OutputFile import *

xml = True  # Enable _WriteXml...() functions


class CompileEngine(object):
    def __init__(self, inputFileName, outputFileName, source=False, debug=False):
        """
        Initializes the compilation of 'inputFileName' to 'outputFileName'.
        If 'source' is True, source code will be included as comments in the
            output.
        If 'debug' is True, ...
        """
        self.inputFileName = inputFileName
        self.outputFile = OutputFile(outputFileName)
        self.tokenizer = Tokenizer(inputFileName, self.outputFile, source)
        self.xmlIndent = 0


    def Close(self):
        """
        Finalize the compilation ans close the output file.
        """
        self.outputFile.Close()
        

    def CompileClass(self):
        """
        Compiles <class> :=
            'class' <class-name> '{' <class-var-dec>* <subroutine-dec>* '}'
        """
        self._WriteXmlTag('<class>\n')

        self._NextToken()
        self._ExpectKeyword(KW_CLASS)
        self._WriteXml('keyword', 'class')
        self._NextToken()

        className = self._ExpectIdentifier()
        self._WriteXml('identifier', className)
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

        ENTRY: JackTokenizer positioned on the initial Keyword.
        EXIT:  JackTokenizer positioned after final ';'.
        """
        self._WriteXmlTag('<classVarDec>\n')
        storageClass = self._ExpectKeyword((KW_STATIC, KW_FIELD))
        self._WriteXml('keyword', self.tokenizer.KeywordStr())
        self._NextToken()
        if self.tokenizer.TokenType() == TK_KEYWORD:
            variableType = self._ExpectKeyword((KW_INT, KW_CHAR, KW_BOOLEAN))
            variableTypeName = None
            self._WriteXml('keyword', self.tokenizer.KeywordStr())
        else:
            variableTypeName = self._ExpectIdentifier()
            variableType = None
            self._WriteXml('identifier', self.tokenizer.Identifier())

        self._NextToken()
        while True:
            variableName = self._ExpectIdentifier()
            self._WriteXml('identifier', self.tokenizer.Identifier())
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
            
        ENTRY: JackTokenizer positioned on the initial Keyword.
        EXIT:  JackTokenizer positioned after <subroutine-body>.
        """
            
        self._WriteXmlTag('<subroutineDec>\n')
        subroutineType = self._ExpectKeyword((KW_CONSTRUCTOR, KW_FUNCTION,
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
        
        subroutineName = self._ExpectIdentifier()
        self._WriteXml('identifier', self.tokenizer.Identifier())
        self._NextToken()
        

        self._ExpectSymbol('(')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()

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

        ENTRY: JackTokenizer positioned on the initial Keyword.
        EXIT:  JackTokenizer positioned after <var-name>.
        """
        self._WriteXmlTag('<parameterList>\n')
        
        while True:
            if self.tokenizer.TokenType() == TK_SYMBOL and \
                   self.tokenizer.Symbol() == ')':
                break;
            
            elif self.tokenizer.TokenType() == TK_KEYWORD:
                variableType = self._ExpectKeyword((KW_INT, KW_CHAR, KW_BOOLEAN))
                variableTypeName = None
                self._WriteXml('keyword', self.tokenizer.KeywordStr())
            else:
                variableTypeName = self._ExpectIdentifier()
                variableType = None
                self._WriteXml('identifier', self.tokenizer.Identifier())
            self._NextToken();

            variableName = self._ExpectIdentifier();
            self._WriteXml('identifier', self.tokenizer.Identifier())
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

        ENTRY: JackTokenizer positioned on the initial '{'.
        EXIT:  JackTokenizer positioned after final '}'.
        """
        #
        self._WriteXmlTag('<subroutineBody>\n')
        self._ExpectSymbol('{')
        self._WriteXml('symbol', self.tokenizer.Symbol()) #kan vara symbol, { också
        self._NextToken()

        while self.tokenizer.Keyword() == KW_VAR and self.tokenizer.TokenType() == TK_KEYWORD:
            self._CompileVarDec()

        self._CompileStatements()

        self._ExpectSymbol('}')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()
        self._WriteXmlTag('</subroutineBody>\n')


    def _CompileVarDec(self):
        """
        Compiles <var-dec> :=
            'var' <type> <var-name> (',' <var-name>)* ';'

        ENTRY: JackTokenizer positioned on the initial 'var'.
        EXIT:  JackTokenizer positioned after final ';'.
        """
        self._WriteXmlTag('<varDec>\n')
        
        storageClass = self._ExpectKeyword(KW_VAR)
        self._WriteXml('keyword', self.tokenizer.KeywordStr())
        self._NextToken()
        
        if self.tokenizer.TokenType() == TK_KEYWORD:
            variableType = self._ExpectKeyword((KW_INT, KW_CHAR, KW_BOOLEAN))
            variableTypeName = None
            self._WriteXml('keyword', self.tokenizer.KeywordStr())
        else:
            variableTypeName = self._ExpectIdentifier()
            variableType = None
            self._WriteXml('identifier', self.tokenizer.Identifier())
        self._NextToken()

        while True:
            variableName = self._ExpectIdentifier()
            self._WriteXml('identifier', self.tokenizer.Identifier())
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
        ENTRY: JackTokenizer positioned on the first statement.
        EXIT:  JackTokenizer positioned after final statement.
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

        ENTRY: JackTokenizer positioned on the first Keyword.
        EXIT:  JackTokenizer positioned after final ';'.
        """
        self._WriteXmlTag('<letStatement>\n')

        self._ExpectKeyword(KW_LET)
        self._WriteXml('keyword', self.tokenizer.KeywordStr())
        self._NextToken()

        variableName = self._ExpectIdentifier()
        self._WriteXml('identifier', self.tokenizer.Identifier())
        self._NextToken()
        
        variableSubscript = None
        sym = self._ExpectSymbol('[=')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()

        if sym == '[':
            self._CompileExpression()
            
            self._ExpectSymbol(']')
            self._WriteXml('symbol', self.tokenizer.Symbol())
            self._NextToken()
            
            self._ExpectSymbol('=')
            self._WriteXml('symbol', self.tokenizer.Symbol())
            self._NextToken()

        self._CompileExpression()
        
        self._ExpectSymbol(';')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()

        self._WriteXmlTag('</letStatement>\n')


    def _CompileDo(self):
        """
        Compiles <do-statement> := 'do' <subroutine-call> ';'
        
        <subroutine-call> := (<subroutine-name> '(' <expression-list> ')') |
            ((<class-name> | <var-name>) '.' <subroutine-name> '('
            <expression-list> ')')

        <*-name> := <identifier>

        ENTRY: JackTokenizer positioned on the first Keyword.
        EXIT:  JackTokenizer positioned after final ';'.
        """
        self._WriteXmlTag('<doStatement>\n')

        self._ExpectKeyword(KW_DO)
        self._WriteXml('keyword', self.tokenizer.KeywordStr())
        self._NextToken()

        self._CompileCall()

        self._ExpectSymbol(';')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()

        self._WriteXmlTag('</doStatement>\n')


    def _CompileCall(self, tokenName=None):
        """
        <subroutine-call> := (<subroutine-name> '(' <expression-list> ')') |
            ((<class-name> | <var-name>) '.' <subroutine-name> '('
            <expression-list> ')')

        <*-name> := <identifier>

        ENTRY: JackTokenizer positioned on the first identifier.
            If 'tokenName' is supplied, tokenizer is on the '.' or the '()'
        EXIT:  JackTokenizer positioned after final ')'.
        """
        #tokenname.subroutine ...
        #tokenname ()
        #subroutineName ()

        if tokenName != None:   #if tokenname exists
            #classname|varname (when tokenname exists)
            self._WriteXml('identifier', tokenName)
            #next token isnt needed because functions starts reading one step ahead

            if self.tokenizer.Symbol() == '.':
                #.
                self._ExpectSymbol('.')
                self._WriteXml('symbol', self.tokenizer.Symbol()) #kan också vara symbol, .
                self._NextToken()

                #subroutineName
                subroutineName = self._ExpectIdentifier()
                self._WriteXml('identifier', subroutineName)
                self._NextToken()

        else:
            #className|varName  (when tokenName doesnt exist)
            subroutineName = self._ExpectIdentifier()
            self._WriteXml('identifier', subroutineName)
            self._NextToken()

            #.
            self._ExpectSymbol('.')
            self._WriteXml('symbol', self.tokenizer.Symbol()) #kan också vara symbol, .
            self._NextToken()

            #subroutineName
            subroutineName = self._ExpectIdentifier()
            self._WriteXml('identifier', subroutineName)
            self._NextToken()

        #(
        self._ExpectSymbol('(')
        self._WriteXml('symbol', self.tokenizer.Symbol()) #kan också vara symbol, )
        self._NextToken()

        # expressionList
        self._CompileExpressionList()

        #)
        self._ExpectSymbol(')')
        self._WriteXml('symbol', self.tokenizer.Symbol()) #kan också vara symbol, )
        self._NextToken()


    def _CompileReturn(self):
        """
        Compiles <return-statement> :=
            'return' <expression>? ';'

        ENTRY: JackTokenizer positioned on the first Keyword.
        EXIT:  JackTokenizer positioned after final ';'.
        """
        self._WriteXmlTag('<returnStatement>\n')
        self._ExpectKeyword(KW_RETURN)
        self._WriteXml('keyword', self.tokenizer.KeywordStr())
        self._NextToken()

        if self.tokenizer.TokenType() != TK_SYMBOL or \
               self.tokenizer.Symbol() != ';':
            self._CompileExpression()

        self._ExpectSymbol(';')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()
        
        self._WriteXmlTag('</returnStatement>\n')


    def _CompileIf(self):
        """
        Compiles <if-statement> :=
            'if' '(' <expression> ')' '{' <statements> '}' ( 'else'
            '{' <statements> '}' )?

        ENTRY: JackTokenizer positioned on the first Keyword.
        EXIT:  JackTokenizer positioned after final '}'.
        """
        self._WriteXmlTag('<ifStatement>\n')

        self._ExpectKeyword(KW_IF)
        self._WriteXml('keyword', self.tokenizer.KeywordStr())
        self._NextToken()

        self._ExpectSymbol('(')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()

        self._CompileExpression()

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
            self._ExpectKeyword(KW_ELSE) #edited
            self._WriteXml('keyword', 'else')
            self._NextToken()

            #copied --------------------------------------------------
            self._ExpectSymbol('{')
            self._WriteXml('symbol', self.tokenizer.Symbol())
            self._NextToken()

            self._CompileStatements()

            self._ExpectSymbol('}')
            self._WriteXml('symbol', self.tokenizer.Symbol())
            self._NextToken()
            #copied --------------------------------------------------

        #end if (and else)
        self._WriteXmlTag('</ifStatement>\n')
        pass #ta bort?

        


    def _CompileWhile(self):
        """
        Compiles <while-statement> :=
            'while' '(' <expression> ')' '{' <statements> '}'

        ENTRY: JackTokenizer positioned on the first Keyword.
        EXIT:  JackTokenizer positioned after final '}'.
        """
        self._WriteXmlTag('<whileStatement>\n')

        self._ExpectKeyword(KW_WHILE)
        self._WriteXml('keyword', self.tokenizer.KeywordStr())
        self._NextToken()

        self._ExpectSymbol('(')
        self._WriteXml('symbol', self.tokenizer.Symbol())
        self._NextToken()

        self._CompileExpression()

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
        
        self._WriteXmlTag('</whileStatement>\n')


    def _CompileExpression(self):
        """
        Compiles <expression> :=
            <term> (op <term)*

        The tokenizer is expected to be positioned on the expression.
        ENTRY: JackTokenizer positioned on the expression.
        EXIT:  JackTokenizer positioned after the expression.
        """
        self._WriteXmlTag('<expression>\n')

        self._CompileTerm()

        while (self.tokenizer.TokenType() == TK_SYMBOL and \
                self.tokenizer.Symbol() in '+-*/&|<>='):
            self._WriteXml('symbol', self.tokenizer.Symbol())
            self._NextToken()
               
            self._CompileTerm()            
        
        self._WriteXmlTag('</expression>\n')


    def _CompileTerm(self):
        """
        Compiles a <term> :=
            <int-const> | <string-const> | <Keyword-const> | <var-name> |
            (<var-name> '[' <expression> ']') | <subroutine-call> |
            ( '(' <expression> ')' ) | (<unary-op> <term>)

        ENTRY: JackTokenizer positioned on the term.
        EXIT:  JackTokenizer positioned after the term.
        """
        self._WriteXmlTag('<term>\n')

        if self.tokenizer.TokenType() == TK_INT_CONST:
            self._WriteXml('integerConstant', str(self.tokenizer.IntVal()))
            self._NextToken()
            
        elif self.tokenizer.TokenType() == TK_STRING_CONST:
            self._WriteXml('stringConstant', self.tokenizer.StringVal())
            self._NextToken()
            
        elif self.tokenizer.TokenType() == TK_KEYWORD and \
                self.tokenizer.Keyword() in (KW_FALSE, KW_NULL, KW_THIS, KW_TRUE):
            self._WriteXml('keyword', self.tokenizer.KeywordStr())
            self._NextToken()

        elif self.tokenizer.TokenType() == TK_SYMBOL and \
                self.tokenizer.Symbol() in '-~':
            self._WriteXml('symbol', self.tokenizer.Symbol())
            self._NextToken()
            
            self._CompileTerm()
            
        elif self.tokenizer.TokenType() == TK_SYMBOL and \
                self.tokenizer.Symbol() == '(':
            self._WriteXml('symbol', self.tokenizer.Symbol())
            self._NextToken()
            
            self._CompileExpression()

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
                # no self._NextToken() -- already there

        self._WriteXmlTag('</term>\n')


    def _CompileExpressionList(self):
        """
        Compiles <expression-list> :=
            (<expression> (',' <expression>)* )?

        ENTRY: JackTokenizer positioned on the first expression.
        EXIT:  JackTokenizer positioned after the last expression.
        """
        self._WriteXmlTag('<expressionList>\n')

        while True:
            if self.tokenizer.TokenType() == TK_SYMBOL and \
                    self.tokenizer.Symbol() == ')':
                break
            
            self._CompileExpression()
            
            if self.tokenizer.TokenType() != TK_SYMBOL or \
                    self.tokenizer.Symbol() != ',':
                break

            self._WriteXml('symbol', self.tokenizer.Symbol())
            self._NextToken()
        
        self._WriteXmlTag('</expressionList>\n')



    
    def _WriteXmlTag(self, tag):
        if xml:
            if '/' in tag:
                self.xmlIndent -= 1
            self.outputFile.Write('  ' * self.xmlIndent)
            self.outputFile.Write(tag)
            if '/' not in tag:
                self.xmlIndent += 1


    def _WriteXml(self, tag, value):
        if xml:
            self.outputFile.Write('  ' * self.xmlIndent)
            self.outputFile.WriteXml(tag, value)


    def _ExpectKeyword(self, keywords):
        """
        Parse the next token.  It is expected to be one of 'keywords'.
        'keywords' may be a keywordID or a tuple of keywordIDs.

        Returns the Keyword parsed or raises an error.
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
        

    def _RaiseError(self, error):
        message = '%s line %d:\n  %s\n  %s' % (
                  self.inputFileName, self.tokenizer.LineNumber(),
                  self.tokenizer.LineStr(), error)
        raise HjcError(message)
        

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

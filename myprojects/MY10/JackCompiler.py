#!/usr/bin/python32
"""
hjc.py -- Hack computer Jack compiler
"""

import sys
import os
from Tokens import *
# from JackTokenizer import *
# from XmlFile import *
from CompilationEngine import *

exitCode = 0


def Process(sourceFileName, outputFileName):
    global source, xml, exitCode, verbose
    if verbose:
        print('Processing ' + sourceFileName)

    if xml:
        xmlFileName = outputFileName.replace('.vm', '.xml')
    else:
        xmlFileName = None

    compiler = CompileEngine(sourceFileName, outputFileName, source, xmlFileName)
    compiler.CompileClass()
    compiler.Close()


def ProcessTokenizerTest(sourceFileName, outputFileName):
    global source, xml, verbose
    if verbose:
        print('Processing' + sourceFileName)

    outputFileName = outputFileName.replace('.vm', 'T.xml')
    outputFile = XmlFile(outputFileName, 'tokens')

    tokenizer = Tokenizer(sourceFileName, outputFile, source)
    while tokenizer.Advance():
        PrintToken(tokenizer, outputFile)
    outputFile.Close()


def PrintToken(tokenizer, outputFile):
    token = tokenizer.TokenType()
    if token == TK_KEYWORD:
        outputFile.WriteXml('keyword', tokenizer.KeywordStr())
    elif token == TK_SYMBOL:
        outputFile.WriteXml('symbol', tokenizer.Symbol())
    elif token == TK_IDENTIFIER:
        outputFile.WriteXml('identifier', tokenizer.Identifier())
    elif token == TK_INT_CONST:
        outputFile.WriteXml('integerConstant', str(tokenizer.IntVal()))
    elif token == TK_STRING_CONST:
        outputFile.WriteXml('stringConstant', tokenizer.StringVal())
    else:
        FatalError('Internal error: bad token type')


def Usage():
    print('usage: hjc [options] sourceFile.jack')
    print('    sourceFile may be a directory in which case all .jack files')
    print('    in the directory will be processed to .vm files.')
    print('options:')
    print('    -d writes source as /// comments in .vm files.')
    print('    -x generates parser .xml file.')
    print('    -v[-] turn progress messages on[off]')
    sys.exit(-1)
    

def main():
    global source, xml, exitCode, verbose
    source = False
    xml = False
    verbose = True
    while True:
        if len(sys.argv) >= 2:
            if sys.argv[1] == '-d':
                source = True
                del (sys.argv[1])
                continue
            if sys.argv[1] == '-x':
                xml = True
                del (sys.argv[1])
                continue
            if sys.argv[1] == '-v':
                verbose = True
                del (sys.argv[1])
                continue
            if sys.argv[1] == '-v-':
                verbose = False
                del (sys.argv[1])
                continue
        break
        
    if len(sys.argv) != 2:
        Usage()
        
    sourceName = sys.argv[1]
    if os.path.isdir(sourceName):
        dirName = sourceName
    else:
        dirName = '.'
    
    if os.path.isdir(sourceName):
        # process all .jack files in dir
        dirName = sourceName
        if verbose:
            print('Processing directory' + dirName)
        for sourceName in os.listdir(dirName):
            if os.path.splitext(sourceName)[1].lower() == os.path.extsep + 'jack':
                outName = os.path.splitext(sourceName)[0] + os.path.extsep + 'vm'
                outName = dirName + os.path.sep + outName
                sourceName = dirName + os.path.sep + sourceName
                Process(sourceName, outName)
    else:
        # process single .jack file
        outName = os.path.splitext(sourceName)[0] + os.path.extsep + 'vm'
        outName = dirName + os.path.sep + outName
        Process(sourceName, outName)
    sys.exit(exitCode)

main()

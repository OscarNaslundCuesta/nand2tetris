"""
hjcSymbol.py -- SymbolTable class for Hack computer Jack compiler
"""

from Error import *

SYMK_STATIC = 0     # Symbol 'kinds' -- also indices for self.index[]
SYMK_FIELD  = 1
SYMK_ARG    = 2
SYMK_VAR    = 3

SYMI_TYPE   = 0     # Indices for symbol data tuple
SYMI_KIND   = 1
SYMI_INDEX  = 2


class SymbolTable(object):
    def __init__(self):
        """
        Create a new empty symbol table.
        """
        self.classSymbols = {}
        self.subroutineSymbols = {}
        self.index = [0, 0, 0, 0]


    def StartSubroutine(self):
        """
        Starts a new subroutine scope.
        """
        self.subroutineSymbols = {}
        self.index[SYMK_ARG] = 0
        self.index[SYMK_VAR] = 0
        

    def Define(self, name, symType, symKind):
        """
        Define a new identifier of a given 'name', 'symType' and 'symKind'.
        'symType' is a builtin type name or a class name.
        'symKind' is SYMK_STATIC, SYMK_FIELD, SYMK_ARG or SYMK_VAR.
        """
        table = self._SelectTable(symKind)

        if name in table:
            message = 'SymbolTable.Define: symbol "%s" already defined' % name
            FatalError(message)

        table[name] = (symType, symKind, self.index[symKind])
        self.index[symKind] += 1
        

    def VarCount(self, symKind):
        """
        Return the number of variables of the given 'symKind' already
        defined in the current scope.
        """
        if symKind not in (SYMK_STATIC, SYMK_FIELD, SYMK_ARG, SYMK_VAR):
            message = 'SymbolTable.Define: unknown symKind (%d)' % symKind
            FatalError(message)
        return self.index[symKind]


    def KindOf(self, name):
        """
        Return the 'kind' of identifier 'name' in the current scope.

        If the identifier is unknown in the current scope, returns None.
        """
        return self._ValueOf(name, SYMI_KIND)


    def KindOfStr(self, name):
        return ('static','field','arg','var')[self.KindOf(name)]


    def TypeOf(self, name):
        """
        Return the 'type' of identifier 'name' in the current scope.

        If the identifier is unknown in the current scope, returns None.
        """
        return self._ValueOf(name, SYMI_TYPE)


    def IndexOf(self, name):
        """
        Return the 'index' of identifier 'name' in the current scope.

        If the identifier is unknown in the current scope, returns None.
        """
        return self._ValueOf(name, SYMI_INDEX)

        
    def ScopeOf(self, name):
        """
        Return the scope(s) where identifier 'name' is found.
        """
        scope = ''
        if name in self.subroutineSymbols:
            scope = 'subroutine'
        if name in self.classSymbols:
            if len(scope):
                scope += '+'
            scope += 'class'
        if len(scope)==0:
            scope = 'None'
        return scope

        
    def _SelectTable(self, symKind):
        """
        Internal routine to select either the class symbol table or the
        subroutine symbol table.
        """
        if symKind in (SYMK_STATIC, SYMK_FIELD):
            return self.classSymbols
        elif symKind in (SYMK_ARG, SYMK_VAR):
            return self.subroutineSymbols
        else:
            message = 'SymbolTable.Define: unknown symKind (%d)' % symKind
            FatalError(message)


    def _ValueOf(self, name, si):
        """
        Inernal routine to return a selected value from a symbol.
        """
        if name in self.subroutineSymbols:
            return self.subroutineSymbols[name][si]
        if name in self.classSymbols:
            return self.classSymbols[name][si]
        return None
    

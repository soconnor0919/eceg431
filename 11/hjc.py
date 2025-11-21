import os
import sys


class JackTokenizer:
    # tokenizes Jack source code

    def __init__(self, filename):
        # load and clean Jack file
        self.lines = []
        self.currentLine = ""
        self.lineNumber = 0
        self.inComment = False

        # current token info
        self.currentToken = ""
        self.tokenType = ""

        # Jack language keywords
        self.keywords = {
            "class",
            "constructor",
            "function",
            "method",
            "field",
            "static",
            "var",
            "int",
            "char",
            "boolean",
            "void",
            "true",
            "false",
            "null",
            "this",
            "let",
            "do",
            "if",
            "else",
            "while",
            "return",
        }

        # Jack language symbols
        self.symbols = {
            "{",
            "}",
            "(",
            ")",
            "[",
            "]",
            ".",
            ",",
            ";",
            "+",
            "-",
            "*",
            "/",
            "&",
            "|",
            "<",
            ">",
            "=",
            "~",
        }

        # read file
        with open(filename, "r") as file:
            self.lines = file.readlines()

    def hasMoreTokens(self):
        # check if more tokens available
        # still have content on current line or more lines to process
        return len(self.currentLine) > 0 or self.lineNumber < len(self.lines)

    def advance(self):
        # get next token from input
        while True:
            # check if current line is empty
            if len(self.currentLine) == 0:
                # get new line
                if self.lineNumber >= len(self.lines):
                    # end of file
                    return False

                self.currentLine = self.lines[self.lineNumber]
                self.lineNumber += 1

                # remove newline
                if self.currentLine.endswith("\n"):
                    self.currentLine = self.currentLine[:-1]

                # handle comments
                # remove inline comments
                if "//" in self.currentLine:
                    self.currentLine = self.currentLine[: self.currentLine.index("//")]

                # handle multi-line comments

                if self.inComment:
                    if "*/" in self.currentLine:
                        self.currentLine = self.currentLine[
                            self.currentLine.index("*/") + 2 :
                        ]
                        self.inComment = False
                    else:
                        self.currentLine = ""
                        continue

                if "/*" in self.currentLine:
                    if "*/" in self.currentLine:
                        before = self.currentLine[: self.currentLine.index("/*")]
                        after = self.currentLine[self.currentLine.index("*/") + 2 :]
                        self.currentLine = before + after
                    else:
                        self.currentLine = self.currentLine[
                            : self.currentLine.index("/*")
                        ]
                        self.inComment = True

                self.currentLine = self.currentLine.strip()
                if len(self.currentLine) == 0:
                    continue

            # skip whitespace
            while len(self.currentLine) > 0 and self.currentLine[0] in " \t":
                self.currentLine = self.currentLine[1:]

            if len(self.currentLine) == 0:
                continue

            # check for string constant
            if self.currentLine[0] == '"':
                end = self.currentLine.index('"', 1)
                self.currentToken = self.currentLine[1:end]
                self.tokenType = "STRING_CONST"
                self.currentLine = self.currentLine[end + 1 :]
                return True

            # check for symbols
            if self.currentLine[0] in self.symbols:
                self.currentToken = self.currentLine[0]
                self.tokenType = "SYMBOL"
                self.currentLine = self.currentLine[1:]
                return True

            # check for numbers
            if self.currentLine[0].isdigit():
                i = 0
                while i < len(self.currentLine) and self.currentLine[i].isdigit():
                    i += 1
                self.currentToken = self.currentLine[:i]
                self.tokenType = "INT_CONST"
                self.currentLine = self.currentLine[i:]
                return True

            # check for identifiers/keywords
            if self.currentLine[0].isalpha() or self.currentLine[0] == "_":
                i = 0
                while i < len(self.currentLine) and (
                    self.currentLine[i].isalnum() or self.currentLine[i] == "_"
                ):
                    i += 1
                self.currentToken = self.currentLine[:i]

                if self.currentToken in self.keywords:
                    self.tokenType = "KEYWORD"
                else:
                    self.tokenType = "IDENTIFIER"

                self.currentLine = self.currentLine[i:]
                return True

            # shouldn't reach here with valid Jack code
            self.currentLine = self.currentLine[1:]

    def getTokenType(self):
        # return current token type
        return self.tokenType

    def keyword(self):
        # return keyword (only if token is keyword)
        if self.tokenType == "KEYWORD":
            return self.currentToken
        return None

    def symbol(self):
        # return symbol (only if token is symbol)
        if self.tokenType == "SYMBOL":
            return self.currentToken
        return None

    def identifier(self):
        # return identifier (only if token is identifier)
        if self.tokenType == "IDENTIFIER":
            return self.currentToken
        return None

    def intVal(self):
        # return integer value (only if token is int)
        if self.tokenType == "INT_CONST":
            return int(self.currentToken)
        return None

    def stringVal(self):
        # return string value (only if token is string)
        if self.tokenType == "STRING_CONST":
            return self.currentToken
        return None


class SymbolTable:
    # manages symbol table for Jack compilation

    def __init__(self):
        self.classTable = {}  # class-scope symbols (static, field)
        self.subroutineTable = {}  # subroutine-scope symbols (arg, var)
        self.staticCount = 0
        self.fieldCount = 0
        self.argCount = 0
        self.varCount = 0

    def startSubroutine(self):
        # start a new subroutine scope
        self.subroutineTable = {}
        self.argCount = 0
        self.varCount = 0

    def define(self, name, type_name, kind):
        # define a new identifier
        if kind == "STATIC":
            self.classTable[name] = {
                "type": type_name,
                "kind": kind,
                "index": self.staticCount,
            }
            self.staticCount += 1
        elif kind == "FIELD":
            self.classTable[name] = {
                "type": type_name,
                "kind": kind,
                "index": self.fieldCount,
            }
            self.fieldCount += 1
        elif kind == "ARG":
            self.subroutineTable[name] = {
                "type": type_name,
                "kind": kind,
                "index": self.argCount,
            }
            self.argCount += 1
        elif kind == "VAR":
            self.subroutineTable[name] = {
                "type": type_name,
                "kind": kind,
                "index": self.varCount,
            }
            self.varCount += 1

    def getVarCount(self, kind):
        # return count of variables of given kind
        if kind == "STATIC":
            return self.staticCount
        elif kind == "FIELD":
            return self.fieldCount
        elif kind == "ARG":
            return self.argCount
        elif kind == "VAR":
            return self.varCount
        return 0

    def kindOf(self, name):
        # return the kind of named identifier
        if name in self.subroutineTable:
            return self.subroutineTable[name]["kind"]
        elif name in self.classTable:
            return self.classTable[name]["kind"]
        return "NONE"

    def typeOf(self, name):
        # return the type of named identifier
        if name in self.subroutineTable:
            return self.subroutineTable[name]["type"]
        elif name in self.classTable:
            return self.classTable[name]["type"]
        return None

    def indexOf(self, name):
        # return the index of named identifier
        if name in self.subroutineTable:
            return self.subroutineTable[name]["index"]
        elif name in self.classTable:
            return self.classTable[name]["index"]
        return None


class VMWriter:
    # emits VM commands into a file

    def __init__(self, output_file):
        self.output = open(output_file, "w")

    def writePush(self, segment, index):
        # write a VM push command
        self.output.write(f"push {segment.lower()} {index}\n")

    def writePop(self, segment, index):
        # write a VM pop command
        self.output.write(f"pop {segment.lower()} {index}\n")

    def writeArithmetic(self, command):
        # write a VM arithmetic command
        self.output.write(f"{command.lower()}\n")

    def writeLabel(self, label):
        # write a VM label command
        self.output.write(f"label {label}\n")

    def writeGoto(self, label):
        # write a VM goto command
        self.output.write(f"goto {label}\n")

    def writeIf(self, label):
        # write a VM if-goto command
        self.output.write(f"if-goto {label}\n")

    def writeCall(self, name, nArgs):
        # write a VM call command
        self.output.write(f"call {name} {nArgs}\n")

    def writeFunction(self, name, nLocals):
        # write a VM function command
        self.output.write(f"function {name} {nLocals}\n")

    def writeReturn(self):
        # write a VM return command
        self.output.write("return\n")

    def close(self):
        # close the output file
        self.output.close()


class CompilationEngine:
    # compiles Jack source code to VM code

    def __init__(self, tokenizer, output_file):
        self.tokenizer = tokenizer
        self.vmWriter = VMWriter(output_file)
        self.symbolTable = SymbolTable()
        self.className = ""
        self.labelCount = 0
        self.whileLabelCount = 0
        self.ifLabelCount = 0

    def getNextWhileLabel(self):
        # generate unique while labels
        exp_label = f"WHILE_EXP{self.whileLabelCount}"
        end_label = f"WHILE_END{self.whileLabelCount}"
        self.whileLabelCount += 1
        return exp_label, end_label

    def getNextIfLabel(self):
        # generate unique if labels
        true_label = f"IF_TRUE{self.ifLabelCount}"
        false_label = f"IF_FALSE{self.ifLabelCount}"
        end_label = f"IF_END{self.ifLabelCount}"
        self.ifLabelCount += 1
        return true_label, false_label, end_label

    def compileClass(self):
        # compile a complete class
        # 'class'
        if not self.tokenizer.advance():
            return

        # className
        if not self.tokenizer.advance():
            return
        self.className = self.tokenizer.identifier()

        # '{'
        if not self.tokenizer.advance():
            return

        # classVarDec*
        if not self.tokenizer.advance():
            return
        while (
            self.tokenizer.getTokenType() == "KEYWORD"
            and self.tokenizer.keyword() in ["static", "field"]
        ):
            self.compileClassVarDec()

        # subroutineDec*
        while (
            self.tokenizer.getTokenType() == "KEYWORD"
            and self.tokenizer.keyword() in ["constructor", "function", "method"]
        ):
            self.compileSubroutine()

        # '}'
        # Already at the closing brace

    def compileClassVarDec(self):
        # compile a static or field declaration
        # ('static' | 'field')
        kind = "STATIC" if self.tokenizer.keyword() == "static" else "FIELD"

        # type
        self.tokenizer.advance()
        type_name = self.tokenizer.currentToken

        # varName
        self.tokenizer.advance()
        name = self.tokenizer.identifier()
        self.symbolTable.define(name, type_name, kind)

        # (',' varName)*
        self.tokenizer.advance()
        while (
            self.tokenizer.getTokenType() == "SYMBOL" and self.tokenizer.symbol() == ","
        ):
            self.tokenizer.advance()  # ','
            name = self.tokenizer.identifier()
            self.symbolTable.define(name, type_name, kind)
            self.tokenizer.advance()

        # ';'
        self.tokenizer.advance()

    def compileSubroutine(self):
        # compile a method, function, or constructor
        self.symbolTable.startSubroutine()

        # ('constructor' | 'function' | 'method')
        subroutineType = self.tokenizer.keyword()

        # If method, add 'this' as first argument
        if subroutineType == "method":
            self.symbolTable.define("this", self.className, "ARG")

        # returnType
        self.tokenizer.advance()

        # subroutineName
        self.tokenizer.advance()
        subroutineName = self.tokenizer.identifier()

        # '('
        self.tokenizer.advance()

        # parameterList
        self.tokenizer.advance()
        self.compileParameterList()

        # ')'
        # Already past the closing parenthesis

        # subroutineBody
        self.compileSubroutineBody(subroutineType, subroutineName)

    def compileParameterList(self):
        # compile a parameter list
        if self.tokenizer.getTokenType() == "SYMBOL" and self.tokenizer.symbol() == ")":
            return

        # type
        type_name = self.tokenizer.currentToken

        # varName
        self.tokenizer.advance()
        name = self.tokenizer.identifier()
        self.symbolTable.define(name, type_name, "ARG")

        # (',' type varName)*
        self.tokenizer.advance()
        while (
            self.tokenizer.getTokenType() == "SYMBOL" and self.tokenizer.symbol() == ","
        ):
            self.tokenizer.advance()  # ','
            type_name = self.tokenizer.currentToken
            self.tokenizer.advance()
            name = self.tokenizer.identifier()
            self.symbolTable.define(name, type_name, "ARG")
            self.tokenizer.advance()

    def compileSubroutineBody(self, subroutineType, subroutineName):
        # compile subroutine body
        # '{'
        self.tokenizer.advance()

        # varDec* - need to advance to first token after '{'
        if not (
            self.tokenizer.getTokenType() == "KEYWORD"
            and self.tokenizer.keyword() == "var"
        ):
            self.tokenizer.advance()

        while (
            self.tokenizer.getTokenType() == "KEYWORD"
            and self.tokenizer.keyword() == "var"
        ):
            self.compileVarDec()

        # Write function declaration
        nLocals = self.symbolTable.getVarCount("VAR")
        functionName = f"{self.className}.{subroutineName}"
        self.vmWriter.writeFunction(functionName, nLocals)

        # Handle constructor/method setup
        if subroutineType == "constructor":
            # Allocate memory for object
            nFields = self.symbolTable.getVarCount("FIELD")
            self.vmWriter.writePush("constant", nFields)
            self.vmWriter.writeCall("Memory.alloc", 1)
            self.vmWriter.writePop("pointer", 0)
        elif subroutineType == "method":
            # Set 'this' pointer
            self.vmWriter.writePush("argument", 0)
            self.vmWriter.writePop("pointer", 0)

        # statements
        self.compileStatements()

        # '}'
        if self.tokenizer.getTokenType() == "SYMBOL" and self.tokenizer.symbol() == "}":
            self.tokenizer.advance()

    def compileVarDec(self):
        # compile a var declaration
        # 'var'
        self.tokenizer.advance()

        # type
        type_name = self.tokenizer.currentToken

        # varName
        self.tokenizer.advance()
        name = self.tokenizer.identifier()
        self.symbolTable.define(name, type_name, "VAR")

        # (',' varName)*
        self.tokenizer.advance()
        while (
            self.tokenizer.getTokenType() == "SYMBOL" and self.tokenizer.symbol() == ","
        ):
            self.tokenizer.advance()  # ','
            name = self.tokenizer.identifier()
            self.symbolTable.define(name, type_name, "VAR")
            self.tokenizer.advance()

        # ';'
        if self.tokenizer.getTokenType() == "SYMBOL" and self.tokenizer.symbol() == ";":
            self.tokenizer.advance()

    def compileStatements(self):
        # compile a sequence of statements
        # We should already be positioned at the first statement token
        while (
            self.tokenizer.getTokenType() == "KEYWORD"
            and self.tokenizer.keyword() in ["let", "if", "while", "do", "return"]
        ):
            keyword = self.tokenizer.keyword()
            if keyword == "let":
                self.compileLet()
            elif keyword == "if":
                self.compileIf()
            elif keyword == "while":
                self.compileWhile()
            elif keyword == "do":
                self.compileDo()
            elif keyword == "return":
                self.compileReturn()

    def compileLet(self):
        # compile a let statement
        # 'let'
        self.tokenizer.advance()

        # varName
        varName = self.tokenizer.identifier()

        # Check for array access
        self.tokenizer.advance()
        isArray = (
            self.tokenizer.getTokenType() == "SYMBOL" and self.tokenizer.symbol() == "["
        )

        if isArray:
            # Push array base address
            self.pushIdentifier(varName)

            # '['
            self.tokenizer.advance()

            # expression (array index)
            self.compileExpression()

            # ']'
            self.tokenizer.advance()

            # Add base + index
            self.vmWriter.writeArithmetic("add")

        # '='
        self.tokenizer.advance()

        # expression (value to assign)
        self.compileExpression()

        if isArray:
            # Pop value to temp, set that pointer, pop value to that 0
            self.vmWriter.writePop("temp", 0)
            self.vmWriter.writePop("pointer", 1)
            self.vmWriter.writePush("temp", 0)
            self.vmWriter.writePop("that", 0)
        else:
            # Simple assignment - pop the expression result to the variable
            self.popIdentifier(varName)

        # ';'
        if self.tokenizer.getTokenType() == "SYMBOL" and self.tokenizer.symbol() == ";":
            self.tokenizer.advance()

    def compileIf(self):
        # compile an if statement
        trueLabel, falseLabel, endLabel = self.getNextIfLabel()

        # 'if'
        self.tokenizer.advance()

        # '('
        self.tokenizer.advance()

        # expression
        self.compileExpression()

        # ')'
        self.tokenizer.advance()

        # Jump to true branch if condition is true
        self.vmWriter.writeIf(trueLabel)
        self.vmWriter.writeGoto(falseLabel)
        self.vmWriter.writeLabel(trueLabel)

        # '{'
        self.tokenizer.advance()

        # statements
        self.compileStatements()

        # '}'
        self.tokenizer.advance()

        # ('else' '{' statements '}')?
        if (
            self.tokenizer.getTokenType() == "KEYWORD"
            and self.tokenizer.keyword() == "else"
        ):
            # Jump over else part
            self.vmWriter.writeGoto(endLabel)
            self.vmWriter.writeLabel(falseLabel)
            self.tokenizer.advance()  # 'else'
            self.tokenizer.advance()  # '{'
            self.compileStatements()
            self.tokenizer.advance()  # '}'
            self.vmWriter.writeLabel(endLabel)
        else:
            self.vmWriter.writeLabel(falseLabel)

    def compileWhile(self):
        # compile a while statement
        expLabel, endLabel = self.getNextWhileLabel()

        # Start of loop
        self.vmWriter.writeLabel(expLabel)

        # 'while'
        self.tokenizer.advance()

        # '('
        self.tokenizer.advance()

        # expression
        self.compileExpression()

        # ')'
        self.tokenizer.advance()

        # Negate condition and jump to end
        self.vmWriter.writeArithmetic("not")
        self.vmWriter.writeIf(endLabel)

        # '{'
        self.tokenizer.advance()

        # statements
        self.compileStatements()

        # '}'
        self.tokenizer.advance()

        # Jump back to start
        self.vmWriter.writeGoto(expLabel)

        # End label
        self.vmWriter.writeLabel(endLabel)

    def compileDo(self):
        # compile a do statement
        # 'do'
        self.tokenizer.advance()

        # subroutineCall
        self.compileSubroutineCall()

        # Pop return value (do statements ignore return value)
        self.vmWriter.writePop("temp", 0)

        # ';'
        if self.tokenizer.getTokenType() == "SYMBOL" and self.tokenizer.symbol() == ";":
            self.tokenizer.advance()

    def compileReturn(self):
        # compile a return statement
        # 'return'
        self.tokenizer.advance()

        # expression?
        if not (
            self.tokenizer.getTokenType() == "SYMBOL" and self.tokenizer.symbol() == ";"
        ):
            self.compileExpression()
        else:
            # Void function returns 0
            self.vmWriter.writePush("constant", 0)

        self.vmWriter.writeReturn()

        # ';'
        if self.tokenizer.getTokenType() == "SYMBOL" and self.tokenizer.symbol() == ";":
            self.tokenizer.advance()

    def compileExpression(self):
        # compile an expression
        # term
        self.compileTerm()

        # (op term)*
        while self.tokenizer.getTokenType() == "SYMBOL" and self.tokenizer.symbol() in [
            "+",
            "-",
            "*",
            "/",
            "&",
            "|",
            "<",
            ">",
            "=",
        ]:
            op = self.tokenizer.symbol()
            self.tokenizer.advance()
            self.compileTerm()

            # Write arithmetic operation
            if op == "+":
                self.vmWriter.writeArithmetic("add")
            elif op == "-":
                self.vmWriter.writeArithmetic("sub")
            elif op == "*":
                self.vmWriter.writeCall("Math.multiply", 2)
            elif op == "/":
                self.vmWriter.writeCall("Math.divide", 2)
            elif op == "&":
                self.vmWriter.writeArithmetic("and")
            elif op == "|":
                self.vmWriter.writeArithmetic("or")
            elif op == "<":
                self.vmWriter.writeArithmetic("lt")
            elif op == ">":
                self.vmWriter.writeArithmetic("gt")
            elif op == "=":
                self.vmWriter.writeArithmetic("eq")

    def compileTerm(self):
        # compile a term
        if self.tokenizer.getTokenType() == "INT_CONST":
            # integerConstant
            self.vmWriter.writePush("constant", self.tokenizer.intVal())
            self.tokenizer.advance()

        elif self.tokenizer.getTokenType() == "STRING_CONST":
            # stringConstant
            string = self.tokenizer.stringVal()
            # Create string object
            self.vmWriter.writePush("constant", len(string))
            self.vmWriter.writeCall("String.new", 1)
            # Append each character
            for char in string:
                self.vmWriter.writePush("constant", ord(char))
                self.vmWriter.writeCall("String.appendChar", 2)
            self.tokenizer.advance()

        elif self.tokenizer.getTokenType() == "KEYWORD":
            # keywordConstant
            keyword = self.tokenizer.keyword()
            if keyword == "true":
                self.vmWriter.writePush("constant", 0)
                self.vmWriter.writeArithmetic("not")
            elif keyword in ["false", "null"]:
                self.vmWriter.writePush("constant", 0)
            elif keyword == "this":
                self.vmWriter.writePush("pointer", 0)
            self.tokenizer.advance()

        elif self.tokenizer.getTokenType() == "IDENTIFIER":
            # varName | varName[expression] | subroutineCall
            name = self.tokenizer.identifier()
            self.tokenizer.advance()

            if self.tokenizer.getTokenType() == "SYMBOL":
                if self.tokenizer.symbol() == "[":
                    # Array access
                    self.pushIdentifier(name)
                    self.tokenizer.advance()  # '['
                    self.compileExpression()
                    self.tokenizer.advance()  # ']'
                    self.vmWriter.writeArithmetic("add")
                    self.vmWriter.writePop("pointer", 1)
                    self.vmWriter.writePush("that", 0)

                elif self.tokenizer.symbol() in ["(", "."]:
                    # Subroutine call - backtrack
                    # This is a bit tricky - we need to handle the identifier we already consumed
                    self.compileSubroutineCallFromName(name)

                else:
                    # Simple variable
                    self.pushIdentifier(name)
            else:
                # Simple variable
                self.pushIdentifier(name)

        elif (
            self.tokenizer.getTokenType() == "SYMBOL" and self.tokenizer.symbol() == "("
        ):
            # '(' expression ')'
            self.tokenizer.advance()  # '('
            self.compileExpression()
            self.tokenizer.advance()  # ')'

        elif self.tokenizer.getTokenType() == "SYMBOL" and self.tokenizer.symbol() in [
            "-",
            "~",
        ]:
            # unaryOp term
            op = self.tokenizer.symbol()
            self.tokenizer.advance()
            self.compileTerm()
            if op == "-":
                self.vmWriter.writeArithmetic("neg")
            elif op == "~":
                self.vmWriter.writeArithmetic("not")

    def compileSubroutineCall(self):
        # compile a subroutine call
        # subroutineName | className.subroutineName | varName.subroutineName
        name = self.tokenizer.identifier()
        self.tokenizer.advance()
        self.compileSubroutineCallFromName(name)

    def compileSubroutineCallFromName(self, name):
        # compile subroutine call starting from identifier name
        nArgs = 0

        if self.tokenizer.getTokenType() == "SYMBOL" and self.tokenizer.symbol() == ".":
            # className.subroutineName or varName.subroutineName
            self.tokenizer.advance()  # '.'
            subroutineName = self.tokenizer.identifier()
            self.tokenizer.advance()

            # Check if name is a variable (object method call)
            if self.symbolTable.kindOf(name) != "NONE":
                # Object method call - push object reference as first argument
                self.pushIdentifier(name)  # Push object reference
                nArgs = 1
                className = self.symbolTable.typeOf(name)
                fullName = f"{className}.{subroutineName}"
            else:
                # Static method call - no implicit 'this' argument
                fullName = f"{name}.{subroutineName}"
        else:
            # Method call on current object
            self.vmWriter.writePush("pointer", 0)  # Push 'this'
            nArgs = 1
            fullName = f"{self.className}.{name}"

        # '('
        self.tokenizer.advance()

        # expressionList
        nArgs += self.compileExpressionList()

        # ')'
        self.tokenizer.advance()

        # Call function
        self.vmWriter.writeCall(fullName, nArgs)

    def compileExpressionList(self):
        # compile expression list and return argument count
        nArgs = 0

        if not (
            self.tokenizer.getTokenType() == "SYMBOL" and self.tokenizer.symbol() == ")"
        ):
            # expression
            self.compileExpression()
            nArgs = 1

            # (',' expression)*
            while (
                self.tokenizer.getTokenType() == "SYMBOL"
                and self.tokenizer.symbol() == ","
            ):
                self.tokenizer.advance()  # ','
                self.compileExpression()
                nArgs += 1

        return nArgs

    def pushIdentifier(self, name):
        # push identifier value onto stack
        kind = self.symbolTable.kindOf(name)
        index = self.symbolTable.indexOf(name)

        if kind == "STATIC":
            self.vmWriter.writePush("static", index)
        elif kind == "FIELD":
            self.vmWriter.writePush("this", index)
        elif kind == "ARG":
            self.vmWriter.writePush("argument", index)
        elif kind == "VAR":
            self.vmWriter.writePush("local", index)

    def popIdentifier(self, name):
        # pop value from stack to identifier
        kind = self.symbolTable.kindOf(name)
        index = self.symbolTable.indexOf(name)

        if kind == "STATIC":
            self.vmWriter.writePop("static", index)
        elif kind == "FIELD":
            self.vmWriter.writePop("this", index)
        elif kind == "ARG":
            self.vmWriter.writePop("argument", index)
        elif kind == "VAR":
            self.vmWriter.writePop("local", index)

    def close(self):
        # close compilation
        self.vmWriter.close()


def compileFile(input_file):
    # compile a single Jack file
    output_file = input_file.replace(".jack", ".vm")

    try:
        tokenizer = JackTokenizer(input_file)
        engine = CompilationEngine(tokenizer, output_file)

        # Start compilation
        engine.compileClass()
        engine.close()

        print(f"Compiled {input_file} -> {output_file}")
    except Exception as e:
        print(f"ERROR: Failed to compile {input_file}: {e}")
        import traceback

        traceback.print_exc()


def main():
    if len(sys.argv) != 2:
        print("Usage: python JackCompilerFinal.py <source>")
        print("  <source> can be a .jack file or a directory containing .jack files")
        sys.exit(1)

    source = sys.argv[1]

    if os.path.isfile(source) and source.endswith(".jack"):
        # Single file
        compileFile(source)
    elif os.path.isdir(source):
        # Directory
        for file in os.listdir(source):
            if file.endswith(".jack"):
                compileFile(os.path.join(source, file))
    else:
        print(f"Error: {source} is not a valid .jack file or directory")
        sys.exit(1)


if __name__ == "__main__":
    main()

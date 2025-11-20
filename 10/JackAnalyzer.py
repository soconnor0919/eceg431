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
                    # check for comment end
                    if "*/" in self.currentLine:
                        endIdx = self.currentLine.index("*/") + 2
                        self.currentLine = self.currentLine[endIdx:]
                        self.inComment = False
                    else:
                        # still in comment, skip this line
                        self.currentLine = ""
                        continue

                # check for comment start
                if "/*" in self.currentLine:
                    startIdx = self.currentLine.index("/*")
                    # check if comment ends on same line
                    if "*/" in self.currentLine[startIdx:]:
                        endIdx = self.currentLine.index("*/", startIdx) + 2
                        self.currentLine = (
                            self.currentLine[:startIdx]
                            + " "
                            + self.currentLine[endIdx:]
                        )
                    else:
                        # comment continues to next line
                        self.currentLine = self.currentLine[:startIdx]
                        self.inComment = True

                # replace tabs with spaces and strip
                self.currentLine = self.currentLine.replace("\t", " ").strip()

                # if line is empty after cleaning, get next line
                if len(self.currentLine) == 0:
                    continue

            # parse token from current line
            # skip leading spaces
            self.currentLine = self.currentLine.lstrip()

            if len(self.currentLine) == 0:
                continue

            # check first character
            firstChar = self.currentLine[0]

            # check if symbol
            if firstChar in self.symbols:
                self.currentToken = firstChar
                self.tokenType = "SYMBOL"
                self.currentLine = self.currentLine[1:]
                return True

            # check if string constant
            if firstChar == '"':
                # find closing quote
                endIdx = self.currentLine.index('"', 1)
                self.currentToken = self.currentLine[1:endIdx]
                self.tokenType = "STRING_CONST"
                self.currentLine = self.currentLine[endIdx + 1 :]
                return True

            # check if integer constant
            if firstChar.isdigit():
                # parse integer
                endIdx = 0
                while (
                    endIdx < len(self.currentLine)
                    and self.currentLine[endIdx].isdigit()
                ):
                    endIdx += 1
                self.currentToken = self.currentLine[:endIdx]
                self.tokenType = "INT_CONST"
                self.currentLine = self.currentLine[endIdx:]
                return True

            # must be identifier or keyword
            if firstChar.isalpha() or firstChar == "_":
                # parse identifier
                endIdx = 0
                while endIdx < len(self.currentLine):
                    char = self.currentLine[endIdx]
                    if char.isalnum() or char == "_":
                        endIdx += 1
                    else:
                        break

                self.currentToken = self.currentLine[:endIdx]
                self.currentLine = self.currentLine[endIdx:]

                # check if keyword
                if self.currentToken in self.keywords:
                    self.tokenType = "KEYWORD"
                else:
                    self.tokenType = "IDENTIFIER"

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


class CompilationEngine:
    # generates XML from Jack code

    def __init__(self, tokenizer, output_file):
        # init compilation engine
        self.tokenizer = tokenizer
        self.output = open(output_file, "w")
        self.indent = 0

    def writeOpenTag(self, tag):
        # write opening XML tag
        self.output.write("  " * self.indent + f"<{tag}>\n")
        self.indent += 1

    def writeCloseTag(self, tag):
        # write closing XML tag
        self.indent -= 1
        self.output.write("  " * self.indent + f"</{tag}>\n")

    def writeTerminal(self, tag, value):
        # write terminal (token) XML element
        # escape special characters
        if value == "<":
            value = "&lt;"
        elif value == ">":
            value = "&gt;"
        elif value == '"':
            value = "&quot;"
        elif value == "&":
            value = "&amp;"

        self.output.write("  " * self.indent + f"<{tag}> {value} </{tag}>\n")

    def writeCurrentToken(self):
        # write current token as XML
        tokenType = self.tokenizer.getTokenType()

        if tokenType == "KEYWORD":
            self.writeTerminal("keyword", self.tokenizer.keyword())
        elif tokenType == "SYMBOL":
            self.writeTerminal("symbol", self.tokenizer.symbol())
        elif tokenType == "IDENTIFIER":
            self.writeTerminal("identifier", self.tokenizer.identifier())
        elif tokenType == "INT_CONST":
            self.writeTerminal("integerConstant", str(self.tokenizer.intVal()))
        elif tokenType == "STRING_CONST":
            self.writeTerminal("stringConstant", self.tokenizer.stringVal())

    def compileClass(self):
        # compile complete class
        self.writeOpenTag("class")

        # class keyword
        self.tokenizer.advance()
        self.writeCurrentToken()

        # class name
        self.tokenizer.advance()
        self.writeCurrentToken()

        # opening brace
        self.tokenizer.advance()
        self.writeCurrentToken()

        # class var declarations
        self.tokenizer.advance()
        while self.tokenizer.keyword() in ["static", "field"]:
            self.compileClassVarDec()
            self.tokenizer.advance()

        # subroutine declarations
        while self.tokenizer.keyword() in ["constructor", "function", "method"]:
            self.compileSubroutine()
            self.tokenizer.advance()

        # closing brace
        self.writeCurrentToken()

        self.writeCloseTag("class")

    def compileClassVarDec(self):
        # compile static or field declaration
        self.writeOpenTag("classVarDec")

        # static or field
        self.writeCurrentToken()

        # type
        self.tokenizer.advance()
        self.writeCurrentToken()

        # var name
        self.tokenizer.advance()
        self.writeCurrentToken()

        # additional var names
        self.tokenizer.advance()
        while self.tokenizer.symbol() == ",":
            # comma
            self.writeCurrentToken()
            # var name
            self.tokenizer.advance()
            self.writeCurrentToken()
            self.tokenizer.advance()

        # semicolon
        self.writeCurrentToken()

        self.writeCloseTag("classVarDec")

    def compileSubroutine(self):
        # compile method, function, or constructor
        self.writeOpenTag("subroutineDec")

        # constructor, function, or method
        self.writeCurrentToken()

        # return type
        self.tokenizer.advance()
        self.writeCurrentToken()

        # subroutine name
        self.tokenizer.advance()
        self.writeCurrentToken()

        # opening paren
        self.tokenizer.advance()
        self.writeCurrentToken()

        # parameter list
        self.tokenizer.advance()
        self.compileParameterList()

        # closing paren
        self.writeCurrentToken()

        # subroutine body
        self.tokenizer.advance()
        self.compileSubroutineBody()

        self.writeCloseTag("subroutineDec")

    def compileParameterList(self):
        # compile parameter list (possibly empty)
        self.writeOpenTag("parameterList")

        # check if empty
        if self.tokenizer.symbol() != ")":
            # type
            self.writeCurrentToken()

            # var name
            self.tokenizer.advance()
            self.writeCurrentToken()

            # additional parameters
            self.tokenizer.advance()
            while self.tokenizer.symbol() == ",":
                # comma
                self.writeCurrentToken()
                # type
                self.tokenizer.advance()
                self.writeCurrentToken()
                # var name
                self.tokenizer.advance()
                self.writeCurrentToken()
                self.tokenizer.advance()

        self.writeCloseTag("parameterList")

    def compileSubroutineBody(self):
        # compile subroutine body
        self.writeOpenTag("subroutineBody")

        # opening brace
        self.writeCurrentToken()

        # var declarations
        self.tokenizer.advance()
        while self.tokenizer.keyword() == "var":
            self.compileVarDec()
            self.tokenizer.advance()

        # statements
        self.compileStatements()

        # closing brace
        self.writeCurrentToken()

        self.writeCloseTag("subroutineBody")

    def compileVarDec(self):
        # compile var declaration
        self.writeOpenTag("varDec")

        # var keyword
        self.writeCurrentToken()

        # type
        self.tokenizer.advance()
        self.writeCurrentToken()

        # var name
        self.tokenizer.advance()
        self.writeCurrentToken()

        # additional var names
        self.tokenizer.advance()
        while self.tokenizer.symbol() == ",":
            # comma
            self.writeCurrentToken()
            # var name
            self.tokenizer.advance()
            self.writeCurrentToken()
            self.tokenizer.advance()

        # semicolon
        self.writeCurrentToken()

        self.writeCloseTag("varDec")

    def compileStatements(self):
        # compile sequence of statements
        self.writeOpenTag("statements")

        # process statements
        while self.tokenizer.keyword() in ["let", "if", "while", "do", "return"]:
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

            self.tokenizer.advance()

        self.writeCloseTag("statements")

    def compileLet(self):
        # compile let statement
        self.writeOpenTag("letStatement")

        # let keyword
        self.writeCurrentToken()

        # var name
        self.tokenizer.advance()
        self.writeCurrentToken()

        # check for array indexing
        self.tokenizer.advance()
        if self.tokenizer.symbol() == "[":
            # opening bracket
            self.writeCurrentToken()

            # expression
            self.tokenizer.advance()
            self.compileExpression()

            # closing bracket
            self.writeCurrentToken()
            self.tokenizer.advance()

        # equals sign
        self.writeCurrentToken()

        # expression
        self.tokenizer.advance()
        self.compileExpression()

        # semicolon
        self.writeCurrentToken()

        self.writeCloseTag("letStatement")

    def compileIf(self):
        # compile if statement
        self.writeOpenTag("ifStatement")

        # if keyword
        self.writeCurrentToken()

        # opening paren
        self.tokenizer.advance()
        self.writeCurrentToken()

        # expression
        self.tokenizer.advance()
        self.compileExpression()

        # closing paren
        self.writeCurrentToken()

        # opening brace
        self.tokenizer.advance()
        self.writeCurrentToken()

        # statements
        self.tokenizer.advance()
        self.compileStatements()

        # closing brace
        self.writeCurrentToken()

        # check for else
        self.tokenizer.advance()
        if self.tokenizer.keyword() == "else":
            # else keyword
            self.writeCurrentToken()

            # opening brace
            self.tokenizer.advance()
            self.writeCurrentToken()

            # statements
            self.tokenizer.advance()
            self.compileStatements()

            # closing brace
            self.writeCurrentToken()
        else:
            # no else, back up
            return

        self.writeCloseTag("ifStatement")

    def compileWhile(self):
        # compile while statement
        self.writeOpenTag("whileStatement")

        # while keyword
        self.writeCurrentToken()

        # opening paren
        self.tokenizer.advance()
        self.writeCurrentToken()

        # expression
        self.tokenizer.advance()
        self.compileExpression()

        # closing paren
        self.writeCurrentToken()

        # opening brace
        self.tokenizer.advance()
        self.writeCurrentToken()

        # statements
        self.tokenizer.advance()
        self.compileStatements()

        # closing brace
        self.writeCurrentToken()

        self.writeCloseTag("whileStatement")

    def compileDo(self):
        # compile do statement
        self.writeOpenTag("doStatement")

        # do keyword
        self.writeCurrentToken()

        # subroutine call (identifier)
        self.tokenizer.advance()
        self.writeCurrentToken()

        # check for class/var name or direct call
        self.tokenizer.advance()
        if self.tokenizer.symbol() == ".":
            # class or object method call
            # dot
            self.writeCurrentToken()
            # method name
            self.tokenizer.advance()
            self.writeCurrentToken()
            self.tokenizer.advance()

        # opening paren
        self.writeCurrentToken()

        # expression list
        self.tokenizer.advance()
        self.compileExpressionList()

        # closing paren
        self.writeCurrentToken()

        # semicolon
        self.tokenizer.advance()
        self.writeCurrentToken()

        self.writeCloseTag("doStatement")

    def compileReturn(self):
        # compile return statement
        self.writeOpenTag("returnStatement")

        # return keyword
        self.writeCurrentToken()

        # check for return value
        self.tokenizer.advance()
        if self.tokenizer.symbol() != ";":
            # expression
            self.compileExpression()

        # semicolon
        self.writeCurrentToken()

        self.writeCloseTag("returnStatement")

    def compileExpression(self):
        # compile expression
        self.writeOpenTag("expression")

        # term
        self.compileTerm()

        # check for op term
        ops = {"+", "-", "*", "/", "&", "|", "<", ">", "="}
        while self.tokenizer.symbol() in ops:
            # operator
            self.writeCurrentToken()
            # term
            self.tokenizer.advance()
            self.compileTerm()

        self.writeCloseTag("expression")

    def compileTerm(self):
        # compile term
        self.writeOpenTag("term")

        tokenType = self.tokenizer.getTokenType()

        if tokenType == "INT_CONST":
            # integer constant
            self.writeCurrentToken()
            self.tokenizer.advance()
        elif tokenType == "STRING_CONST":
            # string constant
            self.writeCurrentToken()
            self.tokenizer.advance()
        elif tokenType == "KEYWORD":
            # keyword constant (true, false, null, this)
            self.writeCurrentToken()
            self.tokenizer.advance()
        elif self.tokenizer.symbol() == "(":
            # opening paren
            self.writeCurrentToken()
            # expression
            self.tokenizer.advance()
            self.compileExpression()
            # closing paren
            self.writeCurrentToken()
            self.tokenizer.advance()
        elif self.tokenizer.symbol() in ["-", "~"]:
            # unary operator
            self.writeCurrentToken()
            # term
            self.tokenizer.advance()
            self.compileTerm()
        elif tokenType == "IDENTIFIER":
            # var name, array access, or subroutine call
            self.writeCurrentToken()
            self.tokenizer.advance()

            if self.tokenizer.symbol() == "[":
                # array access
                # opening bracket
                self.writeCurrentToken()
                # expression
                self.tokenizer.advance()
                self.compileExpression()
                # closing bracket
                self.writeCurrentToken()
                self.tokenizer.advance()
            elif self.tokenizer.symbol() == "(":
                # subroutine call
                # opening paren
                self.writeCurrentToken()
                # expression list
                self.tokenizer.advance()
                self.compileExpressionList()
                # closing paren
                self.writeCurrentToken()
                self.tokenizer.advance()
            elif self.tokenizer.symbol() == ".":
                # method call
                # dot
                self.writeCurrentToken()
                # method name
                self.tokenizer.advance()
                self.writeCurrentToken()
                # opening paren
                self.tokenizer.advance()
                self.writeCurrentToken()
                # expression list
                self.tokenizer.advance()
                self.compileExpressionList()
                # closing paren
                self.writeCurrentToken()
                self.tokenizer.advance()

        self.writeCloseTag("term")

    def compileExpressionList(self):
        # compile expression list (possibly empty)
        self.writeOpenTag("expressionList")

        # check if empty
        if self.tokenizer.symbol() != ")":
            # expression
            self.compileExpression()

            # additional expressions
            while self.tokenizer.symbol() == ",":
                # comma
                self.writeCurrentToken()
                # expression
                self.tokenizer.advance()
                self.compileExpression()

        self.writeCloseTag("expressionList")

    def close(self):
        # close output file
        self.output.close()


def analyzeFile(jackFile, outputFile, tokenizeOnly=False):
    # analyze single Jack file
    tokenizer = JackTokenizer(jackFile)

    if tokenizeOnly:
        # tokenizer test output
        output = open(outputFile, "w")
        output.write("<tokens>\n")

        while tokenizer.hasMoreTokens():
            tokenizer.advance()
            tokenType = tokenizer.getTokenType()

            if tokenType == "KEYWORD":
                value = tokenizer.keyword()
                output.write(f"<keyword> {value} </keyword>\n")
            elif tokenType == "SYMBOL":
                value = tokenizer.symbol()
                # escape special characters
                if value == "<":
                    value = "&lt;"
                elif value == ">":
                    value = "&gt;"
                elif value == '"':
                    value = "&quot;"
                elif value == "&":
                    value = "&amp;"
                output.write(f"<symbol> {value} </symbol>\n")
            elif tokenType == "IDENTIFIER":
                value = tokenizer.identifier()
                output.write(f"<identifier> {value} </identifier>\n")
            elif tokenType == "INT_CONST":
                value = tokenizer.intVal()
                output.write(f"<integerConstant> {value} </integerConstant>\n")
            elif tokenType == "STRING_CONST":
                value = tokenizer.stringVal()
                output.write(f"<stringConstant> {value} </stringConstant>\n")

        output.write("</tokens>\n")
        output.close()
    else:
        # full compilation
        engine = CompilationEngine(tokenizer, outputFile)
        engine.compileClass()
        engine.close()


def main():
    # analyze Jack file or directory
    if len(sys.argv) < 2:
        print("Usage: python JackAnalyzer.py <file_or_directory> [-t]")
        sys.exit(1)

    inputPath = sys.argv[1]
    tokenizeOnly = len(sys.argv) > 2 and sys.argv[2] == "-t"

    if not os.path.exists(inputPath):
        print(f"Error: Path '{inputPath}' not found")
        sys.exit(1)

    if os.path.isfile(inputPath):
        # single file mode
        if not inputPath.endswith(".jack"):
            print("Error: Input file must have .jack extension")
            sys.exit(1)

        if tokenizeOnly:
            outputFile = inputPath[:-5] + "T.xml"
        else:
            outputFile = inputPath[:-5] + ".xml"

        analyzeFile(inputPath, outputFile, tokenizeOnly)
        print(f"Analyzed '{inputPath}' to '{outputFile}'")

    elif os.path.isdir(inputPath):
        # directory mode
        jackFiles = [f for f in os.listdir(inputPath) if f.endswith(".jack")]

        if not jackFiles:
            print(f"Error: No .jack files found in directory '{inputPath}'")
            sys.exit(1)

        for jackFile in jackFiles:
            inputFile = os.path.join(inputPath, jackFile)

            if tokenizeOnly:
                outputFile = os.path.join(inputPath, jackFile[:-5] + "T.xml")
            else:
                outputFile = os.path.join(inputPath, jackFile[:-5] + ".xml")

            analyzeFile(inputFile, outputFile, tokenizeOnly)
            print(f"Analyzed '{inputFile}' to '{outputFile}'")

    else:
        print(f"Error: '{inputPath}' is neither file nor directory")
        sys.exit(1)


if __name__ == "__main__":
    main()

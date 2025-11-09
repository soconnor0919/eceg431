import os
import sys


class Parser:
    # reads VM commands and breaks them into components

    def __init__(self, filename):
        # load and clean VM file
        self.commands = []
        self.current_command = ""
        self.command_index = -1

        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                # remove comments
                if '//' in line:
                    line = line[:line.index('//')]
                line = line.strip()
                # skip empty lines
                if line:
                    self.commands.append(line)

    def hasMoreCommands(self):
        return self.command_index + 1 < len(self.commands)

    def advance(self):
        # move to next command
        if self.hasMoreCommands():
            self.command_index += 1
            self.current_command = self.commands[self.command_index]

    def commandType(self):
        # identify command type
        parts = self.current_command.split()
        command = parts[0]

        if command in ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']:
            return 'C_ARITHMETIC'
        elif command == 'push':
            return 'C_PUSH'
        elif command == 'pop':
            return 'C_POP'
        elif command == 'label':
            return 'C_LABEL'
        elif command == 'goto':
            return 'C_GOTO'
        elif command == 'if-goto':
            return 'C_IF'
        elif command == 'function':
            return 'C_FUNCTION'
        elif command == 'call':
            return 'C_CALL'
        elif command == 'return':
            return 'C_RETURN'
        else:
            return 'C_UNKNOWN'

    def arg1(self):
        # extract first arg
        if self.commandType() == 'C_ARITHMETIC':
            return self.current_command.split()[0]
        else:
            return self.current_command.split()[1]

    def arg2(self):
        # extract second arg for push/pop/function/call
        if self.commandType() in ['C_PUSH', 'C_POP', 'C_FUNCTION', 'C_CALL']:
            return int(self.current_command.split()[2])
        return None


class CodeWriter:
    # generates assembly from VM commands

    def __init__(self, output_file):
        # init code writer
        self.output_file = open(output_file, 'w')
        self.label_counter = 0
        self.filename = None
        self.current_function = None

    def setFileName(self, filename):
        # set current filename for static vars
        self.filename = os.path.splitext(os.path.basename(filename))[0]

    def writeArithmetic(self, command):
        # write arithmetic command
        if command == 'add':
            self.writeBinaryOp('+')
        elif command == 'sub':
            self.writeBinaryOp('-')
        elif command == 'and':
            self.writeBinaryOp('&')
        elif command == 'or':
            self.writeBinaryOp('|')
        elif command == 'neg':
            self.writeUnaryOp('-')
        elif command == 'not':
            self.writeUnaryOp('!')
        elif command == 'eq':
            self.writeComparison('JEQ')
        elif command == 'gt':
            self.writeComparison('JGT')
        elif command == 'lt':
            self.writeComparison('JLT')

    def writePushPop(self, command, segment, index):
        # write push or pop command
        if command == 'C_PUSH':
            self.writePush(segment, index)
        elif command == 'C_POP':
            self.writePop(segment, index)

    def writeBinaryOp(self, op):
        # binary arithmetic operation
        # pop y to D
        self.popToD()
        # pop x, compute x op y
        self.output_file.write("@SP\n")
        self.output_file.write("AM=M-1\n")
        if op == '+':
            self.output_file.write("M=M+D\n")
        elif op == '-':
            self.output_file.write("M=M-D\n")
        elif op == '&':
            self.output_file.write("M=M&D\n")
        elif op == '|':
            self.output_file.write("M=M|D\n")
        # inc stack pointer
        self.incSP()

    def writeUnaryOp(self, op):
        # unary arithmetic operation
        self.output_file.write("@SP\n")
        self.output_file.write("A=M-1\n")
        if op == '-':
            self.output_file.write("M=-M\n")
        elif op == '!':
            self.output_file.write("M=!M\n")

    def writeComparison(self, jumpType):
        # comparison operation
        # pop y to D
        self.popToD()
        # pop x
        self.output_file.write("@SP\n")
        self.output_file.write("AM=M-1\n")
        # compute x - y
        self.output_file.write("D=M-D\n")
        trueLabel = f"TRUE_{self.label_counter}"
        endLabel = f"END_{self.label_counter}"
        self.label_counter += 1

        # jump if condition
        self.output_file.write(f"@{trueLabel}\n")
        self.output_file.write(f"D;{jumpType}\n")
        # false case: push 0
        self.output_file.write("@SP\n")
        self.output_file.write("A=M\n")
        self.output_file.write("M=0\n")
        self.output_file.write(f"@{endLabel}\n")
        self.output_file.write("0;JMP\n")
        # true case: push -1
        self.output_file.write(f"({trueLabel})\n")
        self.output_file.write("@SP\n")
        self.output_file.write("A=M\n")
        self.output_file.write("M=-1\n")
        self.output_file.write(f"({endLabel})\n")
        # inc stack pointer
        self.incSP()

    def writePush(self, segment, index):
        # push command
        if segment == 'constant':
            # push constant val
            self.output_file.write(f"@{index}\n")
            self.output_file.write("D=A\n")
            self.pushD()
        elif segment == 'local':
            self.pushFromSeg("LCL", index)
        elif segment == 'argument':
            self.pushFromSeg("ARG", index)
        elif segment == 'this':
            self.pushFromSeg("THIS", index)
        elif segment == 'that':
            self.pushFromSeg("THAT", index)
        elif segment == 'temp':
            # temp starts at RAM[5]
            self.output_file.write(f"@{5 + index}\n")
            self.output_file.write("D=M\n")
            self.pushD()
        elif segment == 'pointer':
            # pointer 0=THIS, 1=THAT
            if index == 0:
                self.output_file.write("@THIS\n")
            else:
                self.output_file.write("@THAT\n")
            self.output_file.write("D=M\n")
            self.pushD()
        elif segment == 'static':
            # static vars are filename.index
            self.output_file.write(f"@{self.filename}.{index}\n")
            self.output_file.write("D=M\n")
            self.pushD()

    def writePop(self, segment, index):
        # pop command
        if segment == 'local':
            self.popToSeg("LCL", index)
        elif segment == 'argument':
            self.popToSeg("ARG", index)
        elif segment == 'this':
            self.popToSeg("THIS", index)
        elif segment == 'that':
            self.popToSeg("THAT", index)
        elif segment == 'temp':
            # pop to temp
            self.popToD()
            # !! ram starts at address 5 !!
            self.output_file.write(f"@{5 + index}\n")
            self.output_file.write("M=D\n")
        elif segment == 'pointer':
            # pop to pointer
            self.popToD()
            if index == 0:
                self.output_file.write("@THIS\n")
            else:
                self.output_file.write("@THAT\n")
            self.output_file.write("M=D\n")
        elif segment == 'static':
            # pop to static var
            self.popToD()
            # use filename here because static vars need unique names
            self.output_file.write(f"@{self.filename}.{index}\n")
            self.output_file.write("M=D\n")

    def pushFromSeg(self, segName, index):
        # push val from memory segment
        # get base addr
        self.output_file.write(f"@{segName}\n")
        self.output_file.write("D=M\n")
        # add index
        self.output_file.write(f"@{index}\n")
        self.output_file.write("A=D+A\n")
        # get val
        self.output_file.write("D=M\n")
        self.pushD()

    def popToSeg(self, segName, index):
        # pop val to memory segment
        # compute target addr in R13
        self.output_file.write(f"@{segName}\n")
        self.output_file.write("D=M\n")
        self.output_file.write(f"@{index}\n")
        self.output_file.write("D=D+A\n")
        self.output_file.write("@R13\n")
        self.output_file.write("M=D\n")
        # pop val
        self.popToD()
        # store in target
        self.output_file.write("@R13\n")
        self.output_file.write("A=M\n")
        self.output_file.write("M=D\n")

    def pushD(self):
        # push D onto stack
        self.output_file.write("@SP\n")
        self.output_file.write("A=M\n")
        self.output_file.write("M=D\n")
        self.incSP()

    def popToD(self):
        # pop stack to D
        self.output_file.write("@SP\n")
        self.output_file.write("AM=M-1\n")
        self.output_file.write("D=M\n")

    def incSP(self):
        # inc stack pointer
        self.output_file.write("@SP\n")
        self.output_file.write("M=M+1\n")

    def writeInit(self):
        # write bootstrap code
        # set stack pointer to 256
        self.output_file.write("// Bootstrap code\n")
        self.output_file.write("@256\n")
        self.output_file.write("D=A\n")
        self.output_file.write("@SP\n")
        self.output_file.write("M=D\n")
        self.writeCall("Sys.init", 0)

    def writeLabel(self, label):
        # write label command
        # uses function scope
        # example: label LOOP -> (Main.test.LOOP)
        if self.current_function:
            self.output_file.write(f"({self.current_function}${label})\n")
        else:
            self.output_file.write(f"({label})\n")

    def writeGoto(self, label):
        # write goto command
        # example: goto LOOP -> @Main.test.LOOP + 0;JMP
        if self.current_function:
            self.output_file.write(f"@{self.current_function}${label}\n")
        else:
            self.output_file.write(f"@{label}\n")
        self.output_file.write("0;JMP\n")

    def writeIf(self, label):
        # write if-goto command
        # jumps if D is not zero
        # example: if-goto LOOP -> pop + @Main.test.LOOP + D;JNE
        self.popToD()
        if self.current_function:
            self.output_file.write(f"@{self.current_function}${label}\n")
        else:
            self.output_file.write(f"@{label}\n")
        self.output_file.write("D;JNE\n")

    def writeCall(self, functionName, numArgs):
        # write call command
        returnLabel = f"RETURN_{self.label_counter}"
        self.label_counter += 1

        # push return address
        self.output_file.write(f"@{returnLabel}\n")
        self.output_file.write("D=A\n")
        self.pushD()

        # push LCL
        self.output_file.write("@LCL\n")
        self.output_file.write("D=M\n")
        self.pushD()

        # push ARG
        self.output_file.write("@ARG\n")
        self.output_file.write("D=M\n")
        self.pushD()

        # push THIS
        self.output_file.write("@THIS\n")
        self.output_file.write("D=M\n")
        self.pushD()

        # push THAT
        self.output_file.write("@THAT\n")
        self.output_file.write("D=M\n")
        self.pushD()

        # reposition ARG = SP - numArgs - 5
        self.output_file.write("@SP\n")
        self.output_file.write("D=M\n")
        self.output_file.write(f"@{numArgs + 5}\n")
        self.output_file.write("D=D-A\n")
        self.output_file.write("@ARG\n")
        self.output_file.write("M=D\n")

        # reposition LCL = SP
        self.output_file.write("@SP\n")
        self.output_file.write("D=M\n")
        self.output_file.write("@LCL\n")
        self.output_file.write("M=D\n")

        # goto function
        self.output_file.write(f"@{functionName}\n")
        self.output_file.write("0;JMP\n")

        # set return label
        self.output_file.write(f"({returnLabel})\n")

    def writeFunction(self, functionName, numLocals):
        # write function command
        # create function entrypoint label
        self.current_function = functionName
        self.output_file.write(f"({functionName})\n")

        # initialize local variables to 0
        for i in range(numLocals):
            self.output_file.write("@0\n")
            self.output_file.write("D=A\n")
            self.pushD()

    def writeReturn(self):
        # write return command
        # FRAME = LCL
        # save frame pointer
        self.output_file.write("@LCL\n")
        self.output_file.write("D=M\n")
        self.output_file.write("@R13\n")  # use R13 as FRAME
        self.output_file.write("M=D\n")

        # RET = *(FRAME-5)
        # extract return address from frame
        self.output_file.write("@5\n")
        self.output_file.write("A=D-A\n")
        self.output_file.write("D=M\n")
        self.output_file.write("@R14\n")  # use R14 as RET
        self.output_file.write("M=D\n")

        # *ARG = pop()
        # set position of return val for caller
        self.popToD()
        self.output_file.write("@ARG\n")
        self.output_file.write("A=M\n")
        self.output_file.write("M=D\n")

        # SP = ARG + 1
        # restore caller stack pointer
        self.output_file.write("@ARG\n")
        self.output_file.write("D=M+1\n")
        self.output_file.write("@SP\n")
        self.output_file.write("M=D\n")

        # restore caller segment pointers...

        # restore THAT = *(FRAME-1)
        self.output_file.write("@R13\n")
        self.output_file.write("D=M\n")
        self.output_file.write("@1\n")
        self.output_file.write("A=D-A\n")
        self.output_file.write("D=M\n")
        self.output_file.write("@THAT\n")
        self.output_file.write("M=D\n")

        # restore THIS = *(FRAME-2)
        self.output_file.write("@R13\n")
        self.output_file.write("D=M\n")
        self.output_file.write("@2\n")
        self.output_file.write("A=D-A\n")
        self.output_file.write("D=M\n")
        self.output_file.write("@THIS\n")
        self.output_file.write("M=D\n")

        # restore ARG = *(FRAME-3)
        self.output_file.write("@R13\n")
        self.output_file.write("D=M\n")
        self.output_file.write("@3\n")
        self.output_file.write("A=D-A\n")
        self.output_file.write("D=M\n")
        self.output_file.write("@ARG\n")
        self.output_file.write("M=D\n")

        # restore LCL = *(FRAME-4)
        self.output_file.write("@R13\n")
        self.output_file.write("D=M\n")
        self.output_file.write("@4\n")
        self.output_file.write("A=D-A\n")
        self.output_file.write("D=M\n")
        self.output_file.write("@LCL\n")
        self.output_file.write("M=D\n")

        # goto RET
        # jump back to caller
        self.output_file.write("@R14\n")
        self.output_file.write("A=M\n")
        self.output_file.write("0;JMP\n")

    def close(self):
        self.output_file.close()


def translateVMFile(vmFile, codeWriter):
    # translate single VM file using existing code writer
    parser = Parser(vmFile)
    codeWriter.setFileName(vmFile)

    while parser.hasMoreCommands():
        parser.advance()
        cmdType = parser.commandType()

        if cmdType == 'C_ARITHMETIC':
            codeWriter.writeArithmetic(parser.arg1())
        elif cmdType in ['C_PUSH', 'C_POP']:
            codeWriter.writePushPop(cmdType, parser.arg1(), parser.arg2())
        elif cmdType == 'C_LABEL':
            codeWriter.writeLabel(parser.arg1())
        elif cmdType == 'C_GOTO':
            codeWriter.writeGoto(parser.arg1())
        elif cmdType == 'C_IF':
            codeWriter.writeIf(parser.arg1())
        elif cmdType == 'C_FUNCTION':
            codeWriter.writeFunction(parser.arg1(), parser.arg2())
        elif cmdType == 'C_CALL':
            codeWriter.writeCall(parser.arg1(), parser.arg2())
        elif cmdType == 'C_RETURN':
            codeWriter.writeReturn()


def main():
    # translate VM file or directory to assembly
    if len(sys.argv) < 2:
        print("Usage: python hvm.py <file_or_directory> [-y|-n]")
        sys.exit(1)

    inputPath = sys.argv[1]

    # check for bootstrap flag
    writeBootstrap = True
    if len(sys.argv) > 2:
        if sys.argv[2] == '-n':
            writeBootstrap = False
        elif sys.argv[2] == '-y':
            writeBootstrap = True

    if not os.path.exists(inputPath):
        print(f"Error: Path '{inputPath}' not found")
        sys.exit(1)

    if os.path.isfile(inputPath):
        # single file mode
        if not inputPath.endswith('.vm'):
            print("Error: Input file must have .vm extension")
            sys.exit(1)

        outputFile = inputPath[:-3] + '.asm'
        codeWriter = CodeWriter(outputFile)

        if writeBootstrap:
            codeWriter.writeInit()

        translateVMFile(inputPath, codeWriter)
        codeWriter.close()
        print(f"Translated '{inputPath}' to '{outputFile}'")

    elif os.path.isdir(inputPath):
        # directory mode - translate all VM files
        vmFiles = [f for f in os.listdir(inputPath) if f.endswith('.vm')]

        if not vmFiles:
            print(f"Error: No .vm files found in directory '{inputPath}'")
            sys.exit(1)

        # sort files to ensure consistent order
        vmFiles.sort()

        # output file is directory name + .asm
        dirName = os.path.basename(inputPath.rstrip('/'))
        outputFile = os.path.join(inputPath, dirName + '.asm')
        codeWriter = CodeWriter(outputFile)

        if writeBootstrap:
            codeWriter.writeInit()

        # translate all VM files
        for vmFileName in vmFiles:
            vmFile = os.path.join(inputPath, vmFileName)
            translateVMFile(vmFile, codeWriter)

        codeWriter.close()
        print(f"Translated {len(vmFiles)} files to '{outputFile}'")

    else:
        print(f"Error: '{inputPath}' is neither file nor directory")
        sys.exit(1)

if __name__ == "__main__":
    main()

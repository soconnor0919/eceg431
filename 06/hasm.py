import sys
import os

class Parser:
    # reads asm commands and breaks them into components

    def __init__(self, filename):
        # load and clean asm file
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
        if self.current_command.startswith('@'):
            return 'A_COMMAND'
        elif self.current_command.startswith('(') and self.current_command.endswith(')'):
            return 'L_COMMAND'
        else:
            return 'C_COMMAND'

    def symbol(self):
        # extract symbol from @xxx or (xxx)
        if self.commandType() == 'A_COMMAND':
            return self.current_command[1:]
        elif self.commandType() == 'L_COMMAND':
            return self.current_command[1:-1]
        return None

    def dest(self):
        # extract dest from c-command
        if self.commandType() == 'C_COMMAND':
            if '=' in self.current_command:
                return self.current_command.split('=')[0]
            return 'null'
        return None

    def comp(self):
        # extract comp from c-command
        if self.commandType() == 'C_COMMAND':
            command = self.current_command
            # strip dest if present
            if '=' in command:
                command = command.split('=')[1]
            # strip jump if present
            if ';' in command:
                command = command.split(';')[0]
            return command
        return None

    def jump(self):
        # extract jump from c-command
        if self.commandType() == 'C_COMMAND':
            if ';' in self.current_command:
                return self.current_command.split(';')[1]
            return 'null'
        return None


class Code:
    # translates mnemonics to binary codes

    def __init__(self):
        self.dest_codes = {
            'null': '000',
            'M': '001',
            'D': '010',
            'MD': '011',
            'A': '100',
            'AM': '101',
            'AD': '110',
            'AMD': '111'
        }

        self.jump_codes = {
            'null': '000',
            'JGT': '001',
            'JEQ': '010',
            'JGE': '011',
            'JLT': '100',
            'JNE': '101',
            'JLE': '110',
            'JMP': '111'
        }

        self.comp_codes = {
            # a=0 computations
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
            'D-A': '0010011',
            'A-D': '0000111',
            'D&A': '0000000',
            'D|A': '0010101',
            # a=1 computations (M versions)
            'M': '1110000',
            '!M': '1110001',
            '-M': '1110011',
            'M+1': '1110111',
            'M-1': '1110010',
            'D+M': '1000010',
            'D-M': '1010011',
            'M-D': '1000111',
            'D&M': '1000000',
            'D|M': '1010101'
        }

    def dest(self, mnemonic):
        return self.dest_codes.get(mnemonic, '000')

    def comp(self, mnemonic):
        return self.comp_codes.get(mnemonic, '0000000')

    def jump(self, mnemonic):
        return self.jump_codes.get(mnemonic, '000')


class SymbolTable:
    # map symbols to addrs

    def __init__(self):
        # predefined symbols
        self.table = {
            'SP': 0,
            'LCL': 1,
            'ARG': 2,
            'THIS': 3,
            'THAT': 4,
            'R0': 0,
            'R1': 1,
            'R2': 2,
            'R3': 3,
            'R4': 4,
            'R5': 5,
            'R6': 6,
            'R7': 7,
            'R8': 8,
            'R9': 9,
            'R10': 10,
            'R11': 11,
            'R12': 12,
            'R13': 13,
            'R14': 14,
            'R15': 15,
            'SCREEN': 16384,
            'KBD': 24576
        }

    def addEntry(self, symbol, address):
        self.table[symbol] = address

    def contains(self, symbol):
        return symbol in self.table

    def GetAddress(self, symbol):
        return self.table.get(symbol, None)


def assemble(input_file):
    # two-pass assembly: build symbols then generate code

    parser = Parser(input_file)
    code = Code()
    symbol_table = SymbolTable()

    # first pass: scan for labels
    rom_address = 0
    parser.command_index = -1

    while parser.hasMoreCommands():
        parser.advance()
        command_type = parser.commandType()

        if command_type == 'L_COMMAND':
            # add label to symbol table
            symbol = parser.symbol()
            symbol_table.addEntry(symbol, rom_address)
        else:
            # count actual instructions
            rom_address += 1

    # second pass: generate binary code
    output_lines = []
    variable_address = 16  # variables start at RAM[16]
    parser.command_index = -1

    while parser.hasMoreCommands():
        parser.advance()
        command_type = parser.commandType()

        if command_type == 'A_COMMAND':
            symbol = parser.symbol()

            # resolve symbol to address
            if symbol.isdigit():
                address = int(symbol)
            else:
                if symbol_table.contains(symbol):
                    address = symbol_table.GetAddress(symbol)
                else:
                    # new variable
                    symbol_table.addEntry(symbol, variable_address)
                    address = variable_address
                    variable_address += 1

            # convert to 16-bit binary
            binary_instruction = format(address, '016b')
            output_lines.append(binary_instruction)

        elif command_type == 'C_COMMAND':
            # parse c-instruction components
            dest_mnemonic = parser.dest()
            comp_mnemonic = parser.comp()
            jump_mnemonic = parser.jump()

            # translate to binary
            dest_code = code.dest(dest_mnemonic)
            comp_code = code.comp(comp_mnemonic)
            jump_code = code.jump(jump_mnemonic)

            # assemble 16-bit instruction: 111accccccdddjjj
            binary_instruction = '111' + comp_code + dest_code + jump_code
            output_lines.append(binary_instruction)

        # L_COMMAND generates no code

    return output_lines


def main():
    # assemble hack assembly file to binary

    if len(sys.argv) != 2:
        print("Usage: python hasm.py <input_file.asm>")
        sys.exit(1)

    input_file = sys.argv[1]

    # validate input file
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)

    if not input_file.endswith('.asm'):
        print("Error: Input file must have .asm extension")
        sys.exit(1)

    # generate output filename
    output_file = input_file[:-4] + '.hack'

    try:
        # assemble program
        binary_code = assemble(input_file)

        # write binary output
        with open(output_file, 'w') as f:
            for line in binary_code:
                f.write(line + '\n')

        print(f"Assembly completed. Output written to '{output_file}'")
        print(f"Generated {len(binary_code)} instructions")

    except Exception as e:
        print(f"Error during assembly: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

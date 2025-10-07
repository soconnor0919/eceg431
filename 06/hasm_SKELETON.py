import argparse

class Parser():
    def __init__(self, data):
        pass

    def hasMoreCommnads(self):
        pass

    def advance(self):
        pass

    def commandType(self):
        pass

    def symbol(self):
        pass

    def dest(self):
        pass

    def comp(self):
        pass

    def jump(self):
        pass

class Code():
    def dest(self, mnemonic):
        pass

    def comp(self, mnemonic):
        pass

    def jump(self, mnemonic):
        pass

class SymbolTable():
    def __init__(self):
        pass

    def addEntry(self, symbol, address):
        pass

    def contains(self, symbol):
        pass

    def GetAddress(self, symbol):
        pass


def main():
    '''
    The main function for the assembler. Takes a command line argument for the input file
    and an optional argument for the output file.
    ''' 
    print("You do not have to use this method to parse arguments.")
    print("The example from project 5.5 works fine too.")
    print("You will get an error soon if you are running this.")
    print("You need to actually modify the code. What function")
    print("do you want to run first?")
    print("-------------------------")

    # Create an argument parser for command line arguments
    a_parser = argparse.ArgumentParser(description='Assembler for the Hack CPU')

    a_parser.add_argument('input_file', type=str)
    a_parser.add_argument('-o', dest='output_file', default='Prog.hack', type=str)

    args = a_parser.parse_args()

    parser = Parser(args.input_file)

    parser.DoYourThingButPleaseRenameThisMethod() #<-- will error here

# Call the main function
if __name__ == "__main__":
    main()

Project 6: The Assembler

The description for this project is found at:

https://www.nand2tetris.org/project06

You may _not_ work as pairs on this project. For now, please work individually. We'll start partners in the next projects after Fall Break.


The default name for your file should be 'hasm.py'. If you name your file something else, just edit the "PythonFileName.txt" file to have the correct name. For example, the posted text file would tell the grader to run 'hasm_SKELETON.py' for assembling files. Be sure to place your assembled .hack file into the *same location* as the .asm file that you are assembling. The name should be such that XXX.asm is compiled to XXX.hack.

Hints:

a) Use the proposed API in chapter 6 that splits the tasks across three "modules."

b) Start with creating an assembler that will assemble symbol-less files. You can test your assembler against the "MaxL.asm", "RectL.asm" and "PongL.asm" files provided in the project06 directory.

c) To develop a symbol table, you will need to i) pre-load your symbol table with the pre-defined symbols and ii) have your program take a two-pass approach that involves reading the ASM file twice. (Once, first to read in all the symbols and second do then to the actual assembling.)

// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
// The algorithm is based on repetitive addition.

// excuse excessive comments here..

    // init r2 to 0
    @2 // sel r2
    M=0 // set it to 0

(LOOP) // begin loop

    // check if r1 = 0
    @1 // sel r1
    D=M // load r1 to data from mem
    @END // sel END
    D;JEQ // jump to END if r1 = 0 (nothing left to add, we're done)

    // add r0 to r2
    @2 // sel r2
    D=M // load r2 to data
    @0 // sel r0
    D=D+M // add r0 to r2 (r2 in mem, r0 in data)
    @2 // sel r2
    M=D // store result in r2

    // r1 -= 1 (decrement)
    @1 // sel r1
    M=M-1 // decrement r1

    // check if r1 = 0 (jump back)
    @LOOP // sel LOOP
    0;JMP // jump to LOOP

// end
(END) // label for jump
    0;JMP // from textbook, infinite loop?

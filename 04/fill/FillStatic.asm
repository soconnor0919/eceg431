// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/FillStatic.asm

// Blackens the screen, i.e. writes "black" in every pixel.
// Key presses are ignored.
// This is an intermediate step added to help you out.

(LOOP) // main loop
    @FILL_BLACK // sel fill black
    0;JMP // jump unconditionally

(FILL_BLACK) // fill screen with black
    // init count and pointer
    // screen = 512x256 pixels = 131072 pixels total
    // each word holds 16 pixels, so 131072/16 = 8192 words
    @8192 // sel value for count (8192)
    D=A // load 8192 to data
    @count // sel count var
    M=D // set count = 8192
    @SCREEN // sel screen start
    D=A // load screen address to data
    @pointer // sel pointer var
    M=D // set pointer = screen start

(BLACK_LOOP) // loop for filling black
    // check if count = 0
    @count // sel count
    D=M // load count to data
    @LOOP // sel main loop
    D;JEQ // jump to main if done

    // set word to -1 (black)
    @pointer // sel pointer
    A=M // set address to pointer value
    M=-1 // set screen word to black

    // inc pointer
    @pointer // sel pointer
    M=M+1 // inc pointer

    // dec count
    @count // sel count
    M=M-1 // dec count

    // jump back to black loop
    @BLACK_LOOP // sel black loop
    0;JMP // jump back to loop

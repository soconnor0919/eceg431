// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed,
// the screen should be cleared.

// excuse excessive comments here again..
// run test with cmd line, otherwise it takes forever
// later note: web IDE seems to render screen, local tester does not.
// code duplication- we need to write the same code for filling black and white, but this feels wrong (code reuse)

(LOOP) // main loop
    // check kb input
    @KBD // sel kb reg
    D=M // load kb value to data
    @FILL_BLACK // sel fill black
    D;JNE // jump if key pressed (jump not equal? non-zero)

    // jump to fill white if no key pressed
    @FILL_WHITE // sel fill white
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

(FILL_WHITE) // fill screen with white
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

(WHITE_LOOP) // loop for filling white
    // check if count = 0
    @count // sel count
    D=M // load count to data
    @LOOP // sel main loop
    D;JEQ // jump to main if done

    // set word to 0 (white)
    @pointer // sel pointer
    A=M // set address to pointer value
    M=0 // set screen word to white

    // inc pointer
    @pointer // sel pointer
    M=M+1 // inc pointer

    // dec count
    @count // sel count
    M=M-1 // dec count

    // jump back to white loop
    @WHITE_LOOP // sel white loop
    0;JMP // jump back to loop

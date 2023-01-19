// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

//en rad = 32 register lång  (32*16 pixlar)
//en kolumn = 16 register lång (16*16 pixlar)

@SCREEN
D=A
@addr
M=D
/////////////////////// vart den ska hoppa baserat på KBD input
(LOOP)
@KBD
D=M
@UNFILL
D;JEQ
@FILL
D;JGT
///////////////////////////////
(UNFILL)
@addr
A=M
M=0

@addr
D=M
@SCREEN   
D=D-A       //addr-16384 = D
@LOOP
D;JLT       //JUMP till loop ifall D < 0

@addr
M=M-1

@LOOP
0;JMP
//////////////////////////////////
(FILL)
@addr
A=M
M=-1

@addr
D=M
@24575
D=D-A       //addr-24575 = D
@LOOP
D;JEQ       //JUMP till loop ifall D = 0

@addr
M=M+1

@LOOP
0;JMP
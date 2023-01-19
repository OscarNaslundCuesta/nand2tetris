// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

@R2
M=0

@R0     //d blir R0
D=M     
@n
M=D  //n blir R0 och antas vara minst

@R1
D=M
@add    
M=D     //add blir R1 och antas vara störst

@product    //product = 0
M=0

@R0
D=M
@add
D=M-D
@diff   //diff = R1 - R0 (add-n)
M=D
@LOOP
D;JGE   //jump till loop ifall diff equal/greater than 0

//////////////////////////////////////////////////////////////////
@R0     //d blir R0
D=M     
@add
M=D     //add blir R0 och är störst

@R1
D=M
@n    
M=D     //n blir R0 och är minst
///////////////////////////////////////////////////////////////////

(LOOP)
@n
D=M
@STOP
D;JEQ   //if n = 0 goto STOP

@add     //D blir add
D=M

@product     //Lägger till D (R0) till product
M=M+D

@n
M=M-1

@LOOP
0;JMP

(STOP)
@product    //D blir product
D=M
@R2         //R2 blir D
M=D

(END)
@END
0;JMP
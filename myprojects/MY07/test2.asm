//T_ADD
@SP
AM=M-1  //minskar pointern med 1
  //går till top av stacken
D=M    //sparar värdet i D
//@R13    //1st stack
//M=D     //kanske inte behövs
@SP
AM=M-1  //minskar pointern igen 1
 //går till 2nd av stacken
M=M+D  //adderar 1st+2nd = D
@SP
M=M+1

//T_SUB
@SP
AM=M-1  //minskar pointern med 1 och goto top stacken
D=M    //sparar värdet i D
@SP
AM=M-1  //minskar pointern igen 1 och goto 2nd stack
M=M-D  //subtraherar 2nd-1st = D
@SP
M=M+1


//T_NEG
@SP
AM=M-1  //minskar pointern med 1 och goto top stacken
D=M    //sparar värdet i D
M=0     //nollar M
M=M-D   //0-D
@SP
M=M+1

//////////////////////////////////////////////////////////
//T_EQ
@SP
AM=M-1  //minskar pointern med 1 och goto top stacken
D=M    //sparar värdet i D
@R13
M=D
@SP
AM=M-1  //minskar pointern igen 1 och goto 2nd stack
D=M
@R13
D=M-D

@TRUE
D;JEQ   //if D=0 goto TRUE
@FALSE
0;JMP   //if D != 0 goto FALSE

(TRUE)  //INTE MINSKA FÖR MKT???
@SP
A=M
M=-1
@END
0;JMP

(FALSE)
@SP
A=M
M=0
@END
0;JMP

(END)
@SP
M=M+1

/////////////////////////////////////////
//T_GT
@SP
AM=M-1  //minskar pointern med 1 och goto top stacken
D=M    //sparar värdet i D
@R13
M=D   //value 1st (y)
@SP
AM=M-1  //minskar pointern igen 1 och goto 2nd stack
D=M
@R13    //x-y
D=D-M

@TRUE
D;JGT   //if D>0 goto TRUE
@FALSE
D;JLE   //if D <= 0 goto FALSE

(TRUE)  //INTE MINSKA FÖR MKT???
@SP
A=M
M=-1
@END
0;JMP

(FALSE)
@SP
A=M
M=0
@END
0;JMP

(END)
@SP
M=M+1

////////////////////////////////////////////
//T_LT
@SP
AM=M-1  //minskar pointern med 1 och goto top stacken
D=M    //sparar värdet i D
@R13
M=D   //value 1st (y)
@SP
AM=M-1  //minskar pointern igen 1 och goto 2nd stack
D=M
@R13    //y-x
D=M-D

@TRUE
D;JGT   //if D>0 goto TRUE
@FALSE
D;JLE   //if D <= 0 goto FALSE

(TRUE)  //INTE MINSKA FÖR MKT???
@SP
A=M
M=-1
@END
0;JMP

(FALSE)
@SP
A=M
M=0
@END
0;JMP

(END)
@SP
M=M+1

////////////////////////////////////////////
//T_AND
@SP
AM=M-1  //minskar pointern med 1 och goto top stacken
D=M    //sparar värdet i D
@SP
AM=M-1  //minskar pointern igen 1 och goto 2nd stack
M=D&M
@SP
M=M+1

////////////////////////////////////////////
//T_OR
@SP
AM=M-1  //minskar pointern med 1 och goto top stacken
D=M    //sparar värdet i D
@SP
AM=M-1  //minskar pointern igen 1 och goto 2nd stack
M=D|M
@SP
M=M+1

////////////////////////////////////////////
//T_NOT (not y  (topstack))
@SP
AM=M-1  //minskar pointern med 1 och goto top stacken
M=!M
@SP
M=M+1
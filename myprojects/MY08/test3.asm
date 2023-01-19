//Init
@256
D=M
@SP
M=D
//Call sys.init


////////////////////////////
//CALL
@LCL    //LCL
D=M
@SP
A=M
M=D
@SP
M=M+1

@ARG    //ARG
D=M
@SP
A=M
M=D
@SP
M=M+1

@THIS   //THIS
D=M
@SP
A=M
M=D
@SP
M=M+1

@THAT   //THAT
D=M
@SP
A=M
M=D
@SP
M=M+1

//Repositions ARG
@SP
  D=M
  @5
  D=D-A
  @ARG
  M=D

//LCL = SP
@SP
D=M
@LCL
M=D

//Goto functionName
@functionName
0;JMP

//########################################
//RETURN

  //frame = LCL
@LCL
  D=M //sparar LCL addressen i D
  @R13 
  M=D //endFrame sparas i R13

  //RET = *(FRAME-5)
@5
  D=A //D=5
  @R13
  A=M-D
  D=M //D= LCL-5  (retAddr)
  @R14 //sparar retAddr i R14
  M=D


//*ARG = pop()
@SP
  AM=M-1
  D=M
  @ARG
  A=M   //går ditt ARG pekar
  M=D   //lägger in D i dit ARG pekar

//SP = ARG + 1
  @ARG
  D=A   //lägger in ARG addr i D
  D=D+1
@SP
    M=D //SP = ARG + 1

//THAT  sen,THIS,ARG,LCL
@R13
D=M
A=D-1
D=M
@THAT
M=D

//THIS
@R13
D=M
D=D-1
A=D-1
D=M
@THIS
M=D

//ARG
@R13
D=M
D=D-1
D=D-1
A=D-1
D=M
@ARG
M=D

//LCL
@R13
D=M
D=D-1
D=D-1
D=D-1
A=D-1
D=M
@LCL
M=D

@R14    //hämtar retAddr
A=M


//////////////////////////////////////
//FUNCTION
@SP
AM=M-1  //minskar pointern med 1 och goto top stacken
D=M    //sparar värdet i D
@local_label
D;JLT   //if D < 0 (dvs true) JUMP



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
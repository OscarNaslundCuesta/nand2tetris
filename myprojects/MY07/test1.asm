//push local
@LCL
D=M     //hämtar local address
@index
A=A+D   //dest address
D=M     //hämtar värdet i index
@SP
A=M     //går dit SP pekar
M=D     //ändrar värdet på den addressen
@SP
M=M+1

//push constant
@index
D=A
@SP
A=M
M=D
@SP
M=M+1

//push static
@Foo.index
D=M
@SP
A=M     
M=D
@SP
M=M+1

//push temp
@5
D=M     
@index
A=A+D   //dest address
D=M     //hämtar värdet i index
@SP
A=M     //går dit SP pekar
M=D     //ändrar värdet på den addressen
@SP
M=M+1

//push pointer
@3
D=A     
@index
A=A+D   //dest address
D=M     //hämtar värdet i index
@SP
A=M     //går dit SP pekar
M=D     //ändrar värdet på den addressen
@SP
M=M+1

//////////////////////////////
//pop local
@LCL
D=M     //hämtar local address
@index
D=A+D
@R13   //dest address
M=D
@SP     
AM=M-1   //minskar address och går dit SP pekar
D=M     //tar det värdet in i D
@R13
A=M
M=D


//pop static
@SP     
AM=M-1   //minskar address och går dit SP pekar
D=M     //tar det värdet in i D
@Foo.index        //här börjar static
M=D

//pop temp
@5
D=M     //hämtar local address
@index
D=A+D
@R13   //dest address
M=D
@SP     
AM=M-1   //minskar address och går dit SP pekar
D=M     //tar det värdet in i D
@R13
A=M
M=D

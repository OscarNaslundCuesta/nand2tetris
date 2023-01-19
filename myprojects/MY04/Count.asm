//counts
//Create a loop with a counter variable i. The counter variables initial value should be 1 
//and the loop should stop when the counter variable exceeds 10. During execution the 
//program should save the counter value to the RAM register that has the same index 
//as the counter value, as such we will be able to see how the counter variable has 
//incremented during execution. Following is the pseudo-code for the program:

@arr
M=1

@10
D=A
@n
M=D     //n blir 10

@i
M=0

(LOOP)  //loopar så länge inte i = n
@i
D=M
@n
D=D-M
@END
D;JEQ

@arr
D=M
@i
A=D+M
M=A     //i = addressen den printar på

@i
M=M+1      //i ökar med ett

@LOOP
0;JMP

(END)
@END
0;JMP
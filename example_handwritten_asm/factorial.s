##def fact(N):
##    if N < 2:
##        return 1
##    else:
##        return N * fact(N - 1)
##
##def main():
##    a = fact(4)
##    b = fact(5)
##    c = a + b

main:
    addi a0, x0, 4  # Set N = 4
    jal  ra, fact   # Call factorial
    add  s0, a1, x0 # Move the return value into s0 i.e. a = fact(4)
    addi a0, x0, 5  # Set N = 5
    jal  ra, fact   # Call factorial
    add  s1, a1, x0 # Move the return value into s1 i.e. b = fact(5)
    add  a1, s0, s1 # Final result a0 = s0 + s1 i.e. c = a + b
    add  a0, x0, x0 # Return 0
    jal  x0, halt

fact:
    addi sp, sp, -16    # Make room for N, and Return address
    sw   ra, 8(sp)     # Store the return address
    sw   a0, 0(sp)     # Store N
    addi t0, x0, 2     # Test operand 
    slt  t1, a0, t0    # N < 2
    beq  t1, x0, calc  # If N > 2, calculate N * fact(N - 1)
    addi a1, x0, 1     # Otherwise load 1
    jalr x0, ra, 0     # and return

calc:
    addi a0, a0, -1    # Calculate N - 1
    jal  ra, fact      # Call fact(N - 1)
    lw   a0, 0(sp)
    mul  a1, a1, a0
    lw   ra, 8(sp)
    addi sp, sp, 16
    jalr x0, ra, 0

halt:
    add x0, x0, x0 # no operation
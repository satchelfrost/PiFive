from .output import Output

# Assembler directives for gcc
def function_header(out : Output, name):
    out.writeln("\t.align 1")
    out.writeln("\t.globl " + name)
    out.writeln("\t.type " + name + ", @function")

def function_prolog(out : Output, framesize):
    out.writeln("\taddi sp, sp, -" + str(framesize))
    out.writeln("\tsd ra, " + str(framesize - 8) + "(sp)")
    out.writeln("\tsd fp, " + str(framesize - 16)+ "(sp)")
    out.writeln("\taddi fp, sp, " + str(framesize))

def function_epilogue(out : Output, framesize):
    out.writeln("\tld ra, " + str(framesize - 8) + "(sp)")
    out.writeln("\tld fp, " + str(framesize - 16)+ "(sp)")
    out.writeln("\taddi sp, sp, " + str(framesize))

# Assembler directives for gcc
def function_footer(out : Output, name):
    out.writeln("\t.size " + name + ", .-" + name)
import ast
import sys

class Output:
    def __init__(self, output_file=sys.stdout):
        self.output_file = output_file

    def write(self, text):
        print(text, file=self.output_file, end="")

    def writeln(self, text):
        print(text, file=self.output_file)


class PiFive:
    def __init__(self):
        self.out = Output()

    def compile(self, node):
        self.visit(node)

    def visit(self, node):
        name = node.__class__.__name__
        attr = getattr(self, 'visit_' + name, None)
        assert attr is not None, '{} not supported - node {}'.format(name, ast.dump(node))
        attr(node)
    
    # Assembler directives for gcc
    def function_header(self, name):
        self.out.writeln("\t.align 1")
        self.out.writeln("\t.globl " + name)
        self.out.writeln("\t.type " + name + ", @function")
    
    def function_prolog(self, framesize):
        self.out.writeln("\taddi sp, sp, -" + str(framesize))
        self.out.writeln("\tsd ra, " + str(framesize - 8) + "(sp)")
        self.out.writeln("\tsd fp, " + str(framesize - 16)+ "(sp)")
        self.out.writeln("\taddi fp, sp, " + str(framesize))

    def function_epilogue(self, framesize):
        self.out.writeln("\tld ra, " + str(framesize - 8) + "(sp)")
        self.out.writeln("\tld fp, " + str(framesize - 16)+ "(sp)")
        self.out.writeln("\taddi sp, sp, " + str(framesize))

    # Assembler directives for gcc
    def function_footer(self, name):
        self.out.writeln("\t.size " + name + ", .-" + name)
    
    def visit_Module(self, node : ast.Module):
        for stmt in node.body:
            self.visit(stmt)
    
    def visit_FunctionDef(self, node : ast.FunctionDef):
        self.function_header(node.name)
        self.out.write(node.name + ":\n")
        self.function_prolog(24) # Hardcode for now, until we figure out how to determine framesize
        for stmt in node.body:
            self.visit(stmt)
        self.function_epilogue(24) # Hardcode for now, until we figure out how to determine framesize
        self.function_footer(node.name)

    def visit_Return(self, node : ast.Return):
        self.visit(node.value)

    def visit_BinOp(self, node : ast.BinOp):
        self.visit(node.left)
        self.visit(node.op)
        self.visit(node.right)

    def visit_Constant(self, node : ast.Constant):
        self.out.write(node.value)
    
    def visit_Assign(self, node : ast.Assign):
        for target in node.targets:
            self.visit(target)
        
        self.visit(node.value)

    def visit_AnnAssign(self, node : ast.AnnAssign):
        cpp_type = self.type_lookup(node.annotation.id) 
        self.out.write(cpp_type)
        self.visit(node.target)
        self.visit(node.value)

    def visit_Name(self, node : ast.Name):
        self.out.writeln()
    
    def visit_Mult(self, node : ast.Mult):
        self.out.writeln("\tmul")



if __name__ == '__main__':
    file_name = 'input.py'
    with open(file_name) as file:
        source = file.read()

node = ast.parse(source, filename=file_name)
compiler = PiFive()
compiler.compile(node)

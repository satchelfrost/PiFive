from .transpiler import RISCV_Transpiler 
from ast import parse

def run_pifive(file_name, print, comments, output_file):
  with open(file_name) as file:
    source = file.read()
    node = parse(source, filename=file_name)
    rv_transpiler = RISCV_Transpiler(comments)
    rv_transpiler.transpile(node)

    # prints to console if print is true
    if print:
      rv_transpiler.instr.print()

    with open(output_file, 'w') as output:
      for line in rv_transpiler.instr.instr_buffer:
        output.write(line + '\n')

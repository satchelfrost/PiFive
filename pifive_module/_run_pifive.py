from .transpiler import RISCV_Transpiler 
from ast import parse

def run_pifive(file_name):
    with open(file_name) as file:
        source = file.read()
        node = parse(source, filename=file_name)
        rv_transpiler = RISCV_Transpiler()
        rv_transpiler.transpile(node)
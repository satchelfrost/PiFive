# PiFive - The Python to RISC-V Transpiler

## Table of Contents
* [Overview](#overview)
* [Defining the Subset of Python](#defining-the-subset-of-python)
* [References & Source Material](#references-&-source-material)
* [Software Setup / Compiling for Real Hardware](#software-setup)

## Overview

PiFive translates a sub-set of python source code to RISC-V assembly language.

![](PiFive.png)

## Defining the Subset of Python 

Normally, one would define the language using a grammar (for example, utilizing a Backus-Naur-like form), this is especially useful when we are writing the lexer/parser from scratch. However, the Python [ast module](https://docs.python.org/3/library/ast.html) already handles lexing/parsing for us. Hence, the focus of this project isn't so much building or even populating the abstract syntax tree (ast), but instead deciding what to do with each node as it is visited in the tree. To digress slightly, if we use the `ast` module to parse a python script which utilizes a class, but we have not implmented a way to translate classes to assembly, then we will need to throw an exception. First, we need to concretely define which features we will use.

There is a convenient notation utilized by the `ast` module called Abstract Syntax Description Language (ASDL). The ASDL for the full version for Python can be found [here](https://docs.python.org/3/library/ast.html). Amazingly, it expresses all of Python in less than 150 lines of text. It reads very much like a typical grammar, but instead of glancing from the level of syntax/characters (as a normal grammar does), we view the language at a higher, more abstract level; namely, the level of the nodes themselves. 

It is an especially helpful reference when debugging as well, because the names used in the `ASDL` are the names one can find in the Python debugger when visiting each node in the `ast`. For example, suppose we had the following python syntax as input:

```python
def square(x : int) -> int:
    return x * x
```

The first node in the `ASDL` we would encounter using a debugger would be `ast.Module` followed by `ast.FunctionDef` followed by `ast.Return`, etc. As one steps through the debugger and references the `ASDL`, it begins to make sense how the parser has put together the tree.

`PiFive`'s ASDL:

```python
module Python
{
    mod = Module(stmt* body, type_ignore* type_ignores)

    stmt = FunctionDef(identifier name, arguments args,
                       stmt* body, expr* decorator_list, expr? returns,
                       string? type_comment)
          | Return(expr? value)

          | Assign(expr* targets, expr value, string? type_comment)

          -- use 'orelse' because else is a keyword in target languages
          | While(expr test, stmt* body, stmt* orelse)
          | If(expr test, stmt* body, stmt* orelse)

          | Expr(expr value)

          -- col_offset is the byte offset in the utf8 string the parser uses
          attributes (int lineno, int col_offset, int? end_lineno, int? end_col_offset)

    expr = BinOp(expr left, operator op, expr right)
         | UnaryOp(unaryop op, expr operand)
         | Call(expr func, expr* args, keyword* keywords)
         | Constant(constant value, string? kind)
         | Compare(expr left, cmpop* ops, expr* comparators)

         -- the following expression can appear in assignment context
         | Name(identifier id, expr_context ctx)

          -- col_offset is the byte offset in the utf8 string the parser uses
          attributes (int lineno, int col_offset, int? end_lineno, int? end_col_offset)

    expr_context = Load | Store | Del

    operator = Add | Sub | Mult | MatMult | Div | Mod | Pow | LShift
                 | RShift | BitOr | BitXor | BitAnd | FloorDiv

    cmpop = Eq | NotEq | Lt | LtE | Gt | GtE

    arguments = (arg* posonlyargs, arg* args, arg? vararg, arg* kwonlyargs,
                 expr* kw_defaults, arg? kwarg, expr* defaults)

    arg = (identifier arg, expr? annotation, string? type_comment)
           attributes (int lineno, int col_offset, int? end_lineno, int? end_col_offset)
}
```

## References & Source Material

There are several references that I will place here which are either instructional or relevent in some way.

\<Reference Type\> : \<Description\> : \<Link(s)\>

1. *Website* : The original project that spawned the idea for this project *Compiling Python syntax to x86-64 assembly for fun and (zero) profit*] : [blog post](https://benhoyt.com/writings/pyast64/https://my.url.com) + [open source project](https://github.com/benhoyt/pyast64).
2. *Website* : Python ast module : [latest](https://docs.python.org/3/library/ast.html)
3. *Document* : HiFive Unmatched Software Reference Manual : [manual](https://www.sifive.com/boards/hifive-unmatched)
4. *Document* : RISC-V Specification document : [spec](https://riscv.org/technical/specifications/)
5. *Book* : RISC-V Assembly Language, Anthony J. Dos Reis
6. *Book* : The RISC-V Reader, Patterson & Waterman 
7. *Book* : Computer Architecture A Quantitative Approach, Patterson & Hennessy Computer Architecture A Quantitative 
8. *Book* : Engineering A Compiler, Cooper & Torczon
9. *Website* : Python to C++ transpiler : [link](https://github.com/lukasmartinelli/py14) 

## Using PiFive

In order to see all of the available options simply run:

```bash
$ python3 -m pifive -h
```

For example to transpile the `factorial.py` example run:

```bash
$ python3 -m pifive factorial.py -c -p -o factorial.s
```

>**Note** that the `-h` explains what each of the flags do.

Here's a very small snippet of the output:

```mips
factorial:
	# Prologue for "factorial"
	addi sp, sp, -24
	sd ra, 16(sp)
	sd fp, 8(sp)
	addi fp, sp, 24

	# Push variable "n" in register "a1" to stack
	addi sp, sp, -8
	sd a1, 0(sp)

	# Push value "0" to the stack
	addi sp, sp, -8
	li t0, 0
	sd t0, 0(sp)
	# Register "t0" freed
```

You should then be able to compile it using gcc. Of course you won't be able to run it unless you have an emulator or actual hardware.

```bash
$ gcc -o factorial factorial.s
```

>**Note** I'm using the word compile here as opposed to transpile because gcc will actuall translate it to raw binary.

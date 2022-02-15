# PiFive - The Python to RISC-V Transpiler

## Table of Contents
* [Overview](#overview)
* [References & Source Material](#references)
* [Software Setup](#setup)

<a name="overview"></a>
## Overview

PiFive translates a sub-set of python source code to RISC-V assembly language.

![](PiFive.png)

Throughout the semester I will be organizing the project using Trello a software organization tool; a link to that board can be found [here](https://trello.com/b/26kdfMJz/senior-project). In addition, I will be updating a slide deck to organize my thoughts and build towards the final presentation; a link to that slide deck can be found here [here](https://docs.google.com/presentation/d/1rj_9L3pqZ0XZLCmFNdeaLof7cu6qTt5_TXOBURj3eK4/edit#slide=id.g113c484dce6_0_274).

<a name="references"></a>
## References & Source Material

\<Reference Type\> : \<Description\> : \<Link(s)\>

1. *Website* : The original project that spawned the idea for this project *Compiling Python syntax to x86-64 assembly for fun and (zero) profit*] : [blog post](https://benhoyt.com/writings/pyast64/https://my.url.com) + [open source project](https://github.com/benhoyt/pyast64).

2. *Document* : RISC-V Specification document
3. *Document* : HiFive Unmatched Software Reference Manual
4. *Book* : RISC-V Assembly Language, Anthony J. Dos Reis
5. *Book* : The RISC-V Reader, Patterson & Waterman 
6. *Book* : Computer Architecture A Quantitative Approach, Patterson & HennessyComputer Architecture A Quantitative 
7. *Book* : Engineering A Compiler, Cooper & Torczon
8. *Website* : Python ast module : [latest](https://docs.python.org/3/library/ast.html)

<a name="setup"></a>
## Software Setup

Aside from Python 3.9.7+, there are no software requirements in order to run this project. However, if you wish to compile the transpiled assembly down to a raw executable which can be run on real hardware (i.e. HiFive Unmatched), then the following steps, which can be found in reference [3], are required. 
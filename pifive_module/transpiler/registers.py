from enum import Enum

class Reg(Enum):
  zero = 0
  ra = 1
  sp = 2
  gp = 3
  tp = 4
  t0 = 5
  t1 = 6
  t2 = 7
  fp = 8 # aka s0
  s1 = 9
  a0 = 10
  a1 = 11
  a2 = 12
  a3 = 13
  a4 = 14
  a5 = 15
  a6 = 16
  a7 = 17
  s2 = 18
  s3 = 19
  s4 = 20
  s5 = 21
  s6 = 22
  s7 = 23
  s8 = 24
  s9 = 25
  s10 = 26
  s11 = 27
  t3 = 28
  t4 = 29
  t5 = 30
  t6 = 31

class RegType(Enum):
  temp_regs = [
    Reg.t0,
    Reg.t1,
    Reg.t2,
    Reg.t3,
    Reg.t4,
    Reg.t5,
    Reg.t6
  ]
  saved_regs = [
    Reg.s1,
    Reg.s2,
    Reg.s3,
    Reg.s4,
    Reg.s5,
    Reg.s6,
    Reg.s7,
    Reg.s8,
    Reg.s9,
    Reg.s10,
    Reg.s11
  ]
  arg_regs = [
    Reg.a1,
    Reg.a2,
    Reg.a3,
    Reg.a4,
    Reg.a5,
    Reg.a6,
    Reg.a7
  ]

def print_reg_type_info(reg_type : RegType):
  print(f"\"{reg_type.name}\" info:")
  for reg in reg_type.value:
    print(f"name {reg.name}, value {reg.value}") 
  print("")

if __name__ == "__main__":
  print_reg_type_info(RegType.temp_regs)
  print_reg_type_info(RegType.saved_regs)
  print_reg_type_info(RegType.arg_regs)
  print(f"Length of registers {len(Reg)}")
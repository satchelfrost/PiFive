from .registers import Reg, RegType

class RegPool:
  def __init__(self):
    self.reset()

  def reset(self):
    self.available_regs = [True for i in range(len(Reg))]
  
  def get_next_reg(self, reg_type : RegType):
    # Get next available register of a particular type
    for reg in reg_type.value:
      if self.available_regs[reg.value]:
        self.available_regs[reg.value] = False
        return reg
    return None
  
  def restore_reg(self, reg : Reg):
    # Make a register available again
    self.available_regs[reg.value] = True
  
  def take_reg(self, reg : Reg):
    # Make a register unavailable
    self.available_regs[reg.value] = False
  
  def idx_of_regs_in_use(self):
    regs_in_use = []
    for idx, reg in enumerate(self.available_regs):
      if not reg:
        regs_in_use.append(idx)
    return regs_in_use

if __name__ == "__main__":
  reg_pool = RegPool()
  temp_reg_1 = reg_pool.get_next_reg(RegType.temp_regs)
  temp_reg_2 = reg_pool.get_next_reg(RegType.temp_regs)
  save_reg_1 = reg_pool.get_next_reg(RegType.arg_regs)
  print(f"temp_reg_1: name {temp_reg_1.name}, value {temp_reg_1.value}")
  print(f"temp_reg_2: name {temp_reg_2.name}, value {temp_reg_2.value}")
  print(f"save_reg_1: name {save_reg_1.name}, value {save_reg_1.value}")
  print("Regs in use")
  print(reg_pool.idx_of_regs_in_use())
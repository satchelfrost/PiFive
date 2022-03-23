import ast
from .scope import Scope, Variable
from .instruction_maker import InstructionMaker, Binop
from .register_pool import RegPool
from .registers import Reg, RegType
from .symbol_table import SymbolTable, SymbolKind

class RISCV_Transpiler:
  def __init__(self, comments_on=False):
    self.sym_tab = SymbolTable()
    self.scope = Scope()
    self.instr = InstructionMaker(comments_on)
    self.reg_pool = RegPool()

  def reset(self):
    self.scope = Scope('global')
    self.reg_pool.reset()
    self.instr.reset()
    self.sym_tab.reset()

  def transpile(self, node):
    # Insert header here
    self.instr.newline()
    self.visit(node)
    # Insert footer here

  def assign_reg_if_none(self, var : Variable):
    if not var.reg:
      if not self.reg_pool.is_reg_type_avilable(RegType.temp_regs):
        self.sym_tab.free_and_save_reg(self.scope.frame, self.instr)
      var.reg = self.reg_pool.get_next_reg(RegType.temp_regs)

  def get_new_temp(self) -> Reg:
    if not self.reg_pool.is_reg_type_avilable(RegType.temp_regs):
      self.sym_tab.free_and_save_reg(self.scope.frame, self.instr)
    return self.reg_pool.get_next_reg(RegType.temp_regs)

  def anonymous_push(self, value : str):
    '''push value to the stack with reg that has no associated variable'''
    new_temp : Reg = self.get_new_temp()
    self.instr.comment(f'Push value "{value}" to the stack')
    self.instr.push(new_temp, value)
    self.reg_pool.restore_reg(new_temp)
    self.instr.comment(f'Register {new_temp.name} freed')
    self.instr.newline()

  def visit(self, node):
    name = node.__class__.__name__
    attr = getattr(self, 'visit_' + name, None)
    if attr:
      attr(node)
    else:
      raise RuntimeError(f"{name} not supported. Node dump: {ast.dump(node)}")

  def visit_Module(self, node : ast.Module):
    for stmt in node.body:
      self.visit(stmt)

  def visit_FunctionDef(self, node : ast.FunctionDef):
    pass

  def visit_Return(self, node : ast.Return):
    self.visit(node.value)

  def visit_BinOp(self, node : ast.BinOp):
    self.visit(node.left)
    self.visit(node.right)
    self.visit(node.op)

  def visit_Constant(self, node : ast.Constant):
    self.anonymous_push(str(node.value))

  def visit_Name(self, node : ast.Name):
    # Check if variable exists in current scope
    var : Variable = self.scope.lookup_var(node.id)

    # Check the node's context: Load, Store, or Del
    if isinstance(node.ctx, ast.Load):
      if not var:
        raise RuntimeError(f'Variable "{node.id}" undefined in current scope. Cannot load.')
    elif isinstance(node.ctx, ast.Store):
      if not var:
        new_var = Variable(node.id)
        self.scope.add_var(new_var)
        self.sym_tab.add_symbol(self.scope.frame, new_var)
    else:
      raise RuntimeError(f'Contenxt type "{node.ctx}" unsupported in visit_Name().')

  def visit_Assign(self, node : ast.Assign):
    # Check if single target
    if len(node.targets) != 1:
      raise RuntimeError("Only single assignment allowed.")

    # Check if target is assignable
    target : ast.Name = node.targets[0]
    if not isinstance(target, ast.Name):
      raise RuntimeError(f'Assignment of target "{target}" not accepted.')

    # visit target and value
    self.visit(target)
    self.visit(node.value)

    target_var : Variable = self.sym_tab.lookup_symbol(target.id, self.scope.frame, SymbolKind.variable)
    self.assign_reg_if_none(target_var)

    self.instr.comment(f'Target assignment variable "{target_var.name}"')
    if isinstance(node.value, ast.Name):
      value_var : Variable = self.sym_tab.lookup_symbol(node.value.id, self.scope.frame, SymbolKind.variable)
      self.assign_reg_if_none(value_var)
      self.instr.mv(target_var.reg, value_var.reg)
    else:
      self.instr.comment(f'popping stack into "{target_var.reg.name}"')
      self.instr.pop(target_var.reg)
    
    self.instr.newline()

    # if isinstance(node.value, ast.Constant):
    #   self.instr.pop(target_var.reg)
    # elif isinstance(node.value, ast.Name):
    #   value_var : Variable = self.sym_tab.lookup_symbol(node.value.id, self.scope.frame, SymbolKind.variable)
    #   self.assign_reg_if_none(value_var)
    #   self.instr.mv(target_var.reg, value_var.reg)
    # else:
    #   raise RuntimeError(f'Assignment of value "{node.value}" not accepted.')
  
  def visit_AnnAssign(self, node : ast.AnnAssign):
    pass

  def generic_binop(self, binop : Binop):
    temp_1 : Reg = self.get_new_temp()
    self.instr.comment(f'Activate "{temp_1.name}" by popping stack.')
    self.instr.pop(temp_1)
    self.instr.newline()

    temp_2 : Reg = self.get_new_temp()
    self.instr.comment(f'Activate "{temp_2.name}" by popping stack.')
    self.instr.pop(temp_2)
    self.instr.newline()

    self.instr.comment(f'Adding result and storing into "{temp_1.name}"')
    self.instr.binop(binop.value, temp_2, temp_2, temp_1)
    self.reg_pool.restore_reg(temp_1)
    self.instr.comment(f'Register {temp_1.name} freed')
    self.instr.newline()

    self.instr.comment(f'Pushing result stored in "{temp_2.name}" to stack')
    self.instr.push_reg(temp_2)
    self.reg_pool.restore_reg(temp_2)
    self.instr.comment(f'Register {temp_2.name} freed')
    self.instr.newline()


  def visit_Add(self, node : ast.Add):
    self.generic_binop(Binop.ADD)

  def visit_Sub(self, node : ast.Sub):
    self.generic_binop(Binop.SUB)

  def visit_And(self, node : ast.And):
    self.generic_binop(Binop.AND)

  def visit_BitAnd(self, node : ast.BitAnd):
    self.generic_binop(Binop.AND)

  def visit_Or(self, node : ast.Or):
    self.generic_binop(Binop.OR)

  def visit_BitOr(self, node : ast.BitOr):
    self.generic_binop(Binop.OR)
  
  def visit_BitXor(self, node : ast.BitXor):
    self.generic_binop(Binop.XOR)

  def visit_Mult(self, node : ast.Mult):
    self.generic_binop(Binop.MUL)

  def visit_Div(self, node : ast.Div):
    self.generic_binop(Binop.DIV)

  def visit_For(self, node : ast.For):
    pass

  def visit_While(self, node : ast.For):
    pass

  def visit_If(self, node : ast.If):
    pass

  def visit_Expr(self, node : ast.Expr):
    pass

  def visit_BoolOp(self, node : ast.BoolOp):
    pass

  def visit_UnaryOp(self, node : ast.UnaryOp):
    pass

  def visit_Call(self, node : ast.Call):
    pass

  def visit_Attribute(self, node : ast.Attribute):
    pass
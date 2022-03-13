import ast
from .scope import Scope, Variable
from .instruction_maker import InstructionMaker
from .register_pool import RegPool
from .registers import Reg, RegType

class RISCV_Transpiler:
  def __init__(self):
    self.scope = Scope('global')
    self.instr = InstructionMaker()
    self.reg_pool = RegPool()

  def reset(self):
    self.scope = Scope('global')
    self.reg_pool.reset()
    self.instr.reset()

  def transpile(self, node):
    # Insert header here
    self.visit(node)
    # Insert footer here

  def visit(self, node):
    name = node.__class__.__name__
    attr = getattr(self, 'visit_' + name, None)
    if attr is not None:
      return attr(node)
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
    self.visit(node.op)
    self.visit(node.right)

  def visit_Constant(self, node : ast.Constant):
    return node.value

  def visit_Name(self, node : ast.Name):
    # Check if variable exists in current scope
    var : Variable = self.scope.lookup_var(node.id)

    # Check the node's context: Load, Store, or Del
    if isinstance(node.ctx, ast.Load):
      if var:
        return var
      else:
        raise RuntimeError(f"Variable \"{node.id}\" undefined in current scope")
    elif isinstance(node.ctx, ast.Store):
      if var:
        return var
      else:
        temp_reg = self.reg_pool.get_next_reg(RegType.temp_regs)
        return self.scope.add_var(Variable(node.id, reg=temp_reg))
    else:
      raise RuntimeError(f"Contenxt type \"{node.ctx}\" unsupported in visit_Name()")

  def visit_Assign(self, node : ast.Assign):
    # Check if single target
    if len(node.targets) != 1:
      raise RuntimeError("Mutiple target assignments not allowed!")

    # Check if target is assignable
    target = node.targets[0]
    if not isinstance(target, ast.Name):
      raise RuntimeError(f"Assignment of target \"{target}\" not accepted!")

    # Obtain target variable
    target_var : Variable = self.visit(target)

    # Create instruction depending on value to assign
    if isinstance(node.value, ast.Constant):
      self.instr.load_imm(target_var.reg, self.visit(node.value))
    elif isinstance(node.value, ast.Name):
      value_var : Variable = self.visit(node.value)
      self.instr.mv(target_var.reg, value_var.reg)
    else:
      raise RuntimeError(f"Assignment of value \"{node.value}\" not accepted!")

  def visit_AnnAssign(self, node : ast.AnnAssign):
    pass

  def visit_Mult(self, node : ast.Mult):
    pass

  def visit_For(self, node : ast.For):
    pass

  def visit_While(self, node : ast.For):
    pass

  def visit_If():
    pass

  def visit_Expr():
    pass

  def visit_BoolOp(self, node : ast.BoolOp):
    pass

  def visit_BinOp(self, node : ast.BinOp):
    pass

  def visit_UnaryOp(self, node : ast.UnaryOp):
    pass

  def visit_Call(self, node : ast.Call):
    pass

  def visit_Attribute(self, node : ast.Attribute):
    pass
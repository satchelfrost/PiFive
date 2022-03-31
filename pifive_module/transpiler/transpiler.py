import ast
from .scope import Scope, Variable
from .instruction_maker import InstructionMaker, BinOp, BranchOp
from .register_pool import RegPool
from .registers import Reg, RegType
from .symbol_table import SymbolTable

class RISCV_Transpiler:
  def __init__(self, comments_on=False):
    self.sym_tab = SymbolTable()
    self.scope = Scope()
    self.instr = InstructionMaker(comments_on)
    self.reg_pool = RegPool()

  ### Helper Functions ###
  def reset(self):
    self.scope = Scope()
    self.reg_pool.reset()
    self.instr.reset()
    self.sym_tab.reset()

  def transpile(self, node):
    # Insert header here
    self.instr.newline()
    self.visit(node)
    # Insert footer here

  def assign_reg_if_none(self, var : Variable):
    '''Check if variable has active register, and if not then get one'''
    if not var.reg:
      if not self.reg_pool.is_reg_type_avilable(RegType.temp_regs):
        self.sym_tab.save_and_free_reg(self.scope.frame, self.instr)
      var.reg = self.reg_pool.get_next_reg(RegType.temp_regs)

  def get_new_temp(self) -> Reg:
    '''Get a new temporary register'''
    if not self.reg_pool.is_reg_type_avilable(RegType.temp_regs):
      self.sym_tab.save_and_free_reg(self.scope.frame, self.instr)
    return self.reg_pool.get_next_reg(RegType.temp_regs)

  def anonymous_push(self, value : str):
    '''push value to the stack with reg that has no associated variable'''
    temp : Reg = self.get_new_temp()
    self.instr.comment_push_val(value)
    self.instr.push(temp, value)
    self.reg_pool.free_reg(temp)
    self.instr.comment_reg_free(temp)
    self.instr.newline()

  def create_label(self, name : str):
    return f"{name}_fr_{self.scope.frame}_sc_{self.scope.scope_id}_num_{self.scope.get_next_label_number()}"

  #### Visitor Nodes ####
  def visit(self, node):
    '''Generic visitor for all nodes'''
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
    # If var is not in current scope it's value will be None
    var : Variable = self.scope.lookup_var(node.id)

    # Check the node's context: Load, Store, or Del
    if isinstance(node.ctx, ast.Load):
      if not var:
        raise RuntimeError(f'Variable "{node.id}" undefined in current scope. Cannot load.')
      self.instr.comment_reg_push(var.reg, var.name)
      self.instr.push_reg(var.reg)
      self.instr.newline()
    elif isinstance(node.ctx, ast.Store):
      if not var:
        var = Variable(node.id)
        self.scope.add_var(var)
        self.sym_tab.add_symbol(self.scope.frame, var)
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

    # Assign variable by popping the stack
    target_var : Variable = self.scope.lookup_var(target.id)
    self.assign_reg_if_none(target_var)
    self.instr.comment_assign(target_var.name)
    self.instr.comment_pop(target_var.reg)
    self.instr.pop(target_var.reg)
    self.instr.newline()

  def generic_binop(self, binop : BinOp):
    right : Reg = self.get_new_temp()
    self.instr.comment_pop(right)
    self.instr.pop(right)
    self.instr.newline()

    left : Reg = self.get_new_temp()
    self.instr.comment_pop(left)
    self.instr.pop(left)
    self.instr.newline()

    self.instr.comment_binop(binop, left)
    self.instr.binop(binop, left, left, right)
    self.reg_pool.free_reg(right)
    self.instr.comment_reg_free(right)
    self.instr.newline()

    self.instr.comment_binop_push(binop, left)
    self.instr.push_reg(left)
    self.reg_pool.free_reg(left)
    self.instr.comment_reg_free(left)
    self.instr.newline()

  def visit_Add(self, node : ast.Add):
    self.generic_binop(BinOp.ADD)

  def visit_Sub(self, node : ast.Sub):
    self.generic_binop(BinOp.SUB)

  def visit_And(self, node : ast.And):
    self.generic_binop(BinOp.AND)

  def visit_BitAnd(self, node : ast.BitAnd):
    self.generic_binop(BinOp.AND)

  def visit_Or(self, node : ast.Or):
    self.generic_binop(BinOp.OR)

  def visit_BitOr(self, node : ast.BitOr):
    self.generic_binop(BinOp.OR)
  
  def visit_BitXor(self, node : ast.BitXor):
    self.generic_binop(BinOp.XOR)

  def visit_Mult(self, node : ast.Mult):
    self.generic_binop(BinOp.MUL)

  def visit_Div(self, node : ast.Div):
    self.generic_binop(BinOp.DIV)

  def visit_Compare(self, node : ast.Compare):
    self.visit(node.left)

    if len(node.comparators) != 1:
      raise RuntimeError("Only single comparison allowed.")
    self.visit(node.comparators[0])

    if len(node.ops) != 1:
      raise RuntimeError("Only single comparison operator allowed.")
    self.visit(node.ops[0])

  def generic_branch_cmp(self, branchop : BranchOp):
    right : Reg = self.get_new_temp()
    self.instr.comment_pop(right)
    self.instr.pop(right)
    self.instr.newline()

    left : Reg = self.get_new_temp()
    self.instr.comment_pop(left)
    self.instr.pop(left)
    self.instr.newline()

    # Create a result register to push the result of the comparison
    result : Reg = self.get_new_temp()
    self.instr.comment_branchop_result(branchop, True)
    self.instr.set_true(result)
    self.instr.newline()

    # Carry out the comparison
    self.instr.comment_branchop(branchop, left, right)
    label = self.create_label(branchop.name)
    self.instr.branchop(branchop, left, right, label)
    self.reg_pool.free_reg(right)
    self.reg_pool.free_reg(left)
    self.instr.comment_reg_free(right)
    self.instr.comment_reg_free(left)
    self.instr.newline()

    # No branch taken label
    self.instr.comment_branchop_result(branchop, False)
    self.instr.set_false(result)
    self.instr.newline()

    # Push the result to the stack
    self.instr.label(label)
    self.instr.comment_branchop_push(branchop, result)
    self.instr.push_reg(result)
    self.reg_pool.free_reg(result)
    self.instr.comment_reg_free(result)
    self.instr.newline()

  def visit_Lt(self, node : ast.Lt):
    self.generic_branch_cmp(BranchOp.BLT)

  def visit_LtE(self, node : ast.LtE):
    self.generic_branch_cmp(BranchOp.BLE)

  def visit_Gt(self, node : ast.Gt):
    self.generic_branch_cmp(BranchOp.BGT)

  def visit_GtE(self, node : ast.GtE):
    self.generic_branch_cmp(BranchOp.BGE)

  def visit_Eq(self, node : ast.Eq):
    self.generic_branch_cmp(BranchOp.BEQ)

  def visit_NotEq(self, node : ast.NotEq):
    self.generic_branch_cmp(BranchOp.BNE)

  def visit_While(self, node : ast.For):
    # Create a new scope
    self.scope = Scope(name=self.scope.frame, parent=self.scope)

    # Create a labels for the loop and break
    label_while = self.create_label("while")
    label_break = self.create_label("break")

    # Create a label and visit the test
    self.instr.label(label_while)
    self.visit(node.test)
    result : Reg = self.get_new_temp()
    self.instr.comment_pop(result)
    self.instr.pop(result)
    self.instr.newline()

    # Get the result of the test and branch to the break label if false
    self.instr.comment("Break if false")
    self.instr.branch_zero(result, label_break)
    self.reg_pool.free_reg(result)
    self.instr.comment_reg_free(result)
    self.instr.newline()

    # Visit the body
    for statement in node.body:
      self.visit(statement)
    self.instr.jump_label(label_while)
    self.instr.label(label_break)

    # Reset the scope
    self.scope = self.scope.parent

  def visit_If(self, node : ast.If):
    # Create a new scope
    self.scope = Scope(name=self.scope.frame, parent=self.scope)

    # Visit the test condition
    self.visit(node.test)

    label_else = self.create_label("else")
    label_end = self.create_label("end")

    # Grab the result of the test
    result : Reg = self.get_new_temp()
    self.instr.comment_pop(result)
    self.instr.pop(result)
    self.instr.newline()

    # If the result is false, jump to the else block
    self.instr.comment("If condition is false, jump to else")
    self.instr.branch_zero(result, label_else)
    self.reg_pool.free_reg(result)
    self.instr.comment_reg_free(result)
    self.instr.newline()

    # Visit the body of the if
    for statement in node.body:
      self.visit(statement)

    # Visit the orelse
    if node.orelse:
      self.instr.comment("If else wasn't taken, jump to end")
      self.instr.jump_label(label_end)
      self.instr.newline()

    # Label the else/elsif
    self.instr.label(label_else)

    # Visit the orelse statements
    for statement in node.orelse:
      self.visit(statement)

    # Label the end if necessary
    if node.orelse:
      self.instr.label(label_end)

    # Reset the scope
    self.scope = self.scope.parent

  def visit_Expr(self, node : ast.Expr):
    self.visit(node.value)

  def visit_Call(self, node : ast.Call):
    pass
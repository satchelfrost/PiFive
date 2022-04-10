import ast
from .scope import Scope, Variable
from .instruction_maker import InstructionMaker, BinOp, BranchOp
from .register_pool import RegPool
from .registers import Reg, RegType
from .symbols import Function
from .locals_counter import LocalsCounter

class RISCV_Transpiler:
  def __init__(self, comments_on=False):
    self.scope = Scope()
    self.instr = InstructionMaker(comments_on)
    self.reg_pool = RegPool()
    self.aliased = {"print" : self.print_routine}
    self.print_label = False

  ### Helper Functions ###
  def reset(self):
    self.scope = Scope()
    self.reg_pool.reset()
    self.instr.reset()

  def transpile(self, node):
    self.instr.newline()
    self.visit(node)
    if self.print_label:
      self.instr.print_int_label()

  def assign_reg_if_inactive(self, var : Variable, reg_type : RegType):
    '''Check if variable has active register, and if not then get one'''
    if not var.reg_active:
      if not self.reg_pool.is_reg_type_available(reg_type):
        self.restore_reg_type(reg_type)
      if not self.reg_pool.is_reg_type_available(reg_type):
        raise RuntimeError(f'Failed to restore reg of type "{reg_type.name}"')
      var.reg = self.reg_pool.get_next_reg(reg_type)
      var.reg_active = True

  def assign_regs_if_inactive(self, regs : list, reg_type : RegType):
    for reg in regs:
      self.assign_reg_if_inactive(reg, reg_type)

  def restore_reg_type(self, reg_type : RegType):
    var : Variable = self.scope.get_next_var(reg_type)
    self.save_var_to_stack(var)

  def save_var_to_stack(self, var : Variable):
    if var.reg is None:
      raise RuntimeError(f'Register is none for variable "{var.name}"')
    var.reg_active = False
    self.instr.comment(f'Saving reg "{var.reg.name}" to stack')
    self.instr.store_reg(var.reg, var.offset)
    self.reg_pool.free_reg(var.reg)
    self.instr.comment_reg_free(var.reg)
    self.instr.newline()

  def save_vars_to_stack(self, vars : list):
    for var in vars:
      self.save_var_to_stack(var)

  def load_var_from_stack(self, var : Variable):
    if var.reg is None:
      raise RuntimeError(f'Register is none for variable "{var.name}"')
    var.reg_active = True
    self.instr.comment(f'Loading reg "{var.reg.name}" from stack')
    self.instr.load_reg(var.reg, var.offset)
    self.reg_pool.take_reg(var.reg)
    self.instr.newline()

  def load_vars_from_stack(self, vars : list):
    for var in vars:
      self.load_var_from_stack(var)

  def get_new_temp(self) -> Reg:
    '''Get a new temporary register'''
    if not self.reg_pool.is_reg_type_available(RegType.temp_regs):
      self.restore_reg_type(RegType.temp_regs)
    if not self.reg_pool.is_reg_type_available(RegType.temp_regs):
      raise RuntimeError(f'Failed to restore reg of type "{RegType.temp_regs.name}"')
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
    return f"{name}_{self.scope.name}_sc_{self.scope.scope_num}_lab_{self.scope.get_next_label_number()}"

  def free_scope(self):
    '''Free registers in current scope and set scope to parent'''
    for reg in self.scope.deactivate_regs(self.reg_pool):
      self.instr.comment_reg_free(reg)
    self.instr.newline()
    self.scope = self.scope.parent

  def print_routine(self, node : ast.Call):
    # Set the print label
    self.print_label = True

    # Make sure there is only on argument
    if len(node.args) != 1:
      raise RuntimeError(f'Incorrect number of arguments for print function!')

    # Visit the argument
    self.visit(node.args[0])

    # Make sure that a0 and a1 are not used


    # Pop result into a1
    self.instr.comment_pop(Reg.a1)
    self.instr.pop(Reg.a1)
    self.instr.newline()

    # load the print_int label into a0
    self.instr.comment("Load print_int label into a0")
    self.instr.load_label(Reg.a0, "print_int")
    self.instr.newline()

    # Store any temporaries to the stack
    temps = self.scope.get_active_vars(RegType.temp_regs)
    self.save_vars_to_stack(temps)

    # Call the function
    self.instr.comment(f"Call funcion printf")
    self.instr.call("printf")
    self.instr.newline()

    # Restore any temporaries from the stack
    self.load_vars_from_stack(temps)

    # Push the result of the function call
    self.instr.comment(f'Push dummy result to stack')
    self.instr.push_reg(Reg.a0)
    self.instr.newline()

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
    for statement in node.body:
      self.visit(statement)

  def visit_FunctionDef(self, node : ast.FunctionDef):
    # Used to figure out how much stack space to allocate
    locals = LocalsCounter(node, self.scope)

    # Add this function to the current scope
    func_args = [Variable(arg.arg) for arg in node.args.args]
    self.assign_regs_if_inactive(func_args, RegType.arg_regs)
    self.scope.add_func(node.name, func_args)

    # Create a new scope
    self.scope = Scope(name=node.name, parent=self.scope, locals_count=locals.count())
    self.scope.add_vars(func_args)
    self.instr.label(node.name)
    self.instr.comment_prologue(node.name)
    self.instr.prologue(self.scope.locals_count)
    self.instr.newline()

    # Visit statements in function body
    for statement in node.body:
      self.visit(statement)

    # Force a void-return if no return exists
    if not isinstance(node.body[-1], ast.Return):
      self.instr.comment("Automatic void-return")
      self.instr.load_imm(Reg.a0, 0)
      self.instr.newline()
      self.instr.comment_epilogue(node.name)
      self.instr.epilogue(self.scope.locals_count)
      self.instr.newline()

    self.free_scope()

  def visit_Return(self, node : ast.Return):
    # Visit the return value
    self.visit(node.value)

    # Pop return value
    self.instr.comment("Pop return value")
    self.instr.pop(Reg.a0)
    self.instr.newline()

    # Add epilogue to return
    self.instr.comment_epilogue(self.scope.name)
    self.instr.epilogue(self.scope.locals_count) # epilogue includes "ret" instruction
    self.instr.newline()

  def visit_BinOp(self, node : ast.BinOp):
    self.visit(node.left)
    self.visit(node.right)
    self.visit(node.op)

  def visit_Constant(self, node : ast.Constant):
    self.anonymous_push(str(node.value))

  def visit_Name(self, node : ast.Name):
    # Check the node's context: Load, Store, or Del
    if isinstance(node.ctx, ast.Load):
      var : Variable = self.scope.lookup_var(node.id)
      if var.reg is None:
        reg : Reg = self.get_new_temp()
        self.instr.load_reg(reg, var.offset)
      self.instr.comment_reg_push(var.reg, var.name)
      self.instr.push_reg(var.reg)
      self.instr.newline()
    elif isinstance(node.ctx, ast.Store):
      self.scope.add_var(Variable(node.id))
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
    self.assign_reg_if_inactive(target_var, RegType.temp_regs)
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
    self.scope = Scope(name=self.scope.name, parent=self.scope, locals_count=self.scope.locals_count)

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

    self.free_scope()

  def visit_If(self, node : ast.If):
    # Visit the test condition
    self.visit(node.test)

    # Grab the result of the test
    result : Reg = self.get_new_temp()
    self.instr.comment_pop(result)
    self.instr.pop(result)
    self.instr.newline()

    # Create 1st scope
    self.scope = Scope(name=self.scope.name, parent=self.scope, locals_count=self.scope.locals_count)
    label_else = self.create_label("else")

    # If the result is false, jump to the else block
    self.instr.comment("If condition is false, jump to else")
    self.instr.branch_zero(result, label_else)
    self.reg_pool.free_reg(result)
    self.instr.comment_reg_free(result)
    self.instr.newline()

    # Visit the body of the if
    for statement in node.body:
      self.visit(statement)

    # Free the 1st scope
    self.free_scope()

    # Create 2nd scope
    self.scope = Scope(name=self.scope.name, parent=self.scope, locals_count=self.scope.locals_count)

    # Label end
    label_end = self.create_label("end")
    if node.orelse:
      self.instr.comment("If else wasn't taken, jump to end")
      self.instr.jump_label(label_end)
      self.instr.newline()

    # Create scope for else again
    self.instr.label(label_else)

    # Visit the orelse statements
    for statement in node.orelse:
      self.visit(statement)

    # Label the end if necessary
    if node.orelse:
      self.instr.label(label_end)

    # Free the 2nd scope
    self.free_scope()

  def visit_Expr(self, node : ast.Expr):
    # Check if we are calling main--special case
    if isinstance(node.value, ast.Call):
      call : ast.Call = node.value
      if call.func.id == "main":
        return

    # Visit the expression
    self.visit(node.value)

    # This will be the case when the expression is a call to a function
    self.instr.comment("Pop return value from expression")
    self.instr.pop(Reg.a0)
    self.instr.newline()

  def visit_Call(self, node : ast.Call):
    # Check for the built-in functions
    if node.func.id in self.aliased:
      aliased_routine = self.aliased[node.func.id]
      aliased_routine(node)
      return

    # First check if the number of arguments is correct
    func : Function = self.scope.lookup_func(node.func.id)
    if len(func.args) != len(node.args):
      raise RuntimeError(f'Incorrect number of arguments for function "{func.name}"!')

    # Visit the arguments
    self.instr.comment(f'Computing functional arguments for "{node.func.id}"')
    for arg in reversed(node.args):
      self.visit(arg)

    # Ensure that the function is called with arguments in the right registers
    for var_arg in func.args:
      self.instr.comment_pop(var_arg.reg)
      self.instr.pop(var_arg.reg)
      self.instr.newline()

    # Store any temporaries to the stack
    temps = self.scope.get_active_vars(RegType.temp_regs) 
    self.save_vars_to_stack(temps)

    # Call the function
    self.instr.comment(f'Call funcion "{node.func.id}"')
    self.instr.call(node.func.id)
    self.instr.newline()

    # Restore any temporaries from the stack
    self.load_vars_from_stack(temps)

    # Push the result of the function call
    self.instr.comment(f'Push result of "{node.func.id}" stored in "{Reg.a0.name}"')
    self.instr.push_reg(Reg.a0)
    self.instr.newline()
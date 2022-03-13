import ast

class RISCV_Transpiler:

  def transpile(self, node):
    self.visit(node)

  def visit(self, node):
    name = node.__class__.__name__
    attr = getattr(self, 'visit_' + name, None)
    assert attr is not None, '{} not supported - node {}'.format(name, ast.dump(node))
    attr(node)
  
  def visit_Module(self, node : ast.Module):
    for stmt in node.body:
      self.visit(stmt)
  
  def visit_FunctionDef(self, node : ast.FunctionDef):
    self.function_header(node.name)
    self.buffer.write(node.name + ":\n")
    self.function_prolog(24) # Hardcode for now, until we figure out how to determine framesize
    for stmt in node.body:
      self.visit(stmt)
    self.function_epilogue(24) # Hardcode for now, until we figure out how to determine framesize
    self.function_footer(node.name)

  def visit_Return(self, node : ast.Return):
    self.visit(node.value)

  def visit_BinOp(self, node : ast.BinOp):
    self.visit(node.left)
    self.visit(node.op)
    self.visit(node.right)

  def visit_Constant(self, node : ast.Constant):
    self.buffer.write(node.value)

  def visit_Assign(self, node : ast.Assign):
    if len(node.targets) > 2:
      raise("Mutiple target assigns not allowed!")
    target = node.targets[0]
    self.visit(target)
    self.visit(node.value)

  def visit_AnnAssign(self, node : ast.AnnAssign):
    cpp_type = self.type_lookup(node.annotation.id) 
    self.buffer.write(cpp_type)
    self.visit(node.target)
    self.visit(node.value)

  def visit_Name(self, node : ast.Name):
    self.buffer.write(node.id)

  def visit_Mult(self, node : ast.Mult):
    self.buffer.writeln("\tmul")

  def visit_For(self, node : ast.For):
    pass

  def visit_While(self, node : ast.For):
    pass

  def visit_If():
    pass

  def visit_Expr():
    pass

  def BoolOp(self, node : ast.BoolOp):
    pass

  def BinOp(self, node : ast.BinOp):
    pass

  def UnaryOp(self, node : ast.UnaryOp):
    pass

  def Call(self, node : ast.Call):
    pass

  def Constant(self, node : ast.Constant):
    pass

  def Attribute(self, node : ast.Attribute):
    pass

  def Name(self, node : ast.Name):
    pass
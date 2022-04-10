import ast
from .scope import Scope

class LocalsCounter(ast.NodeVisitor):
  def __init__(self, func : ast.FunctionDef, scope : Scope):
    self._names = []
    self._scope = scope

    # Count the arguments
    for arg in func.args.args:
      self._names.append(arg.arg)

    # Visit the function body
    for statement in func.body:
      self.visit(statement)

  def visit_Assign(self, node : ast.Assign):
    # Check if single target
    if len(node.targets) != 1:
      raise RuntimeError("Only single assignment allowed.")

    # Visit the target
    self.visit(node.targets[0])

  def visit_Name(self, node : ast.Name):
    if isinstance(node.ctx, ast.Store):
      # Count up the new variables introduced
      accounted_for = node.id in self._names
      in_scope = self._scope.in_scope(node.id)
      if not accounted_for and not in_scope:
        self._names.append(node.id)

  def count(self):
    return len(self._names)
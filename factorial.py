def factorial(n):
  if n == 0:
    return 1
  return n * factorial(n-1)

def main():
  a = factorial(3 + 4) * 123
  print(a)
  return 0

main()
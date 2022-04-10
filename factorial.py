def factorial(n):
  if n == 0:
    return 1
  return n * factorial(n-1)

def main():
  i = 0
  while i < 10:
    a = factorial(3 + 4) * 123
    print(a)
    i = i + 1
  return 0

main()

# def main():
#   a = 1
#   b = 2
#   c = 3
#   d = 4
#   e = 5
#   f = 6
#   g = 7
#   h = 8
#   i = 9
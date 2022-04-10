def factorial(n):
  if n == 0:
    return 1
  return n * factorial(n-1)

def main():
  i = 0
  sum = 0
  while i < 10:
    a = factorial(3 + 4) * 123
    sum = sum + a
    print(sum)
    i = i + 1
  return 0

main()
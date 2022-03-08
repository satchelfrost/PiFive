def square(x : int) -> int:
    return x * x

def cube (x : int) -> int:
    return x * square(x)

def main():
    a = cube(3)
    print(a)
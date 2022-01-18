#include <stdint.h>
#include <stdio.h>

int64_t square(int64_t x)
{
    return x * x;
}

int64_t cube(int64_t x)
{
    return x * square(x);
}

int main()
{
    int64_t a = cube(3);
    printf("%d\n",a);
}

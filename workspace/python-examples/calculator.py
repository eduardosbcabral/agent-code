# Calculator with intentional bugs for testing
def add(a, b)
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b)
    if b == 0:
        return "Error: Division by zero!"
    return a / b

def power(a, b):
    return a ** b

# Missing main function
if __name__ == "__main__":
    print("Calculator Demo")
    print("5 + 3 =", add(5, 3))
    print("10 - 4 =", subtract(10, 4))
    print("6 * 7 =", multiply(6, 7))
    print("15 / 3 =", divide(15, 3))
    print("2 ^ 8 =", power(2, 8))
    print("10 / 0 =", divide(10, 0))

import random
import sys


def digit_range(digits):
    if digits < 1:
        raise ValueError("digit counts must be positive")
    return 10 ** (digits - 1), (10 ** digits) - 1


def read_inputs():
    values = sys.argv[1:4] if len(sys.argv) >= 4 else sys.stdin.read().split()
    if len(values) < 3:
        raise ValueError("expected three integers: a b n")
    return (int(values[0]), int(values[1]), int(values[2]))


def make_questions(divisor_digits, dividend_digits, count):
    divisor_min, divisor_max = digit_range(divisor_digits)
    dividend_min, dividend_max = digit_range(dividend_digits)
    if divisor_min > dividend_max:
        raise ValueError("divisor digit count cannot exceed dividend digit count")
    if count < 0:
        raise ValueError("question count cannot be negative")

    randint = random.randint
    questions = []
    for _ in range(count):
        divisor = randint(divisor_min, divisor_max)
        quotient_min = (dividend_min + divisor - 1) // divisor
        quotient_max = dividend_max // divisor
        quotient = randint(quotient_min, quotient_max)
        questions.append(f"{divisor * quotient} / {divisor} = ")
    return questions


def main():
    try:
        a, b, n = read_inputs()
        sys.stdout.write("\n".join(make_questions(a, b, n)))
    except ValueError as exc:
        raise SystemExit(str(exc))


if __name__ == "__main__":
    main()

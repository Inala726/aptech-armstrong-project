def is_armstrong(number: int) -> bool:
    """Check if a single number is an Armstrong number."""
    digits = str(number)
    power = len(digits)
    total = sum(int(d) ** power for d in digits)
    return total == number


def find_armstrong_in_range(min_val: int, max_val: int) -> list:
    """Return all Armstrong numbers between min_val and max_val inclusive."""
    if min_val > max_val or min_val < 0:
        return []
    return [n for n in range(min_val, max_val + 1) if is_armstrong(n)]
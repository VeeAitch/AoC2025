"""
Puzzle 03 - Exercise 01
"""


def read_battery_banks(filename):
    """
    Read battery banks from file.
    Each line corresponds to a single bank of batteries.
    """
    with open(filename, 'r') as f:
        return [line.strip() for line in f.readlines()]


def process_battery_bank(bank):
    """
    Process a single battery bank and return an integer value.
    
    Args:
        bank: String representing a battery bank
        
    Returns:
        Integer value from processing the battery bank
    """
    print(f"\nProcessing bank: {bank}")
    
    # First Digit: Choose highest number for string (len-1)
    first_digit = max(bank[:-1])
    print(f"  First digit (max of string excluding last char): {first_digit}")
    
    # Second Digit: Choose highest number for string (first digit till end)
    first_pos = bank.index(first_digit)
    print(f"  Position of first digit: {first_pos}")
    print(f"  Substring after first digit: {bank[first_pos+1:]}")
    second_digit = max(bank[first_pos+1:])
    print(f"  Second digit (max from position {first_pos+1} to end): {second_digit}")
    
    # create value with first and second digit
    value = int(first_digit + second_digit)
    print(f"  Combined value: {value}")
    
    # return value
    return value


def solve():
    # Read battery banks from test file
    # battery_banks = read_battery_banks('test.txt')
    battery_banks = read_battery_banks('input.txt')
    
    # Process each battery bank and calculate total sum
    total = 0
    for bank in battery_banks:
        value = process_battery_bank(bank)
        total += value
    
    # Output the result
    print(f"Total sum: {total}")


if __name__ == "__main__":
    solve()

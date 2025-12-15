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
    
    Selects 12 digits from the bank to form the maximum possible number.
    
    Args:
        bank: String representing a battery bank
        
    Returns:
        Integer value - the maximum 12-digit number from the bank
    """
    print(f"\nProcessing bank: {bank}")
    
    target_length = 12
    n = len(bank)
    result = []
    start = 0
    
    # For each of the 12 positions in our result
    for i in range(target_length):
        # Calculate how many digits we still need to select
        remaining_needed = target_length - i
        
        # Calculate the furthest position we can look at
        # while still having enough digits left to complete our selection
        end = n - remaining_needed + 1
        
        # Find the maximum digit in the valid range
        substring = bank[start:end]
        max_digit = max(substring)
        
        print(f"  Step {i+1}: Looking at {substring} (positions {start} to {end-1}), max={max_digit}")
        
        # Find where this max digit is and move our start position after it
        max_pos = bank.index(max_digit, start)
        result.append(max_digit)
        start = max_pos + 1
    
    # Create the final 12-digit number
    final_number = ''.join(result)
    value = int(final_number)
    print(f"  Final 12-digit number: {final_number} = {value}")
    
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

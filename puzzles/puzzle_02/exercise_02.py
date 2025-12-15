"""
Puzzle 02 - Exercise 01
"""


def load_id_ranges(filename):
    """Load id-ranges from a file.
    
    File format: comma-separated ranges, each range is first-last
    Example: 1-5, 10-15, 20-25
    """
    ranges = []
    
    with open(filename, 'r') as f:
        content = f.read().strip()
    
    # Split by comma to get individual ranges
    range_strings = content.split(',')
    
    for range_str in range_strings:
        range_str = range_str.strip()
        # Split by dash to get first and last
        parts = range_str.split('-')
        first = int(parts[0])
        last = int(parts[1])
        ranges.append((first, last))
    
    return ranges


def is_invalid_id(id_num):
    """Check if an ID is invalid.
    
    An ID is invalid if it's made of a sequence of digits repeated at least twice.
    Examples: 12341234 (1234 twice), 123123123 (123 three times), 1111111 (1 seven times)
    """
    id_str = str(id_num)
    length = len(id_str)
    
    # Try all possible pattern lengths
    for pattern_length in range(1, length // 2 + 1):
        # Check if the length is divisible by pattern length
        if length % pattern_length == 0:
            pattern = id_str[:pattern_length]
            repetitions = length // pattern_length
            
            # Check if the pattern repeated matches the full string
            if pattern * repetitions == id_str:
                return True
    
    return False



def find_invalid_ids(ranges):
    """Find all invalid IDs in the given ranges."""
    invalid = []
    
    for first, last in ranges:
        for id_num in range(first, last + 1):
            if is_invalid_id(id_num):
                invalid.append(id_num)
    
    return invalid


def solve():
    """Solve exercise 01"""
    ranges = load_id_ranges('input.txt')
    print("Loaded ranges:")
    for first, last in ranges:
        print(f"  {first}-{last}")
    
    invalid_ids = find_invalid_ids(ranges)
    total = sum(invalid_ids)
    
    print(f"\nInvalid IDs: {invalid_ids}")
    print(f"Total sum: {total}")


if __name__ == "__main__":
    solve()

"""
Puzzle 01 - Exercise 02
"""

from dataclasses import dataclass
from typing import List
from enum import Enum
from typing import Tuple



class Direction(Enum):
    LEFT = "L"
    RIGHT = "R"


@dataclass
class Vector:
    direction: Direction
    distance: int

    def __repr__(self) -> str:
        return f"Vector({self.direction.value}{self.distance})"


def read_input(filename: str) -> List[Vector]:
    vectors = []
    try:
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                
                direction_char = line[0]
                distance = int(line[1:])
                
                direction = Direction.LEFT if direction_char == "L" else Direction.RIGHT
                vectors.append(Vector(direction, distance))
        
        return vectors
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        return []
    except (ValueError, IndexError) as e:
        print(f"Error parsing input: {e}")
        return []

def dial(start: int, dial: Vector, solution) -> Tuple[int, int]:
    steps: int = dial.distance % 100
    print(F"--- Dialing ---")
    print(F"Vector to process: {dial}")
    print(f"Dialing from {start} {'right' if dial.direction == Direction.RIGHT else 'left'} by {steps} steps")  
    solution = solution + (dial.distance // 100)
    print(f"Adding for divisor: {(dial.distance // 100)}")

    if dial.direction == Direction.RIGHT:
        if (start + steps) > 99:
            if (start + steps) - 100 != 0 and start != 0:
                solution += 1
            return (start + steps) - 100, solution
        else:
            return (start + steps), solution
    else:
        if (start - steps) < 0:
            if 100 + (start - steps) != 0 and start != 0:
                solution += 1
            return 100 +(start - steps), solution
        else:
            return (start - steps), solution

def solve():
    input_file = "/home/hombu03/repos/AoC2025/puzzles/puzzle_01/input_01.txt"
    # input_file = "/home/hombu03/repos/AoC2025/puzzles/puzzle_01/test_01.txt"
    vectors = read_input(input_file)
    start_pos = 50 
    sol: int = 0

    print(f"Starting at position: {start_pos}")
    for vector in vectors:
        start_pos, sol = dial(start_pos, vector, sol)
        print(f"Moved {vector}, new position: {start_pos}")
        if start_pos == 0:
            sol += 1
        print(f"Current solution count: {sol}")
    print(f"Result: {sol}")
    

if __name__ == "__main__":
    solve()

# not: 6173, 7207
"""
Puzzle 01 - Exercise 01
"""

from dataclasses import dataclass
from typing import List
from enum import Enum




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

def dial(start: int, dial: Vector) -> int:
    steps: int = dial.distance % 100
    print(f"Dialing from {start} {'right' if dial.direction == Direction.RIGHT else 'left'} by {steps} steps")  
    

    if dial.direction == Direction.RIGHT:
        if (start + steps) > 99:
            return (start + steps) - 100
        else:
            return (start + steps)
    else:
        if (start - steps) < 0:
            return 100 + (start - steps)
        else:
            return (start - steps) 

def solve():
    input_file = "./input_01.txt"
    vectors = read_input(input_file)
    start_pos = 50 
    sol: int = 0

    print(f"Starting at position: {start_pos}")
    for vector in vectors:
        start_pos = dial(start_pos, vector)
        print(f"Moved {vector}, new position: {start_pos}")
        if start_pos == 0:
            sol += 1
        print(f"Current solution count: {sol}")
    print(f"Result: {sol}")
    
if __name__ == "__main__":
    solve()

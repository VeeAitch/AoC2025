"""
Puzzle 12 - Exercise 01

A attempt to decide whether a set of small shapes 
can be placed on a rectangular board without overlapping. Using Algorithm X 
(Knuth) with optimizations:
- MRV heuristic: pick constraint with fewest candidates
- Cell index: quickly find conflicting candidates
- Constraint index: avoid linear scans

Rotations and reflections are allowed.

But still too slow ...
"""


def read_shapes(file_path):
    """
    Read the shape definitions from the input file.
    Returns a dictionary where keys are shape numbers (0-5) and values are 3x3 matrices.
    """
    shapes = {}

    with open(file_path, "r") as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if line and line[-1] == ":" and line[0].isdigit():
            shape_num = int(line[:-1])
            shape_matrix = []

            for j in range(1, 4):
                if i + j < len(lines):
                    row = lines[i + j].rstrip("\n")
                    row = (row + "...")[:3]
                    shape_matrix.append(row)

            shapes[shape_num] = shape_matrix
            i += 4
        elif line and any(c.isdigit() for c in line) and "x" in line:
            break
        else:
            i += 1

    return shapes


def read_regions(file_path):
    """
    Read the region definitions from the input file.
    Returns a list of tuples: [(width, height, [count0, count1, ..., count5]), ...]
    """
    regions = []

    with open(file_path, "r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        line = line.strip()

        if "x" in line and ":" in line:
            parts = line.split(":")
            dimensions = parts[0].strip().split("x")
            width, height = int(dimensions[0]), int(dimensions[1])

            counts_str = parts[1].strip().split()
            counts = [int(c) for c in counts_str]

            regions.append((width, height, counts))

    return regions


def shape_to_coords(shape_matrix):
    """Convert a 3x3 shape matrix to a set of (row, col) coordinates."""
    coords = set()
    for r, row in enumerate(shape_matrix):
        for c, cell in enumerate(row):
            if cell == '#':
                coords.add((r, c))
    return coords


def rotate_coords_90(coords):
    """Rotate coordinates 90 degrees clockwise, then normalize."""
    rotated = {(c, -r) for r, c in coords}
    min_r = min(r for r, c in rotated)
    min_c = min(c for r, c in rotated)
    return {(r - min_r, c - min_c) for r, c in rotated}


def reflect_coords_horizontal(coords):
    """Mirror across a vertical axis, then normalize."""
    reflected = {(r, -c) for r, c in coords}
    min_r = min(r for r, c in reflected)
    min_c = min(c for r, c in reflected)
    return {(r - min_r, c - min_c) for r, c in reflected}


def get_all_orientations(shape_matrix):
    """Collect all distinct orientations (rotations and reflections)."""
    coords = shape_to_coords(shape_matrix)
    orientations = set()
    
    current = coords
    for _ in range(4):
        orientations.add(frozenset(current))
        current = rotate_coords_90(current)
    
    current = reflect_coords_horizontal(coords)
    for _ in range(4):
        orientations.add(frozenset(current))
        current = rotate_coords_90(current)
    
    return [set(ori) for ori in orientations]


def generate_placements(shape_coords, width, height):
    """Slide the shape across the board and keep those positions that fit."""
    placements = []
    
    for row_offset in range(height):
        for col_offset in range(width):
            translated = {(r + row_offset, c + col_offset) for r, c in shape_coords}
            
            if all(0 <= r < height and 0 <= c < width for r, c in translated):
                placements.append(translated)
    
    return placements


def build_exact_cover_problem(shapes, width, height, shape_counts):
    """Build the constraint system for exact cover."""
    
    candidates = []
    shape_constraints = set()
    max_placements_per_instance = 10000  # Hard limit per instance
    
    for shape_id, count in enumerate(shape_counts):
        if count == 0:
            continue
            
        shape_matrix = shapes[shape_id]
        orientations = get_all_orientations(shape_matrix)
        
        for instance_id in range(count):
            shape_constraints.add((shape_id, instance_id))
            placement_count = 0
            
            for orientation in orientations:
                placements = generate_placements(orientation, width, height)
                
                for placement in placements:
                    if placement_count < max_placements_per_instance:
                        candidates.append((shape_id, instance_id, placement))
                        placement_count += 1
                    else:
                        break
            if placement_count >= max_placements_per_instance:
                break
    return candidates, shape_constraints


def algorithm_x(candidates, shape_constraints, solution=None, depth=0, tracker=None, progress_cb=None, 
                constraint_index=None, cell_index=None, max_depth=80, timeout_secs=2, start_time=None):
    """
    Solve exact cover using Algorithm X with VERY aggressive limits:
    - Early infeasibility detection: backtrack if any constraint has 0 candidates
    - VERY STRICT depth limit (80) and timeout (2s) for fast rejection
    """
    import time
    
    # Track start time on first call
    if start_time is None:
        start_time = time.time()
    
    # Check timeout FIRST - most important for speed
    if time.time() - start_time > timeout_secs:
        return None
    
    # Very aggressive depth limit 
    if depth > max_depth:
        return None
    if solution is None:
        solution = []
    if tracker is None:
        tracker = {"nodes": 0, "solutions": 0, "total_instances": len(shape_constraints)}
    
    # Build indices on first call
    if constraint_index is None:
        constraint_index = {}
        for i, (shape_id, instance_id, placement) in enumerate(candidates):
            key = (shape_id, instance_id)
            if key not in constraint_index:
                constraint_index[key] = []
            constraint_index[key].append(i)
    
    if cell_index is None:
        cell_index = {}
        for i, (_, _, placement) in enumerate(candidates):
            for cell in placement:
                if cell not in cell_index:
                    cell_index[cell] = []
                cell_index[cell].append(i)
    
    # Base case: all shape instances placed
    if not shape_constraints:
        tracker["solutions"] += 1
        return solution
    
    # **OPTIMIZATION 1: Early feasibility check**
    # If any constraint has zero candidates, backtrack immediately
    for constraint in shape_constraints:
        if len(constraint_index.get(constraint, [])) == 0:
            return None
    
    # MRV heuristic: choose constraint with fewest candidates
    constraint = min(
        shape_constraints,
        key=lambda c: len(constraint_index.get(c, []))
    )
    
    valid_candidate_indices = constraint_index.get(constraint, [])
    
    # Try each candidate (placement) for this instance
    for cand_idx in valid_candidate_indices:
        candidate = candidates[cand_idx]
        shape_id, instance_id, placement = candidate
        tracker["nodes"] += 1
        
        # Single-line progress update
        if progress_cb and tracker["nodes"] % 1000 == 0:
            placed = len(solution)
            total = tracker.get("total_instances", placed)
            pct = int(100 * placed / total) if total else 100
            progress_cb(pct, placed, total, tracker["nodes"], tracker["solutions"])
        
        # Choose this candidate
        new_solution = solution + [candidate]
        new_shape_constraints = shape_constraints - {(shape_id, instance_id)}
        
        # **OPTIMIZATION 2: Efficient filtering**
        # Find conflicting indices via cell index
        conflicting_indices = set([cand_idx])
        for cell in placement:
            conflicting_indices.update(cell_index.get(cell, []))
        
        # **OPTIMIZATION 3: Incremental index updates (only create new maps)**
        new_constraint_index = {}
        new_cell_index = {}
        
        # Only iterate through non-conflicting candidates
        for i in range(len(candidates)):
            if i in conflicting_indices:
                continue
                
            cand = candidates[i]
            cand_shape_id, cand_instance_id, cand_placement = cand
            
            # Skip if constraint is already satisfied
            if (cand_shape_id, cand_instance_id) not in new_shape_constraints:
                continue
            
            # Add to constraint index
            key = (cand_shape_id, cand_instance_id)
            if key not in new_constraint_index:
                new_constraint_index[key] = []
            new_constraint_index[key].append(i)
            
            # Add to cell index
            for cell in cand_placement:
                if cell not in new_cell_index:
                    new_cell_index[cell] = []
                new_cell_index[cell].append(i)
        
        # Recurse (pass candidates through, along with updated indices)
        result = algorithm_x(candidates, new_shape_constraints, new_solution, depth + 1, tracker, progress_cb,
                           new_constraint_index, new_cell_index, max_depth, timeout_secs, start_time)
        
        if result is not None:
            return result
    
    return None


def visualize_solution(width, height, solution):
    """Create a visual representation of the solution."""
    grid = [['.' for _ in range(width)] for _ in range(height)]
    
    for shape_id, instance_id, placement in solution:
        for r, c in placement:
            grid[r][c] = str(shape_id)
    
    print("  Solution visualization:")
    print("    +" + "-" * width + "+")
    for row in grid:
        print("    |" + "".join(row) + "|")
    print("    +" + "-" * width + "+")


# --- DLX (Dancing Links) exact cover solver ---
class DLXNode:
    __slots__ = ("L", "R", "U", "D", "C", "row")
    def __init__(self):
        self.L = self
        self.R = self
        self.U = self
        self.D = self
        self.C = None  # column header
        self.row = None  # optional row identifier

class DLXColumn(DLXNode):
    __slots__ = ("name", "size")
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.size = 0  # number of nodes in this column

class DLX:
    def __init__(self, column_names):
        # Create header and column list in a circular doubly linked list
        self.header = DLXNode()
        self.columns = {}
        last = self.header
        for name in column_names:
            col = DLXColumn(name)
            self.columns[name] = col
            # insert to the right of last
            col.R = last.R
            col.L = last
            last.R.L = col
            last.R = col
            last = col
        self.solution = []

    def add_row(self, row_id, col_names):
        first = None
        # Create nodes for this row under each column
        for cname in col_names:
            col = self.columns[cname]
            node = DLXNode()
            node.C = col
            node.row = row_id
            # insert into column at bottom
            node.D = col
            node.U = col.U
            col.U.D = node
            col.U = node
            col.size += 1
            # link horizontally
            if first is None:
                first = node
                node.R = node
                node.L = node
            else:
                node.R = first
                node.L = first.L
                first.L.R = node
                first.L = node

    def cover(self, col):
        col.R.L = col.L
        col.L.R = col.R
        i = col.D
        while i is not col:
            j = i.R
            while j is not i:
                j.D.U = j.U
                j.U.D = j.D
                j.C.size -= 1
                j = j.R
            i = i.D

    def uncover(self, col):
        i = col.U
        while i is not col:
            j = i.L
            while j is not i:
                j.C.size += 1
                j.D.U = j
                j.U.D = j
                j = j.L
            i = i.U
        col.R.L = col
        col.L.R = col

    def search(self, k=0, max_solutions=1):
        # If no columns remain, solution found
        if self.header.R is self.header:
            return [list(self.solution)]
        # Choose column with minimum size (MRV)
        c = self.header.R
        min_col = c
        while c is not self.header:
            if c.size < min_col.size:
                min_col = c
            c = c.R
        self.cover(min_col)
        r = min_col.D
        solutions = []
        while r is not min_col:
            self.solution.append(r)
            j = r.R
            while j is not r:
                self.cover(j.C)
                j = j.R
            sols = self.search(k+1, max_solutions)
            if sols:
                solutions.extend(sols)
                if len(solutions) >= max_solutions:
                    # Early stop, still backtrack properly
                    j = r.L
                    while j is not r:
                        self.uncover(j.C)
                        j = j.L
                    self.solution.pop()
                    break
            j = r.L
            while j is not r:
                self.uncover(j.C)
                j = j.L
            self.solution.pop()
            r = r.D
        self.uncover(min_col)
        return solutions


def solve_with_dlx(shapes, width, height, counts, require_full_cover=False):
    # Columns: all shape instances (must be used exactly once)
    # Optionally also include every cell (require_full_cover) to force tiling.
    instance_cols = [(sid, iid) for sid, cnt in enumerate(counts) for iid in range(cnt)]
    cell_cols = [(r, c) for r in range(height) for c in range(width)] if require_full_cover else []
    # Column names must be unique and hashable; use tuples
    column_names = [("S", sid, iid) for (sid, iid) in instance_cols] + [("C", r, c) for (r, c) in cell_cols]
    dlx = DLX(column_names)
    # Precompute orientations and placements
    orient_cache = {}
    for sid, shape_matrix in shapes.items():
        orient_cache[sid] = get_all_orientations(shape_matrix)
    # Add rows: each feasible placement of a specific instance covers its instance column and all cells it occupies
    for sid, cnt in enumerate(counts):
        for iid in range(cnt):
            for orient in orient_cache[sid]:
                for placement in generate_placements(orient, width, height):
                    cols = [("S", sid, iid)]
                    if require_full_cover:
                        cols += [("C", r, c) for (r, c) in placement]
                    dlx.add_row((sid, iid, placement), cols)
    # Run DLX search for one solution
    sols = dlx.search(max_solutions=1)
    if not sols:
        return None
    # Convert nodes back to solution triples
    nodes = sols[0]
    solution = []
    for node in nodes:
        rid = node.row
        solution.append(rid)
    return solution


def classify_region(shapes, width, height, counts):
    """
    Classify region into three categories:
    1. EASY_YES: Obviously solvable (conservative space check with 3x3 per shape)
    2. EASY_NO: Obviously impossible (too many # cells to fit)
    3. NEEDS_DLX: Requires actual solving
    """
    area = width * height
    
    # Count total # cells needed
    total_cells_needed = 0
    for shape_id, count in enumerate(counts):
        if count > 0:
            shape_matrix = shapes[shape_id]
            cells_per_shape = sum(row.count('#') for row in shape_matrix)
            total_cells_needed += cells_per_shape * count
    
    # EASY_NO: More cells needed than available area
    if total_cells_needed > area:
        return "EASY_NO"
    
    # Conservative check: assume each shape needs full 3x3 grid
    total_shapes = sum(counts)
    conservative_area_needed = total_shapes * 9  # 3x3 per shape
    
    # EASY_YES: Even with conservative 3x3 per shape, everything fits
    if conservative_area_needed <= area:
        return "EASY_YES"
    
    # NEEDS_DLX: Not obviously yes or no
    return "NEEDS_DLX"


def solve():
    file_path = "./input_12.txt"
    # file_path = "./test_12.txt"

    shapes = read_shapes(file_path)
    regions = read_regions(file_path)

    print("=" * 60)
    print("SHAPE FITTING PUZZLE SOLVER")
    print("=" * 60)
    
    print("\nShapes loaded:")
    for shape_num, matrix in shapes.items():
        cells = sum(r.count('#') for r in matrix)
        w = max(len(r) for r in matrix)
        print(f"  Shape {shape_num} ({cells} cells):")
        print("    +" + "-" * w + "+")
        for row in matrix:
            print("    |" + row + "|")
        print("    +" + "-" * w + "+")

    print("\n" + "=" * 60)
    print(f"Processing {len(regions)} region(s)...")
    print("=" * 60)
    
    # First pass: classify all regions
    print("\n[PHASE 1] Classifying regions...")
    easy_yes = []
    easy_no = []
    needs_dlx = []
    
    for idx, (width, height, counts) in enumerate(regions):
        classification = classify_region(shapes, width, height, counts)
        if classification == "EASY_YES":
            easy_yes.append(idx)
        elif classification == "EASY_NO":
            easy_no.append(idx)
        else:
            needs_dlx.append(idx)
    
    print(f"  ✓ EASY_YES (obviously solvable): {len(easy_yes)} regions")
    print(f"  ✗ EASY_NO (obviously impossible): {len(easy_no)} regions")
    print(f"  ? NEEDS_DLX (requires solving): {len(needs_dlx)} regions")
    
    # Second pass: solve NEEDS_DLX regions
    print(f"\n[PHASE 2] Solving {len(needs_dlx)} regions with DLX...")
    
    solved_count = len(easy_yes)  # Start with easy yeses
    total_time = 0
    dlx_solved = 0

    for region_idx in needs_dlx:
        width, height, counts = regions[region_idx]
        print(f"Region {region_idx + 1}/{len(regions)}: {width}x{height}, {sum(counts)} shapes", end=" ... ", flush=True)
        
        import time
        start = time.time()
        solution = solve_with_dlx(shapes, width, height, counts, require_full_cover=False)
        elapsed = time.time() - start
        total_time += elapsed
        
        if solution:
            print(f"✓ {elapsed:.2f}s")
            solved_count += 1
            dlx_solved += 1
        else:
            print(f"✗ {elapsed:.2f}s")

    print("\n" + "=" * 60)
    print("FINAL RESULTS:")
    print(f"  Easy YES (conservative fit): {len(easy_yes)}")
    print(f"  Easy NO (too many cells): {len(easy_no)}")
    print(f"  DLX solved: {dlx_solved} / {len(needs_dlx)}")
    print(f"  DLX failed: {len(needs_dlx) - dlx_solved}")
    print(f"---")
    print(f"Total solvable regions: {solved_count} / {len(regions)}")
    if len(needs_dlx) > 0:
        print(f"DLX time: {total_time:.2f}s (avg {total_time/len(needs_dlx):.2f}s per region)")
    print("=" * 60)


if __name__ == "__main__":
    solve()

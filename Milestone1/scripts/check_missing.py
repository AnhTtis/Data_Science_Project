import os
import re

PATTERN = re.compile(r"^(\d{4})-(\d{5})$")  # e.g. 2303-07856

def collect_ids(base_dir: str):
    ids = []
    for entry in os.scandir(base_dir):
        if entry.is_dir():
            m = PATTERN.match(entry.name)
            if m:
                yymm = m.group(1)    # e.g., "2303"
                tail = m.group(2)    # e.g., "07856"
                ids.append((entry.name, yymm, int(tail)))
    return sorted(ids, key=lambda x: (x[1], x[2]))  # sort by year-month, then tail

def format_for_get_missing(missing_tails):
    """Format missing tails for get_missing.py"""
    if not missing_tails:
        print("No missing papers found!")
        return
    
    print(f"\nMISSING IDs FOR get_missing.py")
    print("=" * 60)
    print("Copy this into get_missing.py:")
    print()
    
    # Format as string list for get_missing.py
    print("MISSING_TAILS = [")
    for i in range(0, len(missing_tails), 10):
        line_tails = missing_tails[i:i+10]
        formatted_tails = ','.join(f'"{tail:05d}"' for tail in line_tails)
        print(f'{formatted_tails},')
    print("]")
    print('MISSING_YM = "2303" # Change this if needed')
    print()
    
    print(f"Total missing: {len(missing_tails)} papers")
    print(f"First few: {[f'2303.{t:05d}' for t in missing_tails[:5]]}")

def check_sequence(base_dir: str):
    ids = collect_ids(base_dir)
    if not ids:
        print("No matching folders.")
        return

    print(f"Found {len(ids)} folders in format YYMM-NNNNN")
    
    # Group by year-month
    grouped = {}
    for name, yymm, tail in ids:
        if yymm not in grouped:
            grouped[yymm] = []
        grouped[yymm].append(tail)
    
    print(f"Found data for months: {list(grouped.keys())}")
    
    all_missing = []
    
    for yymm in sorted(grouped.keys()):
        tails = sorted(grouped[yymm])
        print(f"\n{yymm}:")
        print(f"Range: {min(tails):05d} to {max(tails):05d}")
        print(f"Count: {len(tails)}")
        
        # Find missing in this range
        expected_range = set(range(min(tails), max(tails) + 1))
        present_set = set(tails)
        missing = sorted(expected_range - present_set)
        
        if missing:
            print(f"Missing in {yymm}: {len(missing)} papers")
            if len(missing) <= 20:
                print(f"{[f'{m:05d}' for m in missing]}")
            else:
                print(f"First 20: {[f'{m:05d}' for m in missing[:20]]}")
                print(f"... and {len(missing) - 20} more")
            all_missing.extend(missing)
        else:
            print(f"No missing papers in {yymm}")
    
    # Format for get_missing.py (assuming 2303 is the main target)
    if all_missing and "2303" in grouped:
        march_tails = sorted(grouped["2303"])
        march_range = set(range(min(march_tails), max(march_tails) + 1))
        march_missing = sorted(march_range - set(march_tails))
        
        if march_missing:
            format_for_get_missing(march_missing)

if __name__ == "__main__":
    # Use macOS path
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "23127130"))
    print(f"Checking directory: {BASE_DIR}")
    
    if not os.path.exists(BASE_DIR):
        print(f"Directory does not exist: {BASE_DIR}")
    else:
        check_sequence(BASE_DIR)
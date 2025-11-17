#!/usr/bin/env python3
"""
Script to perform additional cleanup on assignment1-report.ipynb
- Remove Section 1.4 (duplicate summary)
- Remove Section 3.3 (COSC2999 only)
"""

import json
import sys

def clean_notebook_v2(input_path, output_path):
    """Clean the notebook by removing unnecessary sections."""

    # Load notebook
    with open(input_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    cells = nb['cells']
    cells_to_delete = []
    modifications = []

    # Track if we're in a section to delete
    in_section_14 = False
    in_section_33 = False

    # Process each cell
    for idx, cell in enumerate(cells):
        cell_type = cell.get('cell_type', '')
        source = ''.join(cell.get('source', []))

        # Detect Section 1.4 start
        if '## 1.4 Summary of Data Changes' in source:
            in_section_14 = True
            cells_to_delete.append(idx)
            modifications.append(f"Cell {idx}: Marked for deletion (Section 1.4 - duplicate summary)")
            continue

        # Detect Section 1.4 end (when we hit section 2)
        if in_section_14 and ('# 2. Data Exploration' in source or '## 2.' in source):
            in_section_14 = False

        # Mark cells in Section 1.4 for deletion
        if in_section_14:
            cells_to_delete.append(idx)
            continue

        # Detect Section 3.3 start (can be ## or ###)
        if '3.3' in source and ('Hidden Data Quality' in source or 'COSC2999' in source):
            in_section_33 = True
            cells_to_delete.append(idx)
            modifications.append(f"Cell {idx}: Marked for deletion (Section 3.3 - COSC2999 only)")
            continue

        # Detect Section 3.3 end (when we hit section 4)
        if in_section_33 and ('# 4. External' in source or '## 4.' in source):
            in_section_33 = False

        # Mark cells in Section 3.3 for deletion
        if in_section_33:
            cells_to_delete.append(idx)
            continue

    # Delete cells in reverse order to maintain indices
    print(f"Found {len(cells_to_delete)} cells to delete")
    for idx in sorted(cells_to_delete, reverse=True):
        del cells[idx]

    # Save modified notebook
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)

    # Print modifications
    print("Notebook cleaned successfully!")
    print(f"\nModifications made:")
    for mod in modifications:
        print(f"  ✓ {mod}")
    print(f"\nTotal cells deleted: {len(cells_to_delete)}")
    print(f"Output saved to: {output_path}")

    return len(modifications)

if __name__ == '__main__':
    input_file = '/home/user/COSC2789-DS--ASM1/assignment1-report.ipynb'
    output_file = '/home/user/COSC2789-DS--ASM1/assignment1-report.ipynb'

    try:
        count = clean_notebook_v2(input_file, output_file)
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

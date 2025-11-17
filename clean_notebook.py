#!/usr/bin/env python3
"""
Script to clean up assignment1-report.ipynb by removing verbose outputs
and simplifying sections as per Task 5 requirements.
"""

import json
import sys

def clean_notebook(input_path, output_path):
    """Clean the notebook by modifying specific cells."""

    # Load notebook
    with open(input_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    cells = nb['cells']
    cells_to_delete = []

    # Track modifications
    modifications = []

    # Process each cell
    for idx, cell in enumerate(cells):
        cell_type = cell.get('cell_type', '')
        source = ''.join(cell.get('source', []))

        # 1. Cell 16: Simplify 1.3.3 sanity check output
        if idx == 16 and cell_type == 'code':
            # Check if this is the sanity check cell
            if 'sanity_check' in source or 'Valid range' in ''.join(cell.get('outputs', [{}])[0].get('text', [])):
                # Modify the code to simplify output
                old_source = source
                # Find and replace verbose print statements
                lines = source.split('\n')
                new_lines = []
                skip_verbose_prints = False

                for line in lines:
                    # Keep all code except verbose print statements
                    if 'print(f"Column' in line or 'print(f"  Valid range' in line or 'print(f"  Found' in line or 'print(f"  Converting' in line:
                        skip_verbose_prints = True
                        continue
                    elif 'print(f"Total columns' in line:
                        # Replace with simplified output
                        new_lines.append('        # Print simplified summary')
                        new_lines.append('        affected_cols = ", ".join(sanity_check_transformations.keys()) if sanity_check_transformations else "None"')
                        new_lines.append('        print(f"Sanity check completed: {len(sanity_check_transformations)} column(s) had invalid values converted to NaN")')
                        new_lines.append('        print(f"Columns affected: {affected_cols}")')
                        skip_verbose_prints = False
                    else:
                        new_lines.append(line)

                cell['source'] = '\n'.join(new_lines).split('\n')
                # Keep source as list
                cell['source'] = [line + '\n' if i < len(new_lines) - 1 else line
                                 for i, line in enumerate(new_lines)]
                modifications.append(f"Cell {idx}: Simplified sanity check output")

        # 2. Cell 20: Simplify 1.3.5 categorical typo output
        elif idx == 20 and cell_type == 'code':
            source_str = ''.join(cell.get('source', []))
            if 'expected_values' in source_str or 'Unexpected values found' in str(cell.get('outputs', [])):
                # Modify to simplify output
                lines = source_str.split('\n')
                new_lines = []

                for line in lines:
                    # Remove verbose print loops, keep transformation code
                    if 'print(f"  Column' in line or 'print(f"   Expected' in line or 'print(f"   Unexpected' in line or "print(f\"      - '" in line:
                        continue
                    elif 'for column, expected in expected_values.items():' in line:
                        # Replace the print loop with simplified version
                        new_lines.append('# Print simplified summary')
                        new_lines.append('typos_found = {col: len([v for v in df_cleaned[col].dropna().unique() if v not in exp]) ')
                        new_lines.append('               for col, exp in expected_values.items() if col in df_cleaned.columns')
                        new_lines.append('               and len([v for v in df_cleaned[col].dropna().unique() if v not in exp]) > 0}')
                        new_lines.append('')
                        new_lines.append('if typos_found:')
                        new_lines.append('    print(f"Categorical typos identified in {len(typos_found)} column(s): {\', \'.join(typos_found.keys())}")')
                        new_lines.append('    for col, count in typos_found.items():')
                        new_lines.append('        print(f"  - {col}: {count} unexpected value(s)")')
                        new_lines.append('else:')
                        new_lines.append('    print("No categorical typos found.")')
                        new_lines.append('')
                        # Skip the rest of the loop
                        break
                    else:
                        new_lines.append(line)

                # Find where transformation code starts (after the print loop)
                transformation_start = False
                for i, line in enumerate(lines):
                    if 'Transform typos in Mjob' in line or 'df_cleaned.loc[' in line:
                        transformation_start = True
                    if transformation_start:
                        new_lines.append(line)

                cell['source'] = [line + '\n' if i < len(new_lines) - 1 else line
                                 for i, line in enumerate(new_lines)]
                modifications.append(f"Cell {idx}: Simplified categorical typo output")

        # 3. Cell 83: Replace describe() output with brief text
        elif idx == 83 and cell_type == 'code':
            source_str = ''.join(cell.get('source', []))
            if '.describe()' in source_str and 'ratings' in source_str:
                # Replace describe() with summary
                new_source = source_str.replace(
                    'print(ratings.describe())',
                    '''print(f"\\nKey insights:")
print(f"  - Contains {len(ratings)} ratings from {ratings['user_id'].nunique()} users")
print(f"  - Ratings range from {ratings['rating'].min()} to {ratings['rating'].max()} (mean: {ratings['rating'].mean():.2f})")
print(f"  - Covers {ratings['item_id'].nunique()} unique movies")'''
                )
                cell['source'] = new_source.split('\n')
                cell['source'] = [line + '\n' if i < len(cell['source']) - 1 else line
                                 for i, line in enumerate(cell['source'])]
                modifications.append(f"Cell {idx}: Replaced describe() with brief text summary")

        # 4. Cell 79: Remove "4.6 " from heading
        elif idx == 79 and cell_type == 'markdown':
            source_str = ''.join(cell.get('source', []))
            if '## 4.6 Data Preparation Summary' in source_str:
                new_source = source_str.replace('## 4.6 Data Preparation Summary', '## Data Preparation Summary')
                cell['source'] = new_source.split('\n')
                cell['source'] = [line + '\n' if i < len(cell['source']) - 1 else line
                                 for i, line in enumerate(cell['source'])]
                modifications.append(f"Cell {idx}: Removed '4.6' from heading")

        # 5. Cell 91: Mark for deletion (duplicate References intro)
        elif idx == 91 and cell_type == 'markdown':
            source_str = ''.join(cell.get('source', []))
            if '# 5. References' in source_str and 'All sources referenced' in source_str:
                cells_to_delete.append(idx)
                modifications.append(f"Cell {idx}: Marked for deletion (duplicate References intro)")

        # 6. Cell 92: Fix References heading
        elif idx == 92 and cell_type == 'markdown':
            source_str = ''.join(cell.get('source', []))
            if '# 5. Reference' in source_str and 'Allison' in source_str:
                new_source = source_str.replace('# 5. Reference\n', '# 5. References\n')
                cell['source'] = new_source.split('\n')
                cell['source'] = [line + '\n' if i < len(cell['source']) - 1 else line
                                 for i, line in enumerate(cell['source'])]
                modifications.append(f"Cell {idx}: Changed 'Reference' to 'References'")

    # Delete cells in reverse order to maintain indices
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
    print(f"\nCells deleted: {len(cells_to_delete)}")
    print(f"Output saved to: {output_path}")

    return len(modifications)

if __name__ == '__main__':
    input_file = '/home/user/COSC2789-DS--ASM1/assignment1-report.ipynb'
    output_file = '/home/user/COSC2789-DS--ASM1/assignment1-report.ipynb'

    try:
        count = clean_notebook(input_file, output_file)
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

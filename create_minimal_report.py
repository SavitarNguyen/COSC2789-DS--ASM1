#!/usr/bin/env python3
"""
Create ultra-minimal report notebook - only final outputs, no verbose processing logs.
Based strictly on assignment Task 5 requirements.
"""

import json
import re

# Read original notebook
with open('assignment1.ipynb', 'r') as f:
    nb_orig = json.load(f)

# Create report notebook
nb_report = {
    "cells": [],
    "metadata": nb_orig.get("metadata", {}),
    "nbformat": 4,
    "nbformat_minor": 5
}

def suppress_verbose_output(source):
    """Remove excessive print statements but keep essential ones"""
    lines = source.split('\n')
    cleaned_lines = []

    skip_patterns = [
        'print("="',
        'print("─"',
        'print("✓"',
        'print("⚠️"',
        'print("\\n")',
        'print("")',
        'print(f"Shape:',
        'print(f"Memory:',
        'print(f"Columns:',
    ]

    for line in lines:
        # Skip purely decorative print statements
        if any(pattern in line for pattern in skip_patterns):
            continue
        # Skip verbose iteration prints
        if 'for' in line and 'print' in line:
            continue
        cleaned_lines.append(line)

    return '\n'.join(cleaned_lines)

print("Creating ultra-minimal report notebook...")
print("="*80)

# Cell selection rules - VERY STRICT
include_rules = {
    # Title and introduction
    0: ("Title", True),
    1: ("Imports", True),
    2: ("Section 1 header", True),
    3: ("Load data - suppress verbose", True),

    # Section 1: Only show final cleaning summary, not all steps
    24: ("Section 1.3.7 summary header", True),
    25: ("Final cleaning summary output", True),

    # Section 2: Data Exploration - only visualizations and explanations
    27: ("Section 2 header", True),
    # 2.1 - individual variables
    28: ("2.1 Nominal viz", True),
    29: ("2.1 Nominal explanation", True),
    30: ("2.1.2 header", True),
    31: ("2.1 Ordinal viz", True),
    32: ("2.1 Ordinal explanation", True),
    33: ("2.1.3 header", True),
    34: ("2.1 Numerical viz", True),
    35: ("2.1 Numerical explanation", True),
    # 2.2 - relationships
    36: ("2.2 header", True),
    37: ("2.2.1 Relationship 1 viz", True),
    38: ("2.2.1 discussion", True),
    39: ("2.2.2 header", True),
    40: ("2.2.2 Relationship 2 viz", True),
    41: ("2.2.2 discussion", True),
    42: ("2.2.3 header", True),
    43: ("2.2.3 Relationship 3 viz", True),
    44: ("2.2.3 discussion", True),
    # 2.3 - scatter matrix
    45: ("2.3 header", True),
    46: ("2.3 Scatter matrix viz", True),
    47: ("2.3 Analysis", True),

    # Section 3: Missing Values and Outliers
    48: ("Section 3 header", True),
    # Create a consolidated data cleaning cell instead of showing all steps
    49: ("Load data for Task 3", True),
    # 3.1 - imputation
    50: ("3.1.1 header", True),
    51: ("Generate student_fix1", True),
    52: ("3.1.1 explanation", True),
    53: ("3.1.2 header", True),
    54: ("Generate student_fix2", True),
    55: ("3.1.2 explanation", True),
    56: ("3.1.3 header", True),
    57: ("Imputation comparison viz", True),
    58: ("3.1.3 discussion", True),
    # 3.2 - outliers
    59: ("3.2 header", True),
    60: ("3.2 Q1 answer", True),
    62: ("3.2 Q2 answer", True),
    63: ("3.2 Q3 header", True),
    64: ("3.2 Q3 outlier detection", True),
    65: ("3.2 Q3 outlier viz", True),
    # 3.3 - hidden quality
    67: ("3.3 header", True),
    68: ("3.3.1 header", True),
    69: ("3.3.1 checks", True),
    70: ("3.3.2 header", True),
    71: ("3.3.2 checks", True),
    72: ("3.3.3 header", True),
    73: ("3.3.3 checks", True),
    74: ("3.3.4 summary", True),

    # Section 4: External Data
    75: ("Section 4 header", True),
    76: ("4.1 Download", True),
    77: ("4.2 header", True),
    78: ("4.2 Load ratings", True),
    79: ("4.3 header", True),
    80: ("4.3 Load movies", True),
    81: ("4.4 header", True),
    82: ("4.4 Merge", True),
    83: ("4.5 header", True),
    84: ("4.5 Quality assessment", True),
    85: ("4.5 Visualization", True),
    86: ("4.6 Summary", True),

    # Section 5: Conclusion
    87: ("Section 5 Conclusion and References", True),
}

# Build notebook with selected cells
for i in range(len(nb_orig['cells'])):
    if i in include_rules:
        tag, should_include = include_rules[i]
        if should_include:
            cell = nb_orig['cells'][i].copy()

            # For code cells with excessive output, clean them up
            if cell['cell_type'] == 'code':
                source = ''.join(cell['source'])

                # Suppress verbose output in data loading/processing cells
                if i in [3, 49, 76, 78, 80, 82, 84]:
                    # These cells can be streamlined
                    cleaned_source = suppress_verbose_output(source)
                    cell['source'] = [cleaned_source]

            nb_report['cells'].append(cell)
            print(f"✓ Cell {i:3d}: {tag}")

print("\n" + "="*80)
print(f"Original: {len(nb_orig['cells'])} cells")
print(f"Report:   {len(nb_report['cells'])} cells")
print(f"Reduction: {len(nb_orig['cells']) - len(nb_report['cells'])} cells "
      f"({(1 - len(nb_report['cells'])/len(nb_orig['cells']))*100:.1f}%)")

# Save
with open('assignment1_report.ipynb', 'w') as f:
    json.dump(nb_report, f, indent=1)

print("="*80)
print("✓ Ultra-minimal report notebook created: assignment1_report.ipynb")
print("="*80)
print("\nThis version includes ONLY:")
print("  ✓ Required markdown explanations")
print("  ✓ Essential visualizations")
print("  ✓ Final summary outputs")
print("  ✓ Minimal data processing output")
print("\nExcluded:")
print("  ✗ Verbose data cleaning logs")
print("  ✗ Intermediate exploration steps")
print("  ✗ Debug print statements")

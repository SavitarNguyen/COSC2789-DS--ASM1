#!/usr/bin/env python3
"""
Create a clean report notebook with only essential outputs required by assignment.

Assignment requirements (Task 5):
1. Data Preparation: Brief explanation + list of rows changed
2. Data Exploration: 3 variable plots + 3 relationship plots + scatter matrix
3. Missing Values: Imputation comparison + outlier analysis
4. External Data: Steps for retrieval and merging
5. Conclusion and References
"""

import json

# Read original notebook
with open('assignment1.ipynb', 'r') as f:
    nb_orig = json.load(f)

# Create new minimal report notebook
nb_report = {
    "cells": [],
    "metadata": nb_orig.get("metadata", {}),
    "nbformat": 4,
    "nbformat_minor": 5
}

def create_markdown(text):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [text] if isinstance(text, list) else [text]
    }

def create_code(source, outputs=None):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": outputs or [],
        "source": source if isinstance(source, list) else [source]
    }

# Strategy: Only include cells that produce FINAL outputs for the report
# Not intermediate exploration or debugging

print("Creating minimal report notebook...")
print("="*80)

cells_to_copy = []

for i, cell in enumerate(nb_orig['cells']):
    include = False
    tag = ""

    if cell['cell_type'] == 'markdown':
        content = ''.join(cell['source'])

        # Include all major section markdown
        if any(marker in content for marker in [
            '# Assignment', '# 1. Data', '# 2. Data', '# 3. Analysis',
            '# 4. External', '# 5. Conclusion',
            '## 1.1', '## 1.2', '## 1.3', '### 1.3.',
            '## 2.1', '## 2.2', '## 2.3',
            '## 3.1', '## 3.2', '## 3.3',
            '## 4.', '## 5.',
            'Rationale', 'Discussion:', 'Analysis of', '**Answer:**',
            'References'
        ]):
            include = True
            tag = "Report markdown"

        # Exclude very short subsection headers that are just titles
        if len(content.strip()) < 80 and '###' in content and not any(kw in content for kw in ['Rationale', 'Discussion', 'Analysis', 'Answer', 'Summary']):
            include = False
            tag = "Skip - minimal header"

    elif cell['cell_type'] == 'code':
        source = ''.join(cell['source'])

        # Essential: Library imports
        if i <= 3 and 'import' in source:
            include = True
            tag = "Imports"

        # Essential: Load main data
        elif 'pd.read_csv(\'student-data-25s3.csv\')' in source:
            include = True
            tag = "Load data"

        # Data Cleaning: Consolidate - only include if minimal output
        # Skip: verbose cleaning steps (cells 7-23)
        if i >= 7 and i <= 23:
            include = False
            tag = "Skip - verbose cleaning"

        # But DO include the cell that performs all cleaning
        if i == 14 or i == 16 or i == 21:  # Key transformation cells
            # Modify to suppress verbose output
            include = True
            tag = "Data cleaning (suppressed output)"

        # Essential: Section 1 final summary
        if i == 25 and 'DATA CLEANING SUMMARY' in source:
            include = True
            tag = "Section 1 summary"

        # Section 2: ALL visualization cells
        if 'plt.' in source or 'fig,' in source or 'sns.' in source:
            # Only if they're creating the REQUIRED visualizations
            if any(kw in source for kw in ['Mjob', 'Medu', 'G3', 'studytime', 'absences', 'scatter_matrix', 'G1', 'G2']):
                include = True
                tag = "Required visualization"

        # Section 3: Imputation
        if 'student_fix1.csv' in source or 'student_fix2.csv' in source:
            include = True
            tag = "Generate imputed file"

        # Section 3: Imputation comparison visualization
        if i >= 55 and i <= 60 and ('plt.' in source or 'fig,' in source):
            include = True
            tag = "Imputation comparison viz"

        # Section 3.2: Outlier detection visualization
        if i == 64 or i == 65:  # Outlier detection cells
            include = True
            tag = "Outlier detection"

        # Section 3.3: Hidden quality checks
        if i >= 69 and i <= 73:
            include = True
            tag = "Hidden quality checks"

        # Section 4: External data - only final operations
        if i >= 76:
            if 'urllib' in source or 'zipfile' in source:
                include = True
                tag = "Download MovieLens"
            elif 'pd.read_csv' in source and ('u.data' in source or 'u.item' in source):
                include = True
                tag = "Load external data"
            elif '.merge(' in source and 'ratings' in source:
                include = True
                tag = "Merge datasets"
            elif i in [82, 84, 85]:  # Quality assessment and viz
                include = True
                tag = "External data analysis"

    if include:
        cells_to_copy.append((i, tag, cell))

# Build the clean notebook
for idx, tag, cell in cells_to_copy:
    nb_report['cells'].append(cell)

print(f"Original cells: {len(nb_orig['cells'])}")
print(f"Report cells:   {len(nb_report['cells'])}")
print(f"Reduction:      {len(nb_orig['cells']) - len(nb_report['cells'])} cells ({(1 - len(nb_report['cells'])/len(nb_orig['cells']))*100:.1f}%)")

print("\n\nCells included:")
for idx, tag, _ in cells_to_copy:
    print(f"  Cell {idx:3d}: {tag}")

# Save the report notebook
with open('assignment1_report.ipynb', 'w') as f:
    json.dump(nb_report, f, indent=1)

print("\n" + "="*80)
print("✓ Minimal report notebook created: assignment1_report.ipynb")
print("="*80)

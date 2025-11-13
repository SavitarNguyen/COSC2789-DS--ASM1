# Code Snippets Reference - Parts 2 & 3

## Part 2: Data Exploration - Key Code Patterns

### Dynamic Study Time Labels (Cell 33)
```python
df['studytime'] = pd.to_numeric(df['studytime'], errors='coerce')
unique_studytime = sorted(df['studytime'].dropna().unique())

label_map = {
    1: '1 (<2hrs)',
    2: '2 (2-5hrs)',
    3: '3 (5-10hrs)',
    4: '4 (>10hrs)'
}
labels = [label_map.get(int(i), str(int(i))) for i in unique_studytime]

# Creates box plots with dynamic labels
bp = ax.boxplot(g3_by_studytime, labels=labels, patch_artist=True, widths=0.6)
```
**Why it works**: Gets actual values in data, only shows present categories

### Safe Missing Value Handling (Cell 30)
```python
g3_clean = df['G3'].dropna()
ax1.hist(g3_clean, bins=20, color='steelblue', alpha=0.7, edgecolor='black')
ax1.axvline(g3_clean.mean(), color='red', linestyle='--', linewidth=2)
```
**Pattern**: Drop NaN before analysis, don't change original df

### Correlation with Statistical Test (Cell 36)
```python
absences_clean = df[['absences', 'G3']].dropna()
corr, p_val = stats.pearsonr(absences_clean['absences'], absences_clean['G3'])

print(f"Pearson Correlation: r = {corr:.4f}, p-value = {p_val:.4f}")
if corr < 0:
    print("Negative correlation: More absences associated with lower grades")
```

### ANOVA Test for Group Differences (Cell 33)
```python
study_groups = [df[df['studytime'] == i]['G3'].dropna() for i in unique_studytime]
f_stat, p_value = stats.f_oneway(*study_groups)

print(f"ANOVA Test: F-statistic = {f_stat:.4f}, p-value = {p_value:.4f}")
if p_value < 0.05:
    print("Result: Significant difference in grades across study time groups")
else:
    print("Result: No significant difference in grades across study time groups")
```

### Scatter Matrix of Grade Progression (Cell 42)
```python
grade_cols = ['G1', 'G2', 'G3']
grade_data = df[grade_cols].dropna()

# Create scatter matrix
fig = pd.plotting.scatter_matrix(grade_data, figsize=(12, 12), alpha=0.6,
                                 diagonal='hist', color='steelblue')

# Visualize correlations
corr_matrix = grade_data.corr()
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
            square=True, linewidths=2)
```

---

## Part 3: Missing Values & Outliers - Key Code Patterns

### Defensive Data Source Selection (Cells 45, 48, 58, 59)
```python
# Pattern repeated throughout Part 3
try:
    df_mean = df_cleaned.copy()
    print("Using df_cleaned for mean imputation")
except NameError:
    df_mean = df.copy()
    print("df_cleaned not found, using df instead")
```
**Why**: Ensures code runs even if Part 1 was skipped, prints which was used

### Mean Imputation (Cell 45)
```python
numerical_cols = df_mean.select_dtypes(include=[np.number]).columns

for col in numerical_cols:
    if df_mean[col].isnull().any():
        mean_value = df_mean[col].mean()
        missing_count = df_mean[col].isnull().sum()
        df_mean[col].fillna(mean_value, inplace=True)
        print(f"\nColumn '{col}': Imputed {missing_count} missing values with mean = {mean_value:.2f}")

df_mean.to_csv('student_fix1.csv', index=False)
```

### Median Imputation (Cell 48)
```python
for col in numerical_cols:
    if df_median[col].isnull().any():
        median_value = df_median[col].median()
        missing_count = df_median[col].isnull().sum()
        df_median[col].fillna(median_value, inplace=True)
        print(f"\nColumn '{col}': Imputed {missing_count} missing values with median = {median_value:.2f}")

df_median.to_csv('student_fix2.csv', index=False)
```

### Comparison of Imputation Methods (Cell 51)
```python
# Compare original (with NaN removed) vs mean vs median
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Original (using df_cleaned)
try:
    g2_original = df_cleaned['G2'].dropna()
except NameError:
    g2_original = df['G2'].dropna()

axes[0].hist(g2_original, bins=15, color='lightblue', alpha=0.7)
axes[0].set_title('Original Data (Missing Values Removed)', fontsize=12, fontweight='bold')

# Mean imputation
axes[1].hist(df_mean['G2'], bins=15, color='lightcoral', alpha=0.7)
axes[1].set_title('After Mean Imputation', fontsize=12, fontweight='bold')

# Median imputation
axes[2].hist(df_median['G2'], bins=15, color='lightgreen', alpha=0.7)
axes[2].set_title('After Median Imputation', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.show()

# Statistical comparison table
print(f"{'Metric':<20} {'Original':<15} {'Mean Imputed':<15} {'Median Imputed':<15}")
print(f"{'Count':<20} {len(g2_original):<15} {len(df_mean['G2']):<15} {len(df_median['G2']):<15}")
print(f"{'Mean':<20} {g2_original.mean():<15.2f} {df_mean['G2'].mean():<15.2f} {df_median['G2'].mean():<15.2f}")
print(f"{'Std Dev':<20} {g2_original.std():<15.2f} {df_mean['G2'].std():<15.2f} {df_median['G2'].std():<15.2f}")
```

### Outlier Detection with IQR Method (Cell 58)
```python
def detect_outliers_iqr(data, column):
    """Detect outliers using the IQR method"""
    Q1 = data[column].quantile(0.25)
    Q3 = data[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = data[(data[column] < lower_bound) | (data[column] > upper_bound)][column]
    return outliers, lower_bound, upper_bound

# Usage
outliers_iqr, lower, upper = detect_outliers_iqr(data_to_analyze, 'G3')
print(f"IQR Method: {len(outliers_iqr)} outliers detected")
print(f"IQR Bounds: [{lower:.2f}, {upper:.2f}]")
```

### Outlier Detection with Z-Score Method (Cell 58)
```python
def detect_outliers_zscore(data, column, threshold=3):
    """Detect outliers using the Z-score method (default threshold=3)"""
    mean = data[column].mean()
    std = data[column].std()
    z_scores = np.abs((data[column] - mean) / std)
    outliers = data[z_scores > threshold][column]
    return outliers

# Usage
outliers_zscore = detect_outliers_zscore(data_to_analyze, 'G3', threshold=3)
print(f"Z-Score Method: {len(outliers_zscore)} outliers detected")
```

### Visualizing Outliers with Box Plots (Cell 59)
```python
fig, axes = plt.subplots(3, 3, figsize=(18, 15))
axes = axes.flatten()

numeric_cols = data_to_analyze.select_dtypes(include=[np.number]).columns.tolist()

for idx, col in enumerate(numeric_cols[:9]):
    if data_to_analyze[col].notna().sum() > 0:
        data_clean = data_to_analyze[col].dropna()
        
        # Box plot with outlier highlighting
        bp = axes[idx].boxplot(data_clean, vert=True, patch_artist=True, widths=0.5)
        bp['boxes'][0].set_facecolor('lightblue')
        bp['medians'][0].set_color('red')
        
        # Mark outliers in red
        for flier in bp['fliers']:
            flier.set_marker('o')
            flier.set_markerfacecolor('red')
            flier.set_markersize(8)
            flier.set_alpha(0.5)
        
        axes[idx].set_title(f'{col} - Outlier Detection', fontsize=11, fontweight='bold')
        axes[idx].grid(axis='y', alpha=0.3)

plt.suptitle('Outlier Detection Using Box Plots', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.show()
```

---

## Common Patterns & Best Practices Observed

### Pattern 1: Safe Type Conversion
```python
# GOOD: Handles conversion errors gracefully
df['studytime'] = pd.to_numeric(df['studytime'], errors='coerce')

# Result: Invalid values become NaN, doesn't crash
```

### Pattern 2: Conditional Operation Check
```python
# GOOD: Check before operating
if df_mean[col].isnull().any():
    mean_value = df_mean[col].mean()
    missing_count = df_mean[col].isnull().sum()
    # ... proceed with imputation
```

### Pattern 3: Multiple Output Formats
```python
# Good practice: Show both visual and tabular results
# Visualizations (histograms, plots)
# Statistics (printed tables)
# CSV exports (for further use)
```

### Pattern 4: Dynamic Label Generation with Fallback
```python
label_map = {1: '1 (<2hrs)', 2: '2 (2-5hrs)', ...}
labels = [label_map.get(int(i), str(int(i))) for i in unique_studytime]
# Falls back to string representation if key not in map
```

### Pattern 5: Statistical Testing with Interpretation
```python
f_stat, p_value = stats.f_oneway(*groups)
print(f"ANOVA Test: F-statistic = {f_stat:.4f}, p-value = {p_value:.4f}")
if p_value < 0.05:
    print("Result: Significant difference (p < 0.05)")
else:
    print("Result: No significant difference (p >= 0.05)")
```

---

## Key Variables Created

### Part 1
- `df`: Original data (from CSV)
- `df_original`: Backup of original
- `df_cleaned`: Cleaned data (Part 2 & 3 should use this)

### Part 2
- Local variables only (graph data, correlation arrays)
- No new persistent DataFrames

### Part 3
- `df_mean`: Data with mean imputation (saved to student_fix1.csv)
- `df_median`: Data with median imputation (saved to student_fix2.csv)

---

## Critical Execution Order

1. **Part 1 MUST complete** → Creates df and df_cleaned
2. **Cell 45** → Creates df_mean
3. **Cell 48** → Creates df_median
4. **Cell 51** → Must run after 45 & 48 (uses df_mean, df_median)
5. **Cells 58-59** → Can run independently (use df_cleaned with fallback)

If Cell 51 runs before Cell 45 or 48: **NameError** will occur

---

## Generated Output Files

```
student_fix1.csv
├─ Source: Cell 45 (Mean Imputation)
├─ Contains: All columns with NaN filled using column means
└─ Purpose: Alternative dataset for analysis

student_fix2.csv  
├─ Source: Cell 48 (Median Imputation)
├─ Contains: All columns with NaN filled using column medians
└─ Purpose: Alternative dataset for analysis
```


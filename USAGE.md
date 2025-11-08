# Usage Guide

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Prepare Your CSV

Ensure your CSV has:
- ZIP code column (named `Zip`, `ZIP`, or `zip`)
- FIPS code column (named `FIPS` or `fips`)
- Geographic hierarchy columns (`County`, `Chapter`, `Region`, `Division`)
- Data columns (years, totals, metrics)

### 3. Update Script Configuration

Edit `scripts/create_geojson_levels.py`:

```python
# Change these lines:
CSV_FILE = DATA_DIR / "your_data.csv"  # Your CSV file
```

Edit `scripts/create_zip_geojson.py`:

```python
# Change this line:
CSV_FILE = DATA_DIR / "your_data.csv"  # Your CSV file
```

### 4. Run Scripts

```bash
# Create all levels (counties, chapters, regions, divisions)
python3 scripts/create_geojson_levels.py

# Create ZIP code level
python3 scripts/create_zip_geojson.py
```

### 5. Upload to ArcGIS Online

1. Go to your ArcGIS Online portal
2. Content → Add Item → From my computer
3. Select GeoJSON files from `geojson_output/`
4. Upload and style as choropleth maps

## Customization

### Different Column Names

If your CSV uses different column names, update the scripts:

**In both scripts, find:**
```python
df['Zip'] = df['YourZipColumn'].astype(str)...
df['FIPS'] = df['YourFIPSColumn'].astype(str)...
```

**For aggregation, update:**
```python
county_agg = df.groupby('YourFIPSColumn').agg({...})
chapter_agg = df.groupby('YourChapterColumn').agg({...})
```

### Different Aggregation Methods

Modify the `agg()` calls:

```python
# Sum for years
**{col: 'sum' for col in year_cols}

# Mean for metrics
**{col: 'mean' for col in metric_cols}

# First for text
**{col: 'first' for col in text_cols}
```

### Filter to Specific Regions

Add filtering before processing:

```python
# Filter to specific states
df = df[df['State'].isin(['AL', 'FL', 'GA'])]

# Filter to specific regions
df = df[df['Region'] == 'Southeast Region']
```

### Adjust File Output Names

Change output filenames:

```python
county_file = OUTPUT_DIR / "your_counties.geojson"
chapter_file = OUTPUT_DIR / "your_chapters.geojson"
```

## Examples

### Example 1: Basic Usage

```bash
# 1. Place your CSV in the repo directory
cp /path/to/your/data.csv geojson-pipeline-repo/

# 2. Update CSV_FILE in scripts
# Edit scripts/create_geojson_levels.py line 21

# 3. Run
cd geojson-pipeline-repo
python3 scripts/create_geojson_levels.py
python3 scripts/create_zip_geojson.py

# 4. Find output
ls geojson_output/*.geojson
```

### Example 2: Custom Column Names

If your CSV has `ZIP_CODE` instead of `Zip`:

```python
# In both scripts, change:
df['Zip'] = df['ZIP_CODE'].astype(str).str.replace('.0', '', regex=False).str.zfill(5)
```

### Example 3: Process Only Specific States

```python
# Add after loading CSV:
df = df[df['State'].isin(['AL', 'FL', 'GA', 'MS'])]
```

### Example 4: Different Output Directory

```python
# Change OUTPUT_DIR:
OUTPUT_DIR = Path("/path/to/your/output")
OUTPUT_DIR.mkdir(exist_ok=True)
```

## Troubleshooting

### Script Fails to Download Boundaries

**Check internet connection**:
```bash
curl -I https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_county_500k.zip
```

**Try manual download**:
1. Download shapefile manually
2. Extract to `geojson_output/temp_counties/`
3. Update script to use local file

### Memory Errors

**Process in batches**:
```python
# Process by state
for state in df['State'].unique():
    state_df = df[df['State'] == state]
    # ... process state_df
```

**Increase simplification**:
```python
geometry.simplify(0.01, preserve_topology=True)  # More aggressive
```

### No Matches Found

**Check data format**:
```python
print(df['Zip'].head())
print(df['FIPS'].head())
# Should be 5-digit strings: '35004', '01115'
```

**Check for missing values**:
```python
print(df[df['Zip'].isna()])
print(df[df['FIPS'].isna()])
```

## Advanced Usage

### Use Custom Boundaries

If you have your own shapefiles:

```python
# Load custom boundaries
custom_gdf = gpd.read_file("path/to/your/boundaries.shp")
custom_gdf = custom_gdf.to_crs('EPSG:4326')

# Use instead of downloaded boundaries
counties_gdf = custom_gdf
```

### Add Custom Properties

Add additional properties to GeoJSON:

```python
# After merging, add custom columns
county_output['CustomField'] = county_output['SomeColumn'].apply(your_function)
```

### Export to Other Formats

Export to Shapefile instead of GeoJSON:

```python
county_output.to_file("counties.shp", driver='ESRI Shapefile')
```

Export to GeoPackage:

```python
county_output.to_file("counties.gpkg", driver='GPKG')
```

## Best Practices

1. **Backup your CSV** before processing
2. **Test with small subset** first (filter to one state)
3. **Check output** in QGIS or ArcGIS before uploading
4. **Document your changes** if customizing scripts
5. **Version control** your CSV and scripts

## Getting Help

1. Check `docs/PROCESS.md` for detailed process explanation
2. Check `docs/RESOURCES.md` for data sources and references
3. Review script comments for inline documentation
4. Test with sample data first


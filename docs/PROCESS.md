# Detailed Process Documentation

## Overview

This document explains the step-by-step process of creating multi-level GeoJSON files from CSV data.

## Input Requirements

### CSV File Structure

Your CSV must have:
1. **Geographic identifiers**:
   - ZIP code column (e.g., `Zip`, `ZIP`, `zip`)
   - FIPS code column (e.g., `FIPS`, `fips`)

2. **Hierarchy columns**:
   - County name (e.g., `County`)
   - Chapter name (e.g., `Chapter`)
   - Region name (e.g., `Region`)
   - Division name (e.g., `Division`)

3. **Data columns**:
   - Year columns (e.g., `2022`, `2023`, `2024`, `2025`)
   - Total columns (e.g., `Grand Total`, `County_Total_2022`)
   - Any other metrics or attributes

4. **Code columns** (optional but useful):
   - `ECODE` (Chapter code)
   - `RCODE` (Region code)
   - `DCODE` (Division code)

### Example CSV Row

```csv
Zip,FIPS,County,State,ECODE,Chapter,RCODE,Region,DCODE,Division,2022,2023,2024,2025,Grand Total
35004,01115,St. Clair,AL,1019.0,ARC serving Mid Alabama,01R04,Alabama and Mississippi Region,D25,Southeast and Caribbean Division,20.0,32.0,50.0,0.0,102.0
```

## Step-by-Step Process

### Phase 1: Data Preparation

#### Step 1.1: Load CSV
```python
df = pd.read_csv(CSV_FILE, dtype={'Zip': str, 'FIPS': str}, low_memory=False)
```
- Read CSV with pandas
- Specify ZIP and FIPS as strings to preserve leading zeros
- Use `low_memory=False` for better type inference

#### Step 1.2: Normalize Geographic Identifiers
```python
df['Zip'] = df['Zip'].astype(str).str.replace('.0', '', regex=False).str.zfill(5)
df['FIPS'] = df['FIPS'].astype(str).str.zfill(5)
```
- Convert to string
- Remove `.0` suffix (from Excel exports)
- Zero-pad to 5 digits (required for matching)

#### Step 1.3: Identify Column Types
```python
year_cols = [col for col in df.columns if col.isdigit()]
total_cols = [col for col in df.columns if 'Total' in col]
```
- Identify numeric columns for aggregation
- Separate year columns from total columns
- Years will be summed, totals may use 'first' (already aggregated)

### Phase 2: Download Boundaries

#### Step 2.1: Download County Boundaries
```python
counties_url = "https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_county_500k.zip"
response = requests.get(counties_url, timeout=30)
```
- Download ZIP file from Census Bureau
- Extract shapefile components
- Load with geopandas: `gpd.read_file()`

#### Step 2.2: Process County Boundaries
```python
counties_gdf = counties_gdf.to_crs('EPSG:4326')
counties_gdf['FIPS'] = counties_gdf['STATEFP'] + counties_gdf['COUNTYFP']
counties_gdf['geometry'] = counties_gdf['geometry'].simplify(0.001, preserve_topology=True)
```
- Convert to WGS84 (web standard)
- Create FIPS code from state + county FIPS
- Simplify geometry to reduce file size

#### Step 2.3: Download ZIP Boundaries (if needed)
```python
zip_urls = [
    "https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_us_zcta520_500k.zip",
    # ... fallback URLs
]
```
- Try multiple year URLs (Census URLs change)
- Extract and load shapefile
- Normalize ZIP code column name

### Phase 3: Create ZIP Level GeoJSON

#### Step 3.1: Join CSV to ZIP Boundaries
```python
zip_merged = zips_gdf.merge(
    df,
    left_on='ZIP_CODE',
    right_on='Zip',
    how='inner'
)
```
- Match CSV rows to ZIP boundaries
- `how='inner'` keeps only matched ZIPs
- Preserves all CSV columns

#### Step 3.2: Export ZIP GeoJSON
```python
zip_output = zip_merged[['geometry'] + [col for col in df.columns if col in zip_merged.columns]]
zip_geojson = zip_output.to_json()
```
- Keep geometry + all CSV columns
- Convert to GeoJSON format
- Save to file

### Phase 4: Create County Level GeoJSON

#### Step 4.1: Aggregate Data by County
```python
county_agg = df.groupby('FIPS').agg({
    **{col: 'first' for col in ['County', 'State', 'Chapter', 'Region', 'Division']},
    **{col: 'sum' for col in year_cols},
    **{col: 'first' for col in total_cols}
}).reset_index()
```
- Group CSV rows by FIPS code
- Sum year columns (aggregate ZIP data)
- Use 'first' for text columns and totals (already aggregated)

#### Step 4.2: Join to County Boundaries
```python
county_merged = counties_gdf.merge(
    county_agg,
    left_on='FIPS',
    right_on='FIPS',
    how='inner'
)
```
- Match aggregated data to county boundaries
- Preserves geometry from boundaries
- Adds aggregated data as properties

#### Step 4.3: Export County GeoJSON
```python
county_output = county_merged[['geometry'] + [col for col in county_agg.columns if col in county_merged.columns]]
```
- Select geometry + data columns
- Export to GeoJSON

### Phase 5: Create Chapter Level GeoJSON

#### Step 5.1: Aggregate Data by Chapter
```python
chapter_agg = df.groupby('Chapter').agg({
    **{col: 'first' for col in ['Region', 'Division', 'RCODE', 'DCODE']},
    **{col: 'sum' for col in year_cols},
    **{col: 'first' for col in [c for c in total_cols if 'Chapter' in c]}
}).reset_index()
```
- Group by Chapter name
- Sum year columns across counties
- Keep chapter/region/division totals

#### Step 5.2: Create Chapter Boundaries
```python
county_chapter_lookup = df[['FIPS', 'Chapter']].drop_duplicates()
counties_with_chapter = counties_gdf.merge(county_chapter_lookup, on='FIPS', how='inner')
chapter_gdf = counties_with_chapter.dissolve(by='Chapter', aggfunc='first')
```
- Join counties to get Chapter assignment
- Use `dissolve()` to merge county boundaries by Chapter
- Creates new geometry combining all counties in each chapter

#### Step 5.3: Join and Export
```python
chapter_merged = chapter_gdf.merge(chapter_agg, on='Chapter', how='inner')
```
- Match aggregated data to dissolved boundaries
- Export to GeoJSON

### Phase 6: Create Region Level GeoJSON

#### Step 6.1: Aggregate Data by Region
```python
region_agg = df.groupby('Region').agg({
    **{col: 'first' for col in ['Division', 'RCODE', 'DCODE']},
    **{col: 'sum' for col in year_cols},
    **{col: 'first' for col in [c for c in total_cols if 'Region' in c]}
}).reset_index()
```
- Group by Region name
- Sum year columns across chapters
- Keep region/division totals

#### Step 6.2: Create Region Boundaries
```python
region_lookup = df[['FIPS', 'Region']].drop_duplicates()
counties_with_region = counties_gdf.merge(region_lookup, on='FIPS', how='inner')
region_gdf = counties_with_region.dissolve(by='Region', aggfunc='first')
```
- Join counties to get Region assignment
- Dissolve counties by Region
- Creates combined geometry for each region

#### Step 6.3: Join and Export
```python
region_merged = region_gdf.merge(region_agg, on='Region', how='inner')
```
- Match aggregated data to dissolved boundaries
- Export to GeoJSON

### Phase 7: Create Division Level GeoJSON

#### Step 7.1: Aggregate Data by Division
```python
division_agg = df.groupby('Division').agg({
    **{col: 'first' for col in ['DCODE']},
    **{col: 'sum' for col in year_cols},
    **{col: 'first' for col in [c for c in total_cols if 'Division' in c]}
}).reset_index()
```
- Group by Division name
- Sum year columns across regions
- Keep division totals

#### Step 7.2: Create Division Boundaries
```python
division_lookup = df[['FIPS', 'Division']].drop_duplicates()
counties_with_division = counties_gdf.merge(division_lookup, on='FIPS', how='inner')
division_gdf = counties_with_division.dissolve(by='Division', aggfunc='first')
```
- Join counties to get Division assignment
- Dissolve counties by Division
- Creates combined geometry for each division

#### Step 7.3: Join and Export
```python
division_merged = division_gdf.merge(division_agg, on='Division', how='inner')
```
- Match aggregated data to dissolved boundaries
- Export to GeoJSON

## Key Operations Explained

### Dissolve Operation

**What it does**: Merges adjacent polygons into larger polygons based on a grouping field.

**Example**:
- Input: 5 counties, all in "Alabama Chapter"
- Operation: `dissolve(by='Chapter')`
- Output: 1 polygon covering all 5 counties

**Parameters**:
- `by`: Column name to group by
- `aggfunc`: How to aggregate attributes ('first', 'sum', 'mean', etc.)

### Merge Operation

**What it does**: Joins two dataframes on a common column.

**Types**:
- `how='inner'`: Keep only matching rows
- `how='left'`: Keep all left rows, add matching right data
- `how='outer'`: Keep all rows from both

**Example**:
- Left: County boundaries (geometry)
- Right: Aggregated data (no geometry)
- Result: Counties with data attached

### Simplify Operation

**What it does**: Reduces the number of vertices in geometry to make files smaller.

**Tolerance values**:
- `0.0001`: Very detailed (large files)
- `0.001`: Good detail (medium files) - used for counties
- `0.01`: Simplified (small files) - used for regions

**Trade-off**: Higher tolerance = smaller files but less detail

## Output Structure

### GeoJSON Format

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "Zip": "35004",
        "County": "St. Clair",
        "Chapter": "ARC serving Mid Alabama",
        "2022": 20.0,
        "2023": 32.0,
        ...
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[long, lat], ...]]
      }
    },
    ...
  ]
}
```

### File Organization

```
geojson_output/
├── biomed_zip_codes.geojson      (13,760 features, 150 MB)
├── biomed_counties.geojson       (2,129 features, 21 MB)
├── biomed_chapters.geojson       (191 features, 9.6 MB)
├── biomed_regions.geojson        (42 features, 6.9 MB)
└── biomed_divisions.geojson      (6 features, 6.2 MB)
```

## Common Issues and Solutions

### Issue: ZIP Codes Don't Match

**Cause**: Format mismatch (e.g., "3504" vs "03504")

**Solution**: Normalize with `str.zfill(5)`

### Issue: Missing Boundaries

**Cause**: ZIP/FIPS codes in CSV don't exist in boundary files

**Solution**: 
- Check for typos in CSV
- Verify codes are valid (some ZIPs are PO Box only, not ZCTA5)
- Use `how='left'` merge to keep CSV data even without boundaries

### Issue: Dissolve Creates Holes

**Cause**: Counties in same group are not adjacent

**Solution**: This is expected - dissolve creates multipolygons for non-contiguous areas

### Issue: File Too Large

**Cause**: Too much geometry detail

**Solution**: Increase simplification tolerance or filter to specific regions

## Performance Tips

1. **Process in batches**: If memory is limited, process by state/region
2. **Simplify early**: Simplify geometry right after loading boundaries
3. **Filter data**: Only process ZIPs/counties you need
4. **Use appropriate resolution**: 500k boundaries are fine for web mapping
5. **Cache downloads**: Save downloaded shapefiles to avoid re-downloading


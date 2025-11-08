#!/usr/bin/env python3
"""
Create GeoJSON files for Biomed data at multiple geographic levels:
- ZIP codes (most granular, all fields)
- Counties (aggregated from ZIPs, includes county/chapter/region/division data)
- Chapters (aggregated from counties, includes chapter/region/division data)
- Regions (aggregated from chapters, includes region/division data)
- Divisions (aggregated from regions, includes division data)
"""

import geopandas as gpd
import pandas as pd
import json
from pathlib import Path
import requests
from io import BytesIO
import zipfile

# Configuration
DATA_DIR = Path(__file__).parent
CSV_FILE = DATA_DIR / "Biomed by zip code_ENHANCED.csv"
CHAPTERS_SHP = DATA_DIR / "Biomed by zip code_with_redcross_by_chapter" / "chapters.shp"

OUTPUT_DIR = DATA_DIR / "geojson_output"
OUTPUT_DIR.mkdir(exist_ok=True)

print("=" * 70)
print("Creating GeoJSON files for Biomed data at multiple levels")
print("=" * 70)

# Step 1: Load CSV data
print("\n1. Loading CSV data...")
df = pd.read_csv(CSV_FILE, dtype={'Zip': str, 'FIPS': str}, low_memory=False)
df['Zip'] = df['Zip'].astype(str).str.replace('.0', '', regex=False).str.zfill(5)
df['FIPS'] = df['FIPS'].astype(str).str.zfill(5)

print(f"   ✓ Loaded {len(df):,} rows")
print(f"   ✓ Columns: {len(df.columns)}")

# Identify numeric columns (years and totals)
year_cols = [col for col in df.columns if col.isdigit()]
total_cols = [col for col in df.columns if 'Total' in col]
numeric_cols = year_cols + total_cols

# Step 2: Load chapter boundaries (if available)
print("\n2. Checking for chapter boundaries...")
chapters_gdf = None
if CHAPTERS_SHP.exists():
    try:
        temp_chapters = gpd.read_file(CHAPTERS_SHP)
        if len(temp_chapters) > 0:
            chapters_gdf = temp_chapters.to_crs('EPSG:4326')
            chapters_gdf['geometry'] = chapters_gdf['geometry'].simplify(0.001, preserve_topology=True)
            print(f"   ✓ Loaded {len(chapters_gdf)} chapters from shapefile")
        else:
            print("   ⚠ Chapter shapefile exists but is empty")
    except Exception as e:
        print(f"   ⚠ Error reading chapter shapefile: {e}")

if chapters_gdf is None:
    print("   ℹ Will create chapter boundaries by dissolving counties")

# Step 3: Download county boundaries from Census
print("\n3. Downloading county boundaries from Census...")
try:
    # Download US Counties shapefile
    counties_url = "https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_county_500k.zip"
    print(f"   Downloading from: {counties_url}")
    
    response = requests.get(counties_url, timeout=30)
    response.raise_for_status()
    
    with zipfile.ZipFile(BytesIO(response.content)) as z:
        z.extractall(OUTPUT_DIR / "temp_counties")
    
    counties_gdf = gpd.read_file(OUTPUT_DIR / "temp_counties" / "cb_2023_us_county_500k.shp")
    counties_gdf = counties_gdf.to_crs('EPSG:4326')
    counties_gdf['FIPS'] = counties_gdf['STATEFP'] + counties_gdf['COUNTYFP']
    counties_gdf['geometry'] = counties_gdf['geometry'].simplify(0.001, preserve_topology=True)
    
    print(f"   ✓ Loaded {len(counties_gdf)} counties")
except Exception as e:
    print(f"   ⚠ Error downloading counties: {e}")
    print("   Will create county GeoJSON from data only (no geometry)")
    counties_gdf = None

# Step 4: Download ZIP code boundaries from Census
print("\n4. Downloading ZIP code boundaries from Census...")
try:
    # Try multiple possible URLs for ZIP codes
    zip_urls = [
        "https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_zcta520_500k.zip",
        "https://www2.census.gov/geo/tiger/GENZ2022/shp/cb_2022_us_zcta520_500k.zip",
        "https://www2.census.gov/geo/tiger/GENZ2021/shp/cb_2021_us_zcta520_500k.zip"
    ]
    
    zips_gdf = None
    for zips_url in zip_urls:
        try:
            print(f"   Trying: {zips_url}")
            response = requests.get(zips_url, timeout=60)
            response.raise_for_status()
            
            with zipfile.ZipFile(BytesIO(response.content)) as z:
                z.extractall(OUTPUT_DIR / "temp_zips")
            
            # Find the shapefile name
            shp_files = [f for f in z.namelist() if f.endswith('.shp')]
            if shp_files:
                zips_gdf = gpd.read_file(OUTPUT_DIR / "temp_zips" / shp_files[0])
                zips_gdf = zips_gdf.to_crs('EPSG:4326')
                
                # Try different column names for ZIP code
                zip_col = None
                for col in ['ZCTA5CE20', 'ZCTA5CE10', 'ZCTA5', 'GEOID20', 'GEOID10', 'GEOID']:
                    if col in zips_gdf.columns:
                        zip_col = col
                        break
                
                if zip_col:
                    zips_gdf['ZIP_CODE'] = zips_gdf[zip_col].astype(str).str.zfill(5)
                else:
                    print(f"   ⚠ Could not find ZIP code column. Available: {list(zips_gdf.columns)}")
                    zips_gdf = None
                
                if zips_gdf is not None:
                    zips_gdf['geometry'] = zips_gdf['geometry'].simplify(0.0005, preserve_topology=True)
                    print(f"   ✓ Loaded {len(zips_gdf)} ZIP codes")
                    break
        except Exception as e:
            print(f"   ⚠ Failed: {e}")
            continue
    
    if zips_gdf is None:
        print("   ⚠ Could not download ZIP codes from any URL")
        print("   Will create ZIP GeoJSON from data only (no geometry)")
        
except Exception as e:
    print(f"   ⚠ Error downloading ZIP codes: {e}")
    print("   Will create ZIP GeoJSON from data only (no geometry)")
    zips_gdf = None

print("\n" + "=" * 70)
print("Creating GeoJSON files...")
print("=" * 70)

# ============================================================================
# LEVEL 1: ZIP CODES (most granular - all fields from CSV)
# ============================================================================
print("\n📦 Creating ZIP code GeoJSON...")
if zips_gdf is not None and 'ZIP_CODE' in zips_gdf.columns:
    # Join CSV data to ZIP boundaries
    zip_merged = zips_gdf.merge(
        df,
        left_on='ZIP_CODE',
        right_on='Zip',
        how='inner'
    )
    
    # Keep all columns from CSV
    zip_output = zip_merged[['geometry'] + [col for col in df.columns if col in zip_merged.columns]]
    
    zip_geojson = zip_output.to_json()
    zip_file = OUTPUT_DIR / "biomed_zip_codes.geojson"
    with open(zip_file, 'w') as f:
        json.dump(json.loads(zip_geojson), f, indent=2)
    
    print(f"   ✓ Created {zip_file}")
    print(f"   ✓ Features: {len(zip_output):,}")
else:
    print("   ⚠ Skipped (no ZIP boundaries available)")

# ============================================================================
# LEVEL 2: COUNTIES (aggregate ZIPs, include county/chapter/region/division)
# ============================================================================
print("\n🏛️  Creating County GeoJSON...")

# Aggregate data by county
county_agg = df.groupby('FIPS').agg({
    **{col: 'first' for col in ['County', 'State', 'Chapter', 'Region', 'Division', 
                                 'ECODE', 'RCODE', 'DCODE']},
    **{col: 'sum' for col in year_cols},
    **{col: 'first' for col in total_cols}  # Totals are already aggregated
}).reset_index()

if counties_gdf is not None:
    # Join aggregated data to county boundaries
    county_merged = counties_gdf.merge(
        county_agg,
        left_on='FIPS',
        right_on='FIPS',
        how='inner'
    )
    
    county_output = county_merged[['geometry'] + [col for col in county_agg.columns if col in county_merged.columns]]
    
    county_geojson = county_output.to_json()
    county_file = OUTPUT_DIR / "biomed_counties.geojson"
    with open(county_file, 'w') as f:
        json.dump(json.loads(county_geojson), f, indent=2)
    
    print(f"   ✓ Created {county_file}")
    print(f"   ✓ Features: {len(county_output):,}")
else:
    # Create without geometry
    county_geojson = {
        "type": "FeatureCollection",
        "features": []
    }
    for _, row in county_agg.iterrows():
        feature = {
            "type": "Feature",
            "properties": row.dropna().to_dict(),
            "geometry": None
        }
        county_geojson["features"].append(feature)
    
    county_file = OUTPUT_DIR / "biomed_counties.geojson"
    with open(county_file, 'w') as f:
        json.dump(county_geojson, f, indent=2)
    
    print(f"   ✓ Created {county_file} (no geometry)")
    print(f"   ✓ Features: {len(county_agg):,}")

# ============================================================================
# LEVEL 3: CHAPTERS (aggregate counties, include chapter/region/division)
# ============================================================================
print("\n📚 Creating Chapter GeoJSON...")

# Aggregate data by chapter
chapter_agg = df.groupby('Chapter').agg({
    **{col: 'first' for col in ['Region', 'Division', 'RCODE', 'DCODE']},
    **{col: 'sum' for col in year_cols},
    **{col: 'first' for col in [c for c in total_cols if 'Chapter' in c or 'Region' in c or 'Division' in c]}
}).reset_index()

chapter_has_geometry = False

# Try to get geometry from shapefile first
if chapters_gdf is not None and len(chapters_gdf) > 0:
    chapter_name_col = None
    for col in chapters_gdf.columns:
        if col.lower() in ['chapter', 'name', 'chapter_name', 'chapter_nam']:
            chapter_name_col = col
            break
    
    if chapter_name_col:
        chapters_gdf['chapter_match'] = chapters_gdf[chapter_name_col].astype(str).str.strip().str.upper()
        chapter_agg['chapter_match'] = chapter_agg['Chapter'].astype(str).str.strip().str.upper()
        
        chapter_merged = chapters_gdf.merge(
            chapter_agg,
            left_on='chapter_match',
            right_on='chapter_match',
            how='inner'
        )
        
        if len(chapter_merged) > 0:
            chapter_output = chapter_merged[['geometry'] + [col for col in chapter_agg.columns if col in chapter_merged.columns and col != 'chapter_match']]
            chapter_has_geometry = True

# If no shapefile geometry, create by dissolving counties
if not chapter_has_geometry and counties_gdf is not None:
    print("   Creating chapter boundaries by dissolving counties...")
    # Join counties with chapter data
    county_chapter_lookup = df[['FIPS', 'Chapter']].drop_duplicates()
    counties_with_chapter = counties_gdf.merge(county_chapter_lookup, on='FIPS', how='inner')
    
    if 'Chapter' in counties_with_chapter.columns and len(counties_with_chapter) > 0:
        # Dissolve counties by chapter
        chapter_gdf = counties_with_chapter.dissolve(by='Chapter', aggfunc='first')
        chapter_gdf = chapter_gdf.reset_index()
        
        # Merge with aggregated data
        chapter_merged = chapter_gdf.merge(chapter_agg, on='Chapter', how='inner')
        chapter_output = chapter_merged[['geometry'] + [col for col in chapter_agg.columns if col in chapter_merged.columns]]
        chapter_has_geometry = True

# Save chapter GeoJSON
if chapter_has_geometry:
    chapter_geojson = chapter_output.to_json()
    chapter_file = OUTPUT_DIR / "biomed_chapters.geojson"
    with open(chapter_file, 'w') as f:
        json.dump(json.loads(chapter_geojson), f, indent=2)
    print(f"   ✓ Created {chapter_file}")
    print(f"   ✓ Features: {len(chapter_output):,}")
else:
    # Create without geometry
    chapter_geojson = {
        "type": "FeatureCollection",
        "features": []
    }
    for _, row in chapter_agg.iterrows():
        feature = {
            "type": "Feature",
            "properties": row.dropna().to_dict(),
            "geometry": None
        }
        chapter_geojson["features"].append(feature)
    
    chapter_file = OUTPUT_DIR / "biomed_chapters.geojson"
    with open(chapter_file, 'w') as f:
        json.dump(chapter_geojson, f, indent=2)
    print(f"   ✓ Created {chapter_file} (no geometry)")
    print(f"   ✓ Features: {len(chapter_agg):,}")

# ============================================================================
# LEVEL 4: REGIONS (aggregate chapters, include region/division)
# ============================================================================
print("\n🌍 Creating Region GeoJSON...")

# Aggregate data by region
region_agg = df.groupby('Region').agg({
    **{col: 'first' for col in ['Division', 'RCODE', 'DCODE']},
    **{col: 'sum' for col in year_cols},
    **{col: 'first' for col in [c for c in total_cols if 'Region' in c or 'Division' in c]}
}).reset_index()

# Create region boundaries by dissolving counties or chapters
region_has_geometry = False

# Try dissolving counties by region first (most reliable)
if counties_gdf is not None:
    print("   Creating region boundaries by dissolving counties...")
    region_lookup = df[['FIPS', 'Region']].drop_duplicates()
    counties_with_region = counties_gdf.merge(region_lookup, on='FIPS', how='inner')
    
    if 'Region' in counties_with_region.columns and len(counties_with_region) > 0:
        region_gdf = counties_with_region.dissolve(by='Region', aggfunc='first')
        region_gdf = region_gdf.reset_index()
        
        region_merged = region_gdf.merge(region_agg, on='Region', how='inner')
        region_output = region_merged[['geometry'] + [col for col in region_agg.columns if col in region_merged.columns]]
        region_has_geometry = True

# Save region GeoJSON
if region_has_geometry:
    region_geojson = region_output.to_json()
    region_file = OUTPUT_DIR / "biomed_regions.geojson"
    with open(region_file, 'w') as f:
        json.dump(json.loads(region_geojson), f, indent=2)
    print(f"   ✓ Created {region_file}")
    print(f"   ✓ Features: {len(region_output):,}")
elif not region_has_geometry:
    # Create without geometry
    region_geojson = {
        "type": "FeatureCollection",
        "features": []
    }
    for _, row in region_agg.iterrows():
        feature = {
            "type": "Feature",
            "properties": row.dropna().to_dict(),
            "geometry": None
        }
        region_geojson["features"].append(feature)
    
    region_file = OUTPUT_DIR / "biomed_regions.geojson"
    with open(region_file, 'w') as f:
        json.dump(region_geojson, f, indent=2)
    
    print(f"   ✓ Created {region_file} (no geometry)")
    print(f"   ✓ Features: {len(region_agg):,}")

# ============================================================================
# LEVEL 5: DIVISIONS (aggregate regions, include division only)
# ============================================================================
print("\n🌎 Creating Division GeoJSON...")

# Aggregate data by division
division_agg = df.groupby('Division').agg({
    **{col: 'first' for col in ['DCODE']},
    **{col: 'sum' for col in year_cols},
    **{col: 'first' for col in [c for c in total_cols if 'Division' in c]}
}).reset_index()

# Create division boundaries by dissolving counties
division_has_geometry = False

# Dissolve counties by division
if counties_gdf is not None:
    print("   Creating division boundaries by dissolving counties...")
    division_lookup = df[['FIPS', 'Division']].drop_duplicates()
    counties_with_division = counties_gdf.merge(division_lookup, on='FIPS', how='inner')
    
    if 'Division' in counties_with_division.columns and len(counties_with_division) > 0:
        division_gdf = counties_with_division.dissolve(by='Division', aggfunc='first')
        division_gdf = division_gdf.reset_index()
        
        division_merged = division_gdf.merge(division_agg, on='Division', how='inner')
        division_output = division_merged[['geometry'] + [col for col in division_agg.columns if col in division_merged.columns]]
        division_has_geometry = True

# Save division GeoJSON
if division_has_geometry:
    division_geojson = division_output.to_json()
    division_file = OUTPUT_DIR / "biomed_divisions.geojson"
    with open(division_file, 'w') as f:
        json.dump(json.loads(division_geojson), f, indent=2)
    print(f"   ✓ Created {division_file}")
    print(f"   ✓ Features: {len(division_output):,}")
elif not division_has_geometry:
    # Create without geometry
    division_geojson = {
        "type": "FeatureCollection",
        "features": []
    }
    for _, row in division_agg.iterrows():
        feature = {
            "type": "Feature",
            "properties": row.dropna().to_dict(),
            "geometry": None
        }
        division_geojson["features"].append(feature)
    
    division_file = OUTPUT_DIR / "biomed_divisions.geojson"
    with open(division_file, 'w') as f:
        json.dump(division_geojson, f, indent=2)
    
    print(f"   ✓ Created {division_file} (no geometry)")
    print(f"   ✓ Features: {len(division_agg):,}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 70)
print("✅ COMPLETE!")
print("=" * 70)
print(f"\nGeoJSON files created in: {OUTPUT_DIR}")
print("\nFiles created:")
print("  📦 biomed_zip_codes.geojson     - ZIP code level (all fields)")
print("  🏛️  biomed_counties.geojson      - County level (county/chapter/region/division)")
print("  📚 biomed_chapters.geojson      - Chapter level (chapter/region/division)")
print("  🌍 biomed_regions.geojson        - Region level (region/division)")
print("  🌎 biomed_divisions.geojson     - Division level (division)")
print("\nYou can now upload these GeoJSON files directly to ArcGIS Online!")


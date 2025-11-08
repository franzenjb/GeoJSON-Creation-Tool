#!/usr/bin/env python3
"""
Create ZIP code GeoJSON with ALL data fields including ECODE, DCODE, RCODE
Uses Esri Living Atlas service to get ZIP boundaries
"""

import geopandas as gpd
import pandas as pd
import json
from pathlib import Path
import requests
from io import BytesIO
import zipfile
import sys

# Add scripts directory to path for imports
SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

from column_detector import detect_columns, standardize_dataframe

# Configuration
DATA_DIR = Path(__file__).parent.parent
CSV_FILE = DATA_DIR / "Biomed by zip code_ENHANCED.csv"
OUTPUT_DIR = DATA_DIR / "geojson_output"
OUTPUT_DIR.mkdir(exist_ok=True)

print("=" * 70)
print("Creating ZIP Code GeoJSON with ALL data fields")
print("=" * 70)

# Step 1: Load CSV data and detect columns
print("\n1. Loading CSV data...")
df = pd.read_csv(CSV_FILE, low_memory=False)

print(f"   ✓ Loaded {len(df):,} rows")
print(f"   ✓ Columns: {len(df.columns)}")
print(f"   ✓ Column names: {list(df.columns)[:10]}...")

# Auto-detect column names
print("\n   Detecting column names...")
detected_cols = detect_columns(df)
print(f"   ✓ Detected columns:")
for std_name, actual_name in detected_cols.items():
    print(f"      {std_name} → {actual_name}")

# Standardize dataframe
df, detected_cols = standardize_dataframe(df, detected_cols)

print(f"   ✓ Standardized dataframe")
print(f"   ✓ Unique ZIP codes: {df['Zip'].nunique():,}")

# Show what CODE columns we have
code_cols = [c for c in df.columns if c in ['ECODE', 'RCODE', 'DCODE']]
if code_cols:
    print(f"   ✓ CODE columns detected: {code_cols}")

# Step 2: Try to get ZIP boundaries from Census (try different URL formats)
print("\n2. Downloading ZIP code boundaries...")

zips_gdf = None
zip_urls = [
    # Try 2020 format (ZCTA5)
    "https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_us_zcta520_500k.zip",
    # Try 2019 format
    "https://www2.census.gov/geo/tiger/GENZ2019/shp/cb_2019_us_zcta510_500k.zip",
    # Try 2018 format  
    "https://www2.census.gov/geo/tiger/GENZ2018/shp/cb_2018_us_zcta510_500k.zip",
]

for zips_url in zip_urls:
    try:
        print(f"   Trying: {zips_url.split('/')[-1]}")
        response = requests.get(zips_url, timeout=60)
        response.raise_for_status()
        
        with zipfile.ZipFile(BytesIO(response.content)) as z:
            # Extract to temp directory
            temp_dir = OUTPUT_DIR / "temp_zips"
            temp_dir.mkdir(exist_ok=True)
            z.extractall(temp_dir)
            
            # Find the shapefile
            shp_files = [f for f in z.namelist() if f.endswith('.shp')]
            if shp_files:
                zips_gdf = gpd.read_file(temp_dir / shp_files[0])
                zips_gdf = zips_gdf.to_crs('EPSG:4326')
                
                # Find ZIP code column
                zip_col = None
                for col in ['ZCTA5CE20', 'ZCTA5CE10', 'ZCTA5', 'GEOID20', 'GEOID10', 'GEOID', 'ZCTA5CE00']:
                    if col in zips_gdf.columns:
                        zip_col = col
                        break
                
                if zip_col:
                    zips_gdf['ZIP_CODE'] = zips_gdf[zip_col].astype(str).str.zfill(5)
                    zips_gdf['geometry'] = zips_gdf['geometry'].simplify(0.0005, preserve_topology=True)
                    print(f"   ✓ Loaded {len(zips_gdf):,} ZIP codes from Census")
                    break
                else:
                    print(f"   ⚠ Could not find ZIP column. Available: {list(zips_gdf.columns)[:10]}")
                    zips_gdf = None
    except Exception as e:
        print(f"   ⚠ Failed: {str(e)[:80]}")
        continue

# Step 3: If Census failed, try using Esri service via arcgis Python API
if zips_gdf is None:
    print("\n3. Trying Esri Living Atlas service...")
    try:
        from arcgis.features import FeatureLayer
        
        # Esri's USA ZIP Code Areas service
        zip_service_url = "https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_ZIP_Code_Areas/FeatureServer/0"
        zip_layer = FeatureLayer(zip_service_url)
        
        # Get unique ZIPs from our data (limit to first 5000 for performance)
        unique_zips = df['Zip'].dropna().unique()[:5000]
        zip_where = " OR ".join([f"ZCTA5CE10 = '{z}'" for z in unique_zips[:100]])  # Limit query size
        
        print(f"   Querying Esri service for {len(unique_zips)} ZIP codes...")
        zip_fset = zip_layer.query(
            where=zip_where if len(unique_zips) <= 100 else "1=1",
            return_geometry=True,
            out_sr=4326,
            return_all_records=True if len(unique_zips) <= 100 else False
        )
        
        if zip_fset and len(zip_fset.features) > 0:
            # Convert to GeoDataFrame
            features = []
            for feat in zip_fset.features:
                if feat.geometry:
                    features.append({
                        'ZIP_CODE': str(feat.attributes.get('ZCTA5CE10', '')).zfill(5),
                        'geometry': feat.geometry
                    })
            
            if features:
                zips_gdf = gpd.GeoDataFrame(features, crs='EPSG:4326')
                zips_gdf['geometry'] = zips_gdf['geometry'].simplify(0.0005, preserve_topology=True)
                print(f"   ✓ Loaded {len(zips_gdf):,} ZIP codes from Esri")
        else:
            print("   ⚠ No features returned from Esri service")
    except Exception as e:
        print(f"   ⚠ Esri service failed: {e}")
        print("   (You may need to install arcgis package: pip install arcgis)")

# Step 4: Create ZIP GeoJSON
print("\n4. Creating ZIP code GeoJSON...")

if zips_gdf is not None and 'ZIP_CODE' in zips_gdf.columns:
    # Join CSV data to ZIP boundaries
    print(f"   Joining {len(df):,} CSV rows to {len(zips_gdf):,} ZIP boundaries...")
    
    zip_merged = zips_gdf.merge(
        df,
        left_on='ZIP_CODE',
        right_on='Zip',
        how='inner'
    )
    
    print(f"   ✓ Matched {len(zip_merged):,} ZIP codes")
    
    # Keep all columns from CSV (including ECODE, DCODE, RCODE)
    zip_output = zip_merged[['geometry'] + [col for col in df.columns if col in zip_merged.columns]]
    
    # Verify CODE columns are included
    code_cols_in_output = [c for c in zip_output.columns if 'CODE' in c.upper()]
    print(f"   ✓ CODE columns in output: {code_cols_in_output}")
    
    zip_geojson = zip_output.to_json()
    zip_file = OUTPUT_DIR / "biomed_zip_codes.geojson"
    with open(zip_file, 'w') as f:
        json.dump(json.loads(zip_geojson), f, indent=2)
    
    print(f"\n   ✅ Created {zip_file}")
    print(f"   ✓ Features: {len(zip_output):,}")
    print(f"   ✓ File size: {zip_file.stat().st_size / 1024 / 1024:.1f} MB")
    
    # Show sample of what's included
    print(f"\n   Sample columns in GeoJSON:")
    sample_cols = ['Zip', 'ECODE', 'RCODE', 'DCODE', 'Chapter', 'Region', 'Division', '2022', '2023', '2024', '2025']
    available_sample = [c for c in sample_cols if c in zip_output.columns]
    print(f"   {', '.join(available_sample[:10])}...")
    
else:
    # Create GeoJSON without geometry (can be joined later in ArcGIS)
    print("   ⚠ No ZIP boundaries available - creating GeoJSON with data only")
    print("   (You can join this to ZIP boundaries in ArcGIS Online)")
    
    zip_geojson = {
        "type": "FeatureCollection",
        "features": []
    }
    
    for _, row in df.iterrows():
        feature = {
            "type": "Feature",
            "properties": row.dropna().to_dict(),
            "geometry": None
        }
        zip_geojson["features"].append(feature)
    
    zip_file = OUTPUT_DIR / "biomed_zip_codes.geojson"
    with open(zip_file, 'w') as f:
        json.dump(zip_geojson, f, indent=2)
    
    print(f"\n   ✅ Created {zip_file} (data only, no geometry)")
    print(f"   ✓ Features: {len(df):,}")
    print(f"   ✓ All fields included: ECODE, DCODE, RCODE, and all year columns")

print("\n" + "=" * 70)
print("✅ COMPLETE!")
print("=" * 70)
print(f"\nZIP GeoJSON file: {zip_file}")
print("\nThis file includes ALL data fields:")
print("  - ECODE, RCODE, DCODE")
print("  - Chapter, Region, Division")
print("  - All year columns (2022, 2023, 2024, 2025)")
print("  - All total columns")
print("  - County, FIPS, State, and all other CSV columns")


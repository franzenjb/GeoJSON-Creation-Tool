#!/usr/bin/env python3
"""
Column name detection utility for flexible CSV header recognition
Handles variations in column names (case, spaces, underscores, etc.)
"""

def normalize_column_name(col_name):
    """Normalize column name for matching"""
    import pandas as pd
    if pd.isna(col_name):
        return None
    return str(col_name).strip().lower().replace('_', ' ').replace('-', ' ')

def detect_columns(df):
    """
    Auto-detect column names with flexible matching
    Returns a dictionary mapping standard names to actual column names
    """
    normalized_cols = {normalize_column_name(col): col for col in df.columns}
    
    detected = {}
    
    # ZIP code variations
    zip_patterns = ['zip', 'zip code', 'zipcode', 'zcta', 'zcta5', 'postal code', 'postalcode']
    for pattern in zip_patterns:
        if pattern in normalized_cols:
            detected['Zip'] = normalized_cols[pattern]
            break
    
    # FIPS code variations
    fips_patterns = ['fips', 'fips code', 'fipscode', 'geoid', 'county fips', 'countyfips']
    for pattern in fips_patterns:
        if pattern in normalized_cols:
            detected['FIPS'] = normalized_cols[pattern]
            break
    
    # County variations (handle xCounty, County, etc.)
    county_patterns = ['county', 'county name', 'countyname', 'county_name', 'xcounty']
    for pattern in county_patterns:
        if pattern in normalized_cols:
            detected['County'] = normalized_cols[pattern]
            break
    
    # Chapter variations
    chapter_patterns = ['chapter', 'chapter name', 'chaptername', 'chapter_name']
    for pattern in chapter_patterns:
        if pattern in normalized_cols:
            detected['Chapter'] = normalized_cols[pattern]
            break
    
    # Region variations
    region_patterns = ['region', 'region name', 'regionname', 'region_name']
    for pattern in region_patterns:
        if pattern in normalized_cols:
            detected['Region'] = normalized_cols[pattern]
            break
    
    # Division variations
    division_patterns = ['division', 'division name', 'divisionname', 'division_name']
    for pattern in division_patterns:
        if pattern in normalized_cols:
            detected['Division'] = normalized_cols[pattern]
            break
    
    # ECODE variations
    ecode_patterns = ['ecode', 'e code', 'e_code', 'chapter code', 'chaptercode', 'chapter_code']
    for pattern in ecode_patterns:
        if pattern in normalized_cols:
            detected['ECODE'] = normalized_cols[pattern]
            break
    
    # RCODE variations
    rcode_patterns = ['rcode', 'r code', 'r_code', 'region code', 'regioncode', 'region_code']
    for pattern in rcode_patterns:
        if pattern in normalized_cols:
            detected['RCODE'] = normalized_cols[pattern]
            break
    
    # DCODE variations
    dcode_patterns = ['dcode', 'd code', 'd_code', 'division code', 'divisioncode', 'division_code']
    for pattern in dcode_patterns:
        if pattern in normalized_cols:
            detected['DCODE'] = normalized_cols[pattern]
            break
    
    # State variations
    state_patterns = ['state', 'state name', 'statename', 'state_name', 'st', 'state code', 'statecode']
    for pattern in state_patterns:
        if pattern in normalized_cols:
            detected['State'] = normalized_cols[pattern]
            break
    
    return detected

def standardize_dataframe(df, detected_cols):
    """
    Create a standardized dataframe with consistent column names
    """
    import pandas as pd
    
    # Create a copy
    df_std = df.copy()
    
    # Rename columns to standard names
    rename_map = {v: k for k, v in detected_cols.items()}
    df_std = df_std.rename(columns=rename_map)
    
    # Ensure required columns exist (create empty if missing, but don't overwrite existing)
    required_cols = ['Zip', 'FIPS', 'County', 'Chapter', 'Region', 'Division']
    for col in required_cols:
        if col not in df_std.columns:
            df_std[col] = None
    
    # Keep all original columns that weren't renamed
    # This preserves all data fields
    
    # Normalize ZIP and FIPS codes
    if 'Zip' in df_std.columns:
        df_std['Zip'] = df_std['Zip'].astype(str).str.replace('.0', '', regex=False).str.zfill(5)
    
    if 'FIPS' in df_std.columns:
        df_std['FIPS'] = df_std['FIPS'].astype(str).str.zfill(5)
    
    return df_std, detected_cols


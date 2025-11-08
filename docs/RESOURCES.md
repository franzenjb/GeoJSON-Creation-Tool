# Resources Reference

## Data Sources

### 1. US Census Bureau - Cartographic Boundary Files

**County Boundaries:**
- **URL**: `https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_county_500k.zip`
- **Format**: Shapefile (.shp, .shx, .dbf, .prj)
- **Coverage**: All US counties and county equivalents
- **Resolution**: 500k (simplified for web mapping)
- **Coordinate System**: Geographic (WGS84)
- **Update Frequency**: Annual
- **License**: Public domain
- **Documentation**: https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html

**ZIP Code Tabulation Areas (ZCTA5):**
- **URL**: `https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_us_zcta520_500k.zip`
- **Format**: Shapefile
- **Coverage**: All US ZIP Code Tabulation Areas
- **Resolution**: 500k
- **Coordinate System**: Geographic (WGS84)
- **Update Frequency**: Every 10 years (decennial census)
- **Note**: 2023 version not available, using 2020
- **License**: Public domain
- **Key Column**: `ZCTA5CE20` or `ZCTA5CE10` (5-digit ZIP code)

**Alternative Years Available:**
- 2020: `cb_2020_us_zcta520_500k.zip`
- 2019: `cb_2019_us_zcta510_500k.zip`
- 2018: `cb_2018_us_zcta510_500k.zip`

### 2. Esri Living Atlas

**USA ZIP Code Areas:**
- **Service URL**: `https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_ZIP_Code_Areas/FeatureServer/0`
- **Format**: ArcGIS Feature Service (REST API)
- **Coverage**: All US ZIP codes
- **Update Frequency**: Regular updates
- **Access**: Public (no authentication required for queries)
- **Key Column**: `ZCTA5CE10` (5-digit ZIP code)
- **Documentation**: https://www.arcgis.com/home/item.html?id=8d2012a2016e484dafaac0451f9aea24

**USA Counties:**
- **Service URL**: `https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Counties/FeatureServer/0`
- **Format**: ArcGIS Feature Service
- **Coverage**: All US counties
- **Key Column**: `FIPS` (5-digit FIPS code)

## Python Libraries

### Required

**geopandas** (v1.0.1+)
- Purpose: Geographic data manipulation
- Key functions: `read_file()`, `dissolve()`, `merge()`, `to_json()`, `simplify()`
- Installation: `pip install geopandas`
- Documentation: https://geopandas.org/

**pandas** (v2.0+)
- Purpose: Data manipulation and aggregation
- Key functions: `read_csv()`, `groupby()`, `agg()`, `merge()`
- Installation: `pip install pandas`
- Documentation: https://pandas.pydata.org/

**requests** (v2.0+)
- Purpose: Downloading boundary files
- Key functions: `get()`, `raise_for_status()`
- Installation: `pip install requests`
- Documentation: https://requests.readthedocs.io/

### Optional

**arcgis** (Python API)
- Purpose: Access Esri services as fallback
- Key classes: `FeatureLayer`, `GIS`
- Installation: `pip install arcgis`
- Documentation: https://developers.arcgis.com/python/

## Key Concepts

### FIPS Codes
- **Format**: 5-digit code (State FIPS + County FIPS)
- **Example**: `01115` = Alabama (01) + St. Clair County (115)
- **Normalization**: Zero-pad to 5 digits: `str.zfill(5)`
- **Source**: US Census Bureau

### ZIP Codes / ZCTA5
- **Format**: 5-digit code
- **Example**: `35004`
- **Normalization**: Zero-pad to 5 digits: `str.zfill(5)`
- **Note**: ZCTA5 (ZIP Code Tabulation Areas) are approximations of ZIP codes
- **Source**: US Census Bureau

### Geographic Dissolve
- **Process**: Merging adjacent boundaries by grouping field
- **Example**: Multiple counties → Single chapter boundary
- **Function**: `geopandas.GeoDataFrame.dissolve(by='Chapter')`
- **Result**: Combined geometry with aggregated attributes

### Geometry Simplification
- **Purpose**: Reduce file size for web mapping
- **Function**: `geometry.simplify(tolerance)`
- **Tolerance**: Higher = more simplification (smaller files)
- **Typical values**: 0.0005 (ZIP), 0.001 (County), 0.01 (Region)

## File Formats

### Shapefile
- **Components**: .shp (geometry), .shx (index), .dbf (attributes), .prj (projection)
- **Read with**: `geopandas.read_file()`
- **Source**: Census Bureau downloads

### GeoJSON
- **Format**: JSON with geometry and properties
- **Structure**: FeatureCollection → Features → Geometry + Properties
- **Export with**: `geopandas.to_json()` or `json.dump()`
- **Use**: Upload to ArcGIS Online, web mapping

## Coordinate Systems

### WGS84 (EPSG:4326)
- **Type**: Geographic coordinate system
- **Units**: Degrees (latitude/longitude)
- **Standard**: Used by web mapping (Google Maps, ArcGIS Online)
- **Conversion**: `gdf.to_crs('EPSG:4326')`

### Web Mercator (EPSG:3857)
- **Type**: Projected coordinate system
- **Units**: Meters
- **Use**: Web tile services
- **Not used in this pipeline** (we use WGS84)

## Data Processing Steps

1. **Load CSV** → Pandas DataFrame
2. **Normalize IDs** → Zero-pad ZIP/FIPS codes
3. **Download Boundaries** → Shapefile from Census
4. **Load Boundaries** → GeoDataFrame with geopandas
5. **Join Data** → Merge CSV data to boundaries
6. **Aggregate** → Group by geographic level, sum numeric columns
7. **Dissolve** → Merge boundaries by grouping field
8. **Simplify** → Reduce geometry complexity
9. **Export** → Save as GeoJSON

## Performance Considerations

### File Sizes
- **ZIP GeoJSON**: ~150 MB (13,760 features)
- **County GeoJSON**: ~21 MB (2,129 features)
- **Chapter GeoJSON**: ~9.6 MB (191 features)
- **Region GeoJSON**: ~6.9 MB (42 features)
- **Division GeoJSON**: ~6.2 MB (6 features)

### Processing Time
- **County download**: ~30 seconds
- **ZIP download**: ~2-3 minutes
- **Dissolve operations**: ~10-30 seconds per level
- **Total pipeline**: ~5-10 minutes

### Memory Usage
- **Peak**: ~2-4 GB (during ZIP processing)
- **Typical**: ~500 MB - 1 GB

## Troubleshooting Resources

### Census Bureau
- **Main Site**: https://www.census.gov/
- **Boundary Files**: https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html
- **TIGER/Line Files**: https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html

### GeoPandas
- **Documentation**: https://geopandas.org/
- **Examples**: https://geopandas.org/en/stable/gallery/
- **GitHub**: https://github.com/geopandas/geopandas

### ArcGIS Python API
- **Documentation**: https://developers.arcgis.com/python/
- **Feature Layer**: https://developers.arcgis.com/python/api-reference/arcgis.features.toc.html#featurelayer


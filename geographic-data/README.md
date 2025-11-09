# Geographic Boundary Files

This folder contains GeoJSON boundary files used for spatial joins when creating chloropleth maps.

## Files

| File | Size | Description | Source |
|------|------|-------------|--------|
| `zip_boundaries.geojson` | 122MB | US ZIP Code boundaries with Red Cross chapter mapping | `/Users/jefffranzen/Desktop/bingo/Biomed by zip code_with_redcross.geojson` |
| `county_boundaries.geojson` | 33MB | US County boundaries with Red Cross organizational data | `/Users/jefffranzen/alice-red-cross-data/Alice Chloropleth Maps/redcross-counties.geojson` |
| `chapter_boundaries.geojson` | 11MB | American Red Cross Chapter boundaries | `/Users/jefffranzen/alice-red-cross-data/Alice Chloropleth Maps/redcross-chapters.geojson` |
| `region_boundaries.geojson` | 7.4MB | American Red Cross Region boundaries | `/Users/jefffranzen/alice-red-cross-data/Alice Chloropleth Maps/redcross-regions.geojson` |
| `division_boundaries.geojson` | 5.6MB | American Red Cross Division boundaries | `/Users/jefffranzen/alice-red-cross-data/Alice Chloropleth Maps/redcross-divisions.geojson` |

**Total Size:** ~180MB

## Note

These files are **NOT committed to GitHub** (listed in `.gitignore`) due to their large size.

If you need to recreate this folder:
1. Copy the files from the source paths listed above
2. Rename them to match the names in this folder

## Usage

These files are used by the GeoJSON Creation Tool for:
1. Spatial joins between CSV data and geographic boundaries
2. Hierarchical roll-ups (ZIP → County → Chapter → Region → Division)
3. Generating output GeoJSON files for ArcGIS Online chloropleth maps

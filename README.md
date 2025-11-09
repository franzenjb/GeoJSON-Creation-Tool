# Red Cross GeoJSON & Data Tools

A comprehensive suite of 6 web-based tools for American Red Cross data processing, geographic analysis, and visualization. All tools run entirely in the browser - no server required.

**🌐 Live Demo:** https://franzenjb.github.io/GeoJSON-Creation-Tool/

## 🎯 Six Powerful Tools in One

### 1. **Code Lookup** 🔍
Search and explore American Red Cross organizational hierarchy
- **33,120 ZIP codes** (100% US coverage including all territories)
- Search by ZIP, County, FIPS, Chapter, Region, or Division
- Complete Red Cross hierarchy mapping (ECODE, RCODE, DCODE)
- Coverage: All 50 states + Puerto Rico, Virgin Islands, Guam, American Samoa

### 2. **CSV Roll-Up** 📊
Aggregate ZIP-level data to higher geographic levels
- Upload ZIP-level CSV data
- Automatically rolls up to County → Chapter → Region → Division
- Adds FIPS codes and Red Cross hierarchy codes
- Outputs hierarchical CSV with level-specific columns
- Perfect for creating multi-level datasets

### 3. **Create GeoJSON** 🗺️
Transform CSV data into professional GeoJSON files
- Supports ZIP, County, Chapter, Region, and Division levels
- Automatic boundary loading from US Census & ArcGIS Red Cross geography
- Intelligent hierarchical CSV detection
- Real-time join statistics and map preview
- Download ready-to-use GeoJSON files

### 4. **Orgler URL Creator** 🔗
Convert Power BI report URLs to Orgler format
- Paste Power BI report URL
- Automatically generates Orgler URL for embedding in ArcGIS Story Maps
- One-click copy to clipboard

### 5. **ArcGIS Pop-up Creator** 📋
Generate custom ArcGIS pop-up HTML with inline CSS
- Paste ArcGIS REST API feature layer URL
- Automatically fetches field definitions
- Select fields to include in pop-up
- Generates Red Cross branded HTML with inline CSS
- Copy-paste directly into ArcGIS Pro or Online

### 6. **Mapbox Geocoder** 🌐
Geocode addresses to GeoJSON or CSV
- Upload CSV with addresses
- Uses Mapbox Geocoding API
- Export to GeoJSON or CSV with coordinates
- Batch geocoding support

## 🚀 Quick Start

### Option 1: Use the Live Version
Simply visit: **https://franzenjb.github.io/GeoJSON-Creation-Tool/**

### Option 2: Run Locally

```bash
# Clone the repository
git clone https://github.com/franzenjb/GeoJSON-Creation-Tool.git
cd GeoJSON-Creation-Tool

# Start a local web server
python3 -m http.server 8080

# Open in browser
open http://localhost:8080
```

## 📁 Key Files

```
GeoJSON-Creation-Tool/
├── index.html                          # Main application (6 tabs)
├── zip_to_fips_comprehensive.js        # 33,120 ZIPs → Red Cross hierarchy (9.5 MB)
├── zip_to_redcross_comprehensive.csv   # Source data (4.5 MB)
├── lookup_data.js                      # Chapter & County data
├── state_names.js                      # State name mappings
└── README.md                           # This file
```

## 🗄️ Data Sources

### ZIP Code Database (100% US Coverage)
- **Source:** US Census ZCTA (ZIP Code Tabulation Areas) 2010
- **Red Cross Mapping:** ArcGIS Red Cross Master Geography 2022
- **Coverage:** 33,120 ZIP codes
  - All 50 states
  - Puerto Rico (131 ZIPs)
  - US Virgin Islands
  - Guam
  - American Samoa
  - Alaska (including remote areas)

### Red Cross Organizational Structure
- **Source:** ArcGIS Red Cross Master Geography 2022
- **API:** https://services.arcgis.com/pGfbNJoYypmNq86F/ArcGIS/rest/services/Master_ARC_Geography_2022/FeatureServer/
- **Coverage:** 3,162 counties with complete Chapter/Region/Division hierarchy
- **Layers:**
  - Layer 1: Divisions (6 divisions)
  - Layer 2: Regions (48 regions)
  - Layer 4: Chapters (226 chapters)
  - Layer 5: Counties (3,162 counties)

### Geographic Boundaries
- **Counties:** ArcGIS Red Cross Master Geography 2022
- **ZIP Codes:** US Census ZCTA Cartographic Boundary Files
- **Chapters/Regions/Divisions:** Dynamically loaded from ArcGIS FeatureServer

## 📊 CSV Requirements

### For CSV Roll-Up (Tab 2):
Your CSV must have:
- **ZIP column:** `Zip`, `ZIP`, `zip`, or `ZIP Code`
- **Data columns:** Numeric values to aggregate
- Optional: `County`, `FIPS`, `ECODE`, `RCODE`, `DCODE` (will be added if missing)

### For Create GeoJSON (Tab 3):
Your CSV must have:
- **ID column** matching your target level:
  - ZIP level: ZIP code column
  - County level: FIPS code column
  - Chapter level: ECODE column
  - Region level: RCODE column
  - Division level: DCODE column
- **Data columns:** Fields to include in GeoJSON properties

## 🎨 Workflow Example

### Creating Multi-Level Blood Drive Data

1. **Start with ZIP-level data** (Tab 2: CSV Roll-Up)
   ```csv
   ZIP,Drives,Products_Collected
   10001,5,450
   10002,3,280
   ...
   ```

2. **Roll up to all levels**
   - Upload CSV → Automatically aggregates to County, Chapter, Region, Division
   - Downloads hierarchical CSV with columns like:
     - `Drives (ZIP)`, `Drives (County)`, `Drives (Chapter)`, etc.
     - Adds FIPS, ECODE, RCODE, DCODE

3. **Create GeoJSON files** (Tab 3: Create GeoJSON)
   - Upload the rolled-up CSV
   - Select "Division" level
   - Tool detects hierarchical format
   - Creates Division GeoJSON with aggregated data
   - Map preview shows 6 division boundaries with data

4. **Visualize in ArcGIS**
   - Import GeoJSON to ArcGIS Online
   - Style by `RBC Products Collected (Division)`
   - Use Pop-up Creator (Tab 5) for branded pop-ups

## 🛠️ Technologies

- **Frontend Only:** Pure HTML5, CSS3, Vanilla JavaScript
- **Data Processing:** Client-side CSV parsing, GeoJSON manipulation
- **APIs:**
  - ArcGIS REST API (Red Cross geography)
  - Mapbox Geocoding API (geocoding tool)
- **No Backend Required:** All processing happens in your browser

## 📈 Performance

- **ZIP Database:** 33,120 records load in ~2 seconds
- **Hierarchical Roll-Up:** Processes 1,000 ZIPs in <1 second
- **GeoJSON Creation:** Division level (6 features) in <3 seconds
- **File Sizes:**
  - ZIP database: 9.5 MB (JavaScript), 4.5 MB (CSV)
  - Division GeoJSON: ~500 KB
  - ZIP GeoJSON: Can be large (14,000+ features)

## 🔧 Advanced Features

### Hierarchical CSV Support
The tool automatically detects hierarchical CSVs with level-specific columns:
```csv
ZIP,County,DCODE,Drives (ZIP),Drives (County),Drives (Division)
10001,"New York, NY",D27,5,27,649
```

When creating Division GeoJSON:
- Detects hierarchical format
- Uses `Drives (Division)` column instead of aggregating
- Groups by DCODE
- Faster processing, more accurate results

### Dynamic Boundary Loading
- Automatically fetches boundaries from ArcGIS when needed
- Caches in browser for faster subsequent loads
- Falls back to US Census data for ZIPs
- No manual boundary file management

### Smart Column Detection
- Automatically finds ZIP, FIPS, ECODE, RCODE, DCODE columns
- Case-insensitive matching
- Handles variations (e.g., "ZIP Code", "Zip", "zip")
- Detects numeric columns for aggregation

## 🐛 Troubleshooting

### "No joins found" when creating GeoJSON
- **Check ID column:** Ensure your CSV has the correct ID column for your chosen level
- **Check format:** Division codes should be like "D21", Region codes like "32R16", etc.
- **Try hierarchical:** If you have a rolled-up CSV, the tool will automatically use pre-aggregated values

### Slow performance with large files
- **Use hierarchical CSVs:** Pre-aggregate data using Tab 2 (CSV Roll-Up)
- **Start with higher levels:** Try County/Chapter instead of ZIP
- **Close other tabs:** Browser memory matters

### Missing territories
- All US territories are now included! If you find a missing ZIP, please report it.

## 📄 License

This tool uses public domain data from the US Census Bureau and official American Red Cross geography data. Code is provided as-is for reuse.

## 🙏 Credits

- **US Census Bureau** - ZCTA boundary data
- **American Red Cross** - Official geography and organizational structure
- **ArcGIS Platform** - Hosting Red Cross Master Geography service
- **Mapbox** - Geocoding API

## 🔗 Related Repositories

- **Portfolio Showcase:** https://franzenjb.github.io/portfolio-showcase/ (merged into this tool)
- **ALICE Master Database:** https://github.com/franzenjb/alice_master_database (poverty data)
- **County Consolidation Tool:** ~/county-consolidation-tool/ (data processing scripts)

## 📞 Support

Issues? Questions? Please open an issue on GitHub:
https://github.com/franzenjb/GeoJSON-Creation-Tool/issues

---

**Made with ❤️ for the American Red Cross**

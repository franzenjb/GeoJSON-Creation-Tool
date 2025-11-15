# Red Cross GeoJSON & Data Tools

A comprehensive suite of 9 web-based tools for American Red Cross data processing, geographic analysis, and visualization. All tools run entirely in the browser - no server required.

**🌐 Live Demo:** https://franzenjb.github.io/GeoJSON-Creation-Tool/

## 🆕 Recent Updates

- **Data Enrichment Tool**: Simplified from CSV Roll-Up - now ONLY adds 8 geographic hierarchy columns, preserving all original data
- **Multi-Provider Geocoding**: All 3 providers (Mapbox, Geoapify, Bing Maps) are 100% FREE
- **Enhanced Data Enrichment**: Larger, easier-to-read INPUT/OUTPUT examples with visual improvements
- **Pop-up Creator Samples**: Pre-filled field definition examples for quick testing
- **Professional Documentation**: Clear, technical explanations throughout all tools
- **100% US Coverage**: All 33,120 ZIP codes including territories (PR, VI, Guam, American Samoa)

## 🎯 Nine Powerful Tools in One

### 1. **Code Lookup** 🔍
Search and explore American Red Cross organizational hierarchy
- **33,120 ZIP codes** (100% US coverage including all territories)
- Search by ZIP, County, FIPS, Chapter, Region, or Division
- Complete Red Cross hierarchy mapping (ECODE, RCODE, DCODE)
- Coverage: All 50 states + Puerto Rico, Virgin Islands, Guam, American Samoa

### 2. **Data Enrichment** 📊
Enrich your data with complete Red Cross geographic hierarchy
- Upload CSV with **ZIP codes**, **County FIPS codes**, or **County + State names**
- Flexible matching: accepts "Dallas" or "Dallas County", "TX" or "Texas"
- Adds 8 geographic hierarchy columns: County, FIPS, ECODE, Chapter Name, RCODE, Region Name, DCODE, Division Name
- Keeps ALL original columns and rows intact
- Perfect for analysis, reporting, and creating choropleth maps
- 100% Red Cross hierarchy compliance (33,120 ZIPs, 3,162 counties, 226 chapters)

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

### 6. **Address Geocoder** 🌐
Geocode addresses to GeoJSON or CSV with 3 FREE provider options
- **All 3 providers are 100% FREE** with generous limits
- **Mapbox** (default): 100,000/month FREE (requires credit card)
- **Geoapify**: 3,000/day FREE (~90k/month, no credit card, can cache results)
- **Bing Maps**: 125,000/year FREE (~10k/month, no credit card)
- Upload CSV with address columns
- Export to GeoJSON or CSV with coordinates
- Batch geocoding support with progress tracking

### 7. **Metadata BETA** 📋
Extract and analyze metadata from ArcGIS Feature Services
- Paste ArcGIS REST API URL
- Automatically fetches layer metadata and field definitions
- View field types, domains, and statistics
- Export metadata to CSV or JSON

### 8. **OAuth Tokens** 🔐
Generate OAuth tokens for ArcGIS API authentication
- Supports multiple authentication flows
- Token generation for ArcGIS Online and Enterprise
- Secure credential management
- Copy tokens to clipboard for use in scripts and applications

### 9. **Hi-Res Captures** 📸
Capture high-resolution screenshots of ArcGIS web maps
- Generate publication-quality map images
- Supports custom dimensions and resolutions
- Export to PNG or JPEG formats
- Perfect for reports, presentations, and documentation

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

### For Data Enrichment (Tab 2):
Your CSV must have **one of these**:
- **ZIP column:** `Zip`, `ZIP`, `zip`, or `ZIP Code`
- **County FIPS column:** 5-digit FIPS code
- **County + State columns:** County name (with or without "County") + State (abbreviation or full name)
  - Examples: "Dallas" + "TX", "Dallas County" + "Texas", "Orleans Parish" + "LA"

**Any data columns:** All original columns will be preserved

**Tool adds:** `County`, `FIPS`, `ECODE`, `Chapter`, `RCODE`, `Region`, `DCODE`, `Division`

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

### Creating Enriched Building Data for GeoJSON Mapping

1. **Start with your data** (Tab 2: Data Enrichment)
   ```csv
   Building_ID,Address,City,ZIP,Status,Owner
   B14625,113 S LAS POSAS RD,SAN MARCOS,92078,Active,Leased
   B14627,400 MAIN ST,BROCKWAY,15824,Active,Licensed
   ...
   ```

2. **Enrich with geographic hierarchy**
   - Upload CSV → Tool adds 8 geographic columns
   - Downloads enriched CSV with ALL original columns plus:
     - `County`, `FIPS`, `ECODE`, `Chapter`, `RCODE`, `Region`, `DCODE`, `Division`
   - Every row keeps all original data

3. **Create GeoJSON files** (Tab 3: Create GeoJSON)
   - Upload the enriched CSV
   - Select your desired level (ZIP, County, Chapter, Region, or Division)
   - Tool creates GeoJSON with geographic boundaries
   - Map preview shows features with your data

4. **Visualize in ArcGIS**
   - Import GeoJSON to ArcGIS Online
   - Style by any of your data columns
   - Use Pop-up Creator (Tab 5) for branded pop-ups

## 🛠️ Technologies

- **Frontend Only:** Pure HTML5, CSS3, Vanilla JavaScript
- **Data Processing:** Client-side CSV parsing, GeoJSON manipulation
- **APIs:**
  - ArcGIS REST API (Red Cross geography)
  - Geoapify, Mapbox, & Bing Maps Geocoding APIs (multi-provider geocoding)
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
- **Enrich first:** Use Tab 2 (Data Enrichment) to add geographic hierarchy
- **Start with higher levels:** Try County/Chapter instead of ZIP for GeoJSON creation
- **Close other tabs:** Browser memory matters

### Missing territories
- All US territories are now included! If you find a missing ZIP, please report it.

## 📄 License

This tool uses public domain data from the US Census Bureau and official American Red Cross geography data. Code is provided as-is for reuse.

## 🙏 Credits

- **US Census Bureau** - ZCTA boundary data
- **American Red Cross** - Official geography and organizational structure
- **ArcGIS Platform** - Hosting Red Cross Master Geography service
- **Geoapify** - Geocoding API (recommended provider)
- **Mapbox** - Geocoding API
- **Bing Maps** - Geocoding API

## 🔗 Related Repositories

- **Portfolio Showcase:** https://franzenjb.github.io/portfolio-showcase/ (merged into this tool)
- **ALICE Master Database:** https://github.com/franzenjb/alice_master_database (poverty data)
- **County Consolidation Tool:** ~/county-consolidation-tool/ (data processing scripts)

## 📞 Support

Issues? Questions? Please open an issue on GitHub:
https://github.com/franzenjb/GeoJSON-Creation-Tool/issues

---

**Made with ❤️ for the American Red Cross**

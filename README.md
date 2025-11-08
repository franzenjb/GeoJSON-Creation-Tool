# GeoJSON Creation Tool

A beautiful, interactive web application for creating multi-level GeoJSON files from CSV data. Transform your geographic data into professional GeoJSON files at multiple aggregation levels (ZIP → County → Chapter → Region → Division).

## 🎯 Features

- **Interactive Web Interface** - Beautiful, modern UI with American Red Cross branding
- **Multi-Level Processing** - Create GeoJSON files at ZIP, County, Chapter, Region, and Division levels
- **Automatic Boundary Download** - Fetches boundaries from US Census Bureau automatically
- **Drag & Drop Upload** - Easy CSV file upload
- **Real-Time Progress** - See processing status in real-time
- **Download Ready** - Get your GeoJSON files instantly

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements-web.txt
```

### Run the Application

```bash
python3 app.py
```

Then open http://localhost:5000 in your browser.

## 📋 Requirements

Your CSV file should have:
- ZIP code column (`Zip`, `ZIP`, or `zip`)
- FIPS code column (`FIPS` or `fips`)
- Geographic hierarchy columns (`County`, `Chapter`, `Region`, `Division`)
- Data columns (years, totals, metrics)

## 🎨 Usage

1. **Upload CSV** - Drag and drop or click to upload your CSV file
2. **Select Levels** - Choose which GeoJSON levels you want to create
3. **Process** - Click "Create GeoJSON Files" and wait for processing
4. **Download** - Download your generated GeoJSON files

## 📁 Repository Structure

```
geojson-pipeline-repo/
├── index.html              # Beautiful web interface
├── app.py                  # Flask backend server
├── requirements-web.txt    # Python dependencies
├── scripts/
│   ├── create_geojson_levels.py  # Creates county/chapter/region/division GeoJSON
│   └── create_zip_geojson.py     # Creates ZIP code GeoJSON
└── docs/
    ├── PROCESS.md         # Detailed process documentation
    └── RESOURCES.md       # Data sources and references
```

## 🔧 How It Works

1. **Load CSV Data** - Reads your CSV with geographic identifiers
2. **Download Boundaries** - Fetches county and ZIP boundaries from Census Bureau
3. **Join Data** - Matches your data to geographic boundaries
4. **Aggregate** - Creates aggregated data at each geographic level
5. **Dissolve Boundaries** - Merges boundaries for chapters/regions/divisions
6. **Export GeoJSON** - Saves ready-to-use GeoJSON files

## 📦 Output Files

- `biomed_zip_codes.geojson` - ZIP code level (all fields)
- `biomed_counties.geojson` - County level (aggregated)
- `biomed_chapters.geojson` - Chapter level (dissolved boundaries)
- `biomed_regions.geojson` - Region level (dissolved boundaries)
- `biomed_divisions.geojson` - Division level (dissolved boundaries)

## 🛠️ Technologies

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: Flask (Python)
- **Data Processing**: GeoPandas, Pandas
- **Boundaries**: US Census Bureau Cartographic Boundary Files

## 📄 License

This tool uses public domain data from the US Census Bureau. Scripts are provided as-is for reuse.

## 🙏 Credits

- US Census Bureau for boundary data
- American Red Cross for inspiration
- GeoPandas and Pandas communities

# Documentation Index

## 📚 Documentation Files

### Getting Started
- **[README.md](README.md)** - Start here! Overview, quick start, and key concepts
- **[SUMMARY.md](SUMMARY.md)** - Quick reference of what we learned and resources used
- **[USAGE.md](USAGE.md)** - Step-by-step usage guide with examples

### Detailed Documentation
- **[docs/PROCESS.md](docs/PROCESS.md)** - Detailed technical process explanation (step-by-step)
- **[docs/RESOURCES.md](docs/RESOURCES.md)** - Complete resource reference (data sources, libraries, URLs)

## 🛠️ Scripts

- **[scripts/create_geojson_levels.py](scripts/create_geojson_levels.py)** - Creates county/chapter/region/division GeoJSON
- **[scripts/create_zip_geojson.py](scripts/create_zip_geojson.py)** - Creates ZIP code GeoJSON with all fields

## 📋 Quick Navigation

### I want to...

**...understand what this does:**
→ Read [README.md](README.md)

**...use this for my data:**
→ Read [USAGE.md](USAGE.md)

**...understand how it works:**
→ Read [docs/PROCESS.md](docs/PROCESS.md)

**...find data sources:**
→ Read [docs/RESOURCES.md](docs/RESOURCES.md)

**...quick reference:**
→ Read [SUMMARY.md](SUMMARY.md)

**...customize the scripts:**
→ Read [USAGE.md](USAGE.md) → Customization section

## 🔑 Key Concepts

### Process Flow
1. Load CSV → 2. Download Boundaries → 3. Join Data → 4. Aggregate → 5. Dissolve → 6. Export

### Geographic Levels
ZIP → County → Chapter → Region → Division

### Key Operations
- `dissolve()` - Merge boundaries
- `merge()` - Join data
- `groupby().agg()` - Aggregate data
- `simplify()` - Reduce file size

### Data Sources
- Census Bureau (counties, ZIP codes)
- Esri Living Atlas (fallback)

## 📦 Files Created

When you run the scripts, you'll get:
- `biomed_zip_codes.geojson` (ZIP level)
- `biomed_counties.geojson` (County level)
- `biomed_chapters.geojson` (Chapter level)
- `biomed_regions.geojson` (Region level)
- `biomed_divisions.geojson` (Division level)

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Update CSV file path in scripts

# 3. Run scripts
python3 scripts/create_geojson_levels.py
python3 scripts/create_zip_geojson.py

# 4. Find output in geojson_output/
```

## 📖 Reading Order

**First time user:**
1. README.md
2. USAGE.md
3. Run scripts with your data

**Want to understand deeply:**
1. README.md
2. docs/PROCESS.md
3. docs/RESOURCES.md

**Quick reference:**
1. SUMMARY.md
2. INDEX.md (this file)


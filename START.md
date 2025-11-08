# 🚀 Quick Start Guide

## Start the Web Application

### 1. Install Dependencies

```bash
pip install -r requirements-web.txt
```

### 2. Run the Application

```bash
python3 app.py
```

### 3. Open in Browser

Open http://localhost:5000 in your web browser

## How to Use

1. **Upload CSV**: Drag and drop or click to upload your CSV file
2. **Select Levels**: Choose which GeoJSON levels you want (ZIP, County, Chapter, Region, Division)
3. **Process**: Click "Create GeoJSON Files" and wait for processing
4. **Download**: Click download buttons to get your GeoJSON files

## Requirements

Your CSV should have:
- ZIP code column (named `Zip`, `ZIP`, or `zip`)
- FIPS code column (named `FIPS` or `fips`)
- Geographic hierarchy columns (`County`, `Chapter`, `Region`, `Division`)
- Data columns (years, totals, metrics)

## Troubleshooting

**Port already in use?**
- Change port in `app.py`: `app.run(debug=True, port=5001)`

**Scripts not found?**
- Make sure `scripts/` folder exists with the Python scripts

**Processing fails?**
- Check that your CSV has the required columns
- Check the terminal for error messages
- Make sure you have internet connection (for downloading boundaries)

## What Gets Created

- `uploads/` - Your uploaded CSV files
- `outputs/` - Generated GeoJSON files organized by session


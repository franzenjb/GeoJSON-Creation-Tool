#!/usr/bin/env python3
"""
Flask backend for GeoJSON Pipeline Web App
Handles file uploads and processes CSV files using the pipeline scripts
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import tempfile
import shutil
import subprocess
import json
from pathlib import Path
import pandas as pd

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'csv'}

# Create folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_file('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle CSV file upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only CSV files are allowed'}), 400
    
    # Save uploaded file
    filename = file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    # Get file info
    file_size = os.path.getsize(filepath)
    
    return jsonify({
        'success': True,
        'filename': filename,
        'size': file_size,
        'message': 'File uploaded successfully'
    })

@app.route('/api/process', methods=['POST'])
def process_file():
    """Process CSV file and generate GeoJSON files"""
    data = request.json
    filename = data.get('filename')
    levels = data.get('levels', [])
    
    if not filename:
        return jsonify({'error': 'No filename provided'}), 400
    
    if not levels:
        return jsonify({'error': 'No levels selected'}), 400
    
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    # Create temporary directory for this processing session
    session_id = f"session_{hash(filename)}"
    temp_dir = os.path.join(OUTPUT_FOLDER, session_id)
    os.makedirs(temp_dir, exist_ok=True)
    
    # Copy CSV to temp directory
    temp_csv = os.path.join(temp_dir, filename)
    shutil.copy(filepath, temp_csv)
    
    # Copy scripts to temp directory
    scripts_dir = Path(__file__).parent / 'scripts'
    for script in ['create_geojson_levels.py', 'create_zip_geojson.py']:
        script_path = scripts_dir / script
        if script_path.exists():
            shutil.copy(script_path, temp_dir)
    
    # Modify scripts to use temp CSV
    modify_scripts_for_processing(temp_dir, filename)
    
    generated_files = []
    
    try:
        # Process each selected level
        for level in levels:
            result = process_level(level, temp_dir, temp_csv)
            if result:
                generated_files.append(result)
        
        return jsonify({
            'success': True,
            'files': generated_files,
            'message': f'Successfully generated {len(generated_files)} GeoJSON files'
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Error processing file'
        }), 500

def modify_scripts_for_processing(temp_dir, csv_filename):
    """Modify Python scripts to use the uploaded CSV"""
    scripts = ['create_geojson_levels.py', 'create_zip_geojson.py']
    
    for script_name in scripts:
        script_path = os.path.join(temp_dir, script_name)
        if os.path.exists(script_path):
            with open(script_path, 'r') as f:
                content = f.read()
            
            # Replace CSV file path
            content = content.replace(
                'CSV_FILE = DATA_DIR / "Biomed by zip code_ENHANCED.csv"',
                f'CSV_FILE = DATA_DIR / "{csv_filename}"'
            )
            
            # Update output directory
            content = content.replace(
                'OUTPUT_DIR = DATA_DIR / "geojson_output"',
                'OUTPUT_DIR = DATA_DIR / "geojson_output"'
            )
            
            with open(script_path, 'w') as f:
                f.write(content)

def process_level(level, temp_dir, csv_path):
    """Process a specific geographic level"""
    # All levels use create_geojson_levels.py except zip which uses create_zip_geojson.py
    if level == 'zip':
        script_name = 'create_zip_geojson.py'
    else:
        script_name = 'create_geojson_levels.py'
    
    script_path = os.path.join(temp_dir, script_name)
    output_dir = os.path.join(temp_dir, 'geojson_output')
    os.makedirs(output_dir, exist_ok=True)
    
    # Change to temp directory and run script
    original_dir = os.getcwd()
    try:
        os.chdir(temp_dir)
        
        # Run the Python script
        result = subprocess.run(
            ['python3', script_name],
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout (ZIP processing can take time)
        )
        
        if result.returncode != 0:
            print(f"Script output: {result.stdout}")
            print(f"Script error: {result.stderr}")
            raise Exception(f"Script failed: {result.stderr[:500]}")
        
        # Find generated file based on level
        expected_filenames = {
            'zip': 'biomed_zip_codes.geojson',
            'county': 'biomed_counties.geojson',
            'chapter': 'biomed_chapters.geojson',
            'region': 'biomed_regions.geojson',
            'division': 'biomed_divisions.geojson'
        }
        
        expected_filename = expected_filenames.get(level)
        filepath = os.path.join(output_dir, expected_filename)
        
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            # Return relative path from OUTPUT_FOLDER for download
            rel_path = os.path.relpath(filepath, OUTPUT_FOLDER)
            return {
                'level': level,
                'filename': expected_filename,
                'size': file_size,
                'path': rel_path
            }
        else:
            # Try to find any geojson file that was created
            geojson_files = list(Path(output_dir).glob('*.geojson'))
            if geojson_files:
                # Find the one matching our level
                for gf in geojson_files:
                    if level in str(gf).lower():
                        filepath = str(gf)
                        file_size = os.path.getsize(filepath)
                        rel_path = os.path.relpath(filepath, OUTPUT_FOLDER)
                        return {
                            'level': level,
                            'filename': os.path.basename(filepath),
                            'size': file_size,
                            'path': rel_path
                        }
                # If no match, return first one
                filepath = str(geojson_files[0])
                file_size = os.path.getsize(filepath)
                rel_path = os.path.relpath(filepath, OUTPUT_FOLDER)
                return {
                    'level': level,
                    'filename': os.path.basename(filepath),
                    'size': file_size,
                    'path': rel_path
                }
            else:
                raise Exception(f"No GeoJSON file was generated for {level}")
    
    finally:
        os.chdir(original_dir)
    
    return None

@app.route('/api/download/<path:filepath>')
def download_file(filepath):
    """Download generated GeoJSON file"""
    # filepath comes as: session_id/filename or session_id/geojson_output/filename
    full_path = os.path.join(OUTPUT_FOLDER, filepath)
    
    # Normalize path to prevent directory traversal
    full_path = os.path.normpath(full_path)
    if not full_path.startswith(os.path.abspath(OUTPUT_FOLDER)):
        return jsonify({'error': 'Invalid path'}), 400
    
    if not os.path.exists(full_path):
        return jsonify({'error': 'File not found'}), 404
    
    filename = os.path.basename(full_path)
    return send_file(full_path, as_attachment=True, download_name=filename)

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'GeoJSON Pipeline API is running'})

if __name__ == '__main__':
    print("Starting GeoJSON Pipeline Web App...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, port=5000)


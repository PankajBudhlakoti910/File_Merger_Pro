from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import numpy as np
import os
import io
import base64
from datetime import datetime
import warnings
from werkzeug.utils import secure_filename

warnings.filterwarnings('ignore')

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], mode=0o777, exist_ok=True)

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'json', 'txt'}

def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_file(file_path, filename):
    """Read uploaded file"""
    try:
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext == '.csv':
            return pd.read_csv(file_path)
        elif file_ext in ['.xlsx', '.xls']:
            return pd.read_excel(file_path)
        elif file_ext == '.json':
            return pd.read_json(file_path)
        elif file_ext == '.txt':
            # Try different separators
            try:
                return pd.read_csv(file_path, sep=',')
            except:
                try:
                    return pd.read_csv(file_path, sep='\t')
                except:
                    return pd.read_csv(file_path, sep=None, engine='python')
        else:
            # Try CSV first
            try:
                return pd.read_csv(file_path)
            except:
                try:
                    return pd.read_excel(file_path)
                except:
                    return pd.read_csv(file_path, sep=None, engine='python')
                    
    except Exception as e:
        return None

def prepare_download_data(df, file_format):
    """Prepare data for download"""
    try:
        if file_format == 'csv':
            output = io.StringIO()
            df.to_csv(output, index=False, encoding='utf-8')
            return {
                'data': output.getvalue(),
                'mime_type': 'text/csv',
                'file_extension': 'csv'
            }
            
        elif file_format == 'excel':
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='MergedData')
            output.seek(0)
            return {
                'data': output.getvalue(),
                'mime_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'file_extension': 'xlsx'
            }
            
        elif file_format == 'json':
            return {
                'data': df.to_json(orient='records', indent=2, force_ascii=False),
                'mime_type': 'application/json',
                'file_extension': 'json'
            }
        
        return None
            
    except Exception as e:
        return None

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload():
    """Handle file uploads"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        
        if not files or files[0].filename == '':
            return jsonify({'error': 'No files selected'}), 400
        
        uploaded_files = []
        
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                uploaded_files.append({
                    'name': filename,
                    'size': os.path.getsize(filepath),
                    'path': filepath
                })
        
        if not uploaded_files:
            return jsonify({'error': 'No valid files uploaded'}), 400
        
        return jsonify({
            'success': True,
            'message': f'{len(uploaded_files)} files uploaded successfully',
            'files': uploaded_files
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/merge', methods=['POST'])
def merge():
    """Handle file merging"""
    try:
        data = request.get_json()
        
        file_paths = data.get('file_paths', [])
        merge_method = data.get('merge_method', 'Append Rows (Common Columns Only)')
        add_source = data.get('add_source', True)
        handle_duplicates = data.get('handle_duplicates', 'Remove Exact Duplicates')
        
        if not file_paths:
            return jsonify({'error': 'No files provided'}), 400
        
        # Read all files
        dataframes = []
        for filepath in file_paths:
            filename = os.path.basename(filepath)
            df = read_file(filepath, filename)
            if df is not None:
                if add_source:
                    df['_source_file'] = filename
                dataframes.append(df)
        
        if not dataframes:
            return jsonify({'error': 'No valid files could be read'}), 400
        
        # Merge based on method
        if "Common Columns" in merge_method:
            common_cols = set(dataframes[0].columns)
            for df in dataframes[1:]:
                common_cols = common_cols.intersection(set(df.columns))
            
            if add_source and '_source_file' in common_cols:
                common_cols.discard('_source_file')
            
            common_cols = list(common_cols)
            
            aligned_dfs = []
            for df in dataframes:
                cols_to_keep = [col for col in common_cols if col in df.columns]
                if add_source and '_source_file' in df.columns:
                    cols_to_keep.append('_source_file')
                aligned_dfs.append(df[cols_to_keep].copy())
            
            merged_df = pd.concat(aligned_dfs, ignore_index=True)
        
        elif "All Columns" in merge_method:
            merged_df = pd.concat(dataframes, ignore_index=True, sort=False)
        
        else:
            merged_df = pd.concat(dataframes, ignore_index=True)
        
        # Handle duplicates
        if handle_duplicates == "Remove Exact Duplicates":
            merged_df = merged_df.drop_duplicates()
        elif handle_duplicates == "Keep First":
            merged_df = merged_df.drop_duplicates(keep='first')
        elif handle_duplicates == "Keep Last":
            merged_df = merged_df.drop_duplicates(keep='last')
        
        # Store in session (in production, use database or cache)
        merged_data_json = merged_df.head(1000).to_json(orient='records')
        
        return jsonify({
            'success': True,
            'message': 'Files merged successfully',
            'stats': {
                'rows': len(merged_df),
                'columns': len(merged_df.columns),
                'files_merged': len(dataframes)
            },
            'preview': merged_df.head(20).to_dict('records'),
            'merged_data': base64.b64encode(merged_df.to_csv(index=False).encode()).decode()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download', methods=['POST'])
def download():
    """Handle file download"""
    try:
        data = request.get_json()
        
        merged_data_b64 = data.get('merged_data')
        filename = data.get('filename', 'merged_data')
        file_format = data.get('format', 'csv')
        
        if not merged_data_b64:
            return jsonify({'error': 'No data to download'}), 400
        
        # Decode merged data
        csv_data = base64.b64decode(merged_data_b64).decode()
        df = pd.read_csv(io.StringIO(csv_data))
        
        # Prepare download
        download_info = prepare_download_data(df, file_format)
        
        if not download_info:
            return jsonify({'error': 'Failed to prepare download'}), 500
        
        file_extension = download_info['file_extension']
        download_filename = f"{filename}.{file_extension}"
        
        return jsonify({
            'success': True,
            'filename': download_filename,
            'data': download_info['data'] if isinstance(download_info['data'], str) else base64.b64encode(download_info['data']).decode(),
            'mime_type': download_info['mime_type']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=3000)

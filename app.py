import streamlit as st
import pandas as pd
import numpy as np
import os
import time
from datetime import datetime
import io
import base64
import warnings
warnings.filterwarnings('ignore')

# Set page configuration
st.set_page_config(
    page_title="📊 File Merger Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    
    .success-toast {
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #10B981, #059669);
        color: white;
        padding: 15px 25px;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
        z-index: 9999;
        animation: slideIn 0.5s ease, fadeOut 0.5s ease 2s forwards;
        font-weight: bold;
    }
    
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes fadeOut {
        from { opacity: 1; }
        to { opacity: 0; }
    }
    
    .step-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #3B82F6;
        margin-bottom: 1.5rem;
    }
    
    .download-btn {
        background: linear-gradient(135deg, #10B981, #059669);
        color: white;
        padding: 12px 24px;
        border-radius: 8px;
        border: none;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        text-decoration: none;
        display: inline-block;
        transition: all 0.3s ease;
    }
    
    .download-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
    }
</style>
""", unsafe_allow_html=True)

class FileMergerApp:
    def __init__(self):
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'uploaded_files' not in st.session_state:
            st.session_state.uploaded_files = []
        if 'merged_data' not in st.session_state:
            st.session_state.merged_data = None
        if 'step' not in st.session_state:
            st.session_state.step = 1
        if 'show_success' not in st.session_state:
            st.session_state.show_success = False
        if 'success_message' not in st.session_state:
            st.session_state.success_message = ""
        if 'processing' not in st.session_state:
            st.session_state.processing = False
        if 'download_ready' not in st.session_state:
            st.session_state.download_ready = False
        if 'download_data' not in st.session_state:
            st.session_state.download_data = None
    
    def show_success_toast(self, message):
        """Show success toast"""
        toast_html = f"""
        <div class="success-toast">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.5rem;">✅</span>
                <span>{message}</span>
            </div>
        </div>
        """
        st.markdown(toast_html, unsafe_allow_html=True)
        # Use a placeholder to clear after 2 seconds
        toast_placeholder = st.empty()
        toast_placeholder.markdown(toast_html, unsafe_allow_html=True)
        time.sleep(2)
        toast_placeholder.empty()
    
    def prepare_download_data(self, df, file_format):
        """Prepare data for download"""
        try:
            if file_format == 'csv':
                # Convert to CSV
                csv = df.to_csv(index=False, encoding='utf-8-sig')
                b64 = base64.b64encode(csv.encode('utf-8-sig')).decode()
                mime_type = 'text/csv'
                file_extension = 'csv'
                
            elif file_format == 'excel':
                # Convert to Excel
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='MergedData')
                output.seek(0)
                b64 = base64.b64encode(output.read()).decode()
                mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                file_extension = 'xlsx'
                
            elif file_format == 'json':
                # Convert to JSON
                json_str = df.to_json(orient='records', indent=2, force_ascii=False)
                b64 = base64.b64encode(json_str.encode('utf-8')).decode()
                mime_type = 'application/json'
                file_extension = 'json'
            
            return {
                'b64': b64,
                'mime_type': mime_type,
                'file_extension': file_extension,
                'size': len(df)
            }
            
        except Exception as e:
            st.error(f"Error preparing download: {str(e)}")
            return None
    
    def read_file(self, uploaded_file):
        """Read uploaded file"""
        try:
            filename = uploaded_file.name
            file_ext = os.path.splitext(filename)[1].lower()
            
            if file_ext == '.csv':
                return pd.read_csv(uploaded_file)
            elif file_ext in ['.xlsx', '.xls']:
                return pd.read_excel(uploaded_file)
            elif file_ext == '.json':
                return pd.read_json(uploaded_file)
            elif file_ext == '.txt':
                content = uploaded_file.getvalue().decode('utf-8')
                # Try different separators
                try:
                    return pd.read_csv(io.StringIO(content), sep=',')
                except:
                    try:
                        return pd.read_csv(io.StringIO(content), sep='\t')
                    except:
                        return pd.read_csv(io.StringIO(content), sep=None, engine='python')
            else:
                # Try CSV first
                try:
                    return pd.read_csv(uploaded_file)
                except:
                    # Try Excel
                    try:
                        return pd.read_excel(uploaded_file)
                    except:
                        # Read as text
                        content = uploaded_file.getvalue().decode('utf-8')
                        return pd.read_csv(io.StringIO(content), sep=None, engine='python')
                        
        except Exception as e:
            st.warning(f"Could not read {filename}: {str(e)}")
            return None
    
    def render_step_indicator(self):
        """Render step indicator"""
        steps = [
            ("📁 Upload", 1),
            ("⚙️ Configure", 2),
            ("💾 Download", 3)
        ]
        
        cols = st.columns(len(steps))
        for idx, (step_name, step_num) in enumerate(steps):
            with cols[idx]:
                is_active = st.session_state.step == step_num
                is_completed = st.session_state.step > step_num
                
                if is_active:
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #3B82F6, #8B5CF6);
                        color: white;
                        padding: 10px;
                        border-radius: 8px;
                        text-align: center;
                        font-weight: bold;
                        margin: 5px;
                    ">
                        {step_name}
                    </div>
                    """, unsafe_allow_html=True)
                elif is_completed:
                    st.markdown(f"""
                    <div style="
                        background: #10B981;
                        color: white;
                        padding: 10px;
                        border-radius: 8px;
                        text-align: center;
                        font-weight: bold;
                        margin: 5px;
                    ">
                        ✅ {step_name}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="
                        background: #E5E7EB;
                        color: #6B7280;
                        padding: 10px;
                        border-radius: 8px;
                        text-align: center;
                        font-weight: bold;
                        margin: 5px;
                    ">
                        {step_name}
                    </div>
                    """, unsafe_allow_html=True)
    
    def render_step1_upload(self):
        """Render Step 1: Upload Files"""
        st.markdown("""
        <div class="step-card">
            <h2 style="margin-top: 0; color: #1E40AF;">📁 STEP 1: UPLOAD FILES</h2>
            <p>Select 30-40 files with similar column names</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            "Choose files (CSV, Excel, JSON, TXT)",
            type=['csv', 'xlsx', 'xls', 'txt', 'json'],
            accept_multiple_files=True,
            key="file_uploader"
        )
        
        if uploaded_files:
            st.session_state.uploaded_files = uploaded_files
            
            with st.spinner("Processing uploaded files..."):
                time.sleep(0.5)
            
            st.success(f"✅ {len(uploaded_files)} files uploaded successfully!")
            
            with st.expander(f"📋 Uploaded Files ({len(uploaded_files)})", expanded=True):
                for idx, file in enumerate(uploaded_files, 1):
                    file_size = file.size / 1024  # KB
                    st.write(f"**{idx}. {file.name}** ({file_size:.1f} KB)")
            
            if st.button("Next: Configure Merge →", type="primary", use_container_width=True):
                st.session_state.step = 2
                st.rerun()
            
            return True
        
        return False
    
    def render_step2_configure(self):
        """Render Step 2: Configure Merge"""
        st.markdown("""
        <div class="step-card">
            <h2 style="margin-top: 0; color: #059669;">⚙️ STEP 2: CONFIGURE MERGE</h2>
            <p>Choose how to merge your files</p>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.uploaded_files:
            st.error("❌ No files uploaded. Please go back to Step 1.")
            if st.button("← Back to Upload", type="secondary"):
                st.session_state.step = 1
                st.rerun()
            return False
        
        st.info(f"📁 Ready to merge {len(st.session_state.uploaded_files)} files")
        
        col1, col2 = st.columns(2)
        
        with col1:
            merge_method = st.selectbox(
                "**Merge Method**",
                options=[
                    "Append Rows (Common Columns Only)",
                    "Append Rows (All Columns)",
                    "Smart Merge"
                ],
                index=0
            )
        
        with col2:
            add_source = st.checkbox(
                "Add Source File Column",
                value=True
            )
        
        with st.expander("⚙️ Advanced Options"):
            handle_duplicates = st.selectbox(
                "Handle Duplicates",
                ["Keep All", "Remove Exact Duplicates", "Keep First", "Keep Last"],
                index=1
            )
        
        if st.button("🚀 START MERGING FILES", type="primary", use_container_width=True):
            self.process_merge(merge_method, add_source, handle_duplicates)
        
        if st.button("← Back to Upload", type="secondary"):
            st.session_state.step = 1
            st.rerun()
        
        return True
    
    def process_merge(self, merge_method, add_source, handle_duplicates):
        """Process file merging"""
        with st.spinner("🔄 Merging files..."):
            try:
                # Read all files
                dataframes = []
                for file in st.session_state.uploaded_files:
                    df = self.read_file(file)
                    if df is not None:
                        if add_source:
                            df['_source_file'] = file.name
                        dataframes.append(df)
                
                if not dataframes:
                    st.error("❌ No valid files could be read")
                    return
                
                # Merge based on method
                if "Common Columns" in merge_method:
                    common_cols = set(dataframes[0].columns)
                    for df in dataframes[1:]:
                        common_cols = common_cols.intersection(set(df.columns))
                    
                    if add_source and '_source_file' in common_cols:
                        common_cols.remove('_source_file')
                    
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
                
                # Store merged data
                st.session_state.merged_data = merged_df
                st.session_state.step = 3
                
                # Show success
                st.success("✅ Files merged successfully!")
                st.balloons()
                
                # Rerun to show step 3
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error merging files: {str(e)}")
    
    def render_step3_download(self):
        """Render Step 3: Download"""
        st.markdown("""
        <div class="step-card">
            <h2 style="margin-top: 0; color: #D97706;">💾 STEP 3: DOWNLOAD MERGED FILE</h2>
            <p>Configure and download your merged dataset</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.merged_data is None:
            st.error("❌ No merged data found.")
            if st.button("← Back to Configure", type="secondary"):
                st.session_state.step = 2
                st.rerun()
            return
        
        # Show statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Rows", f"{len(st.session_state.merged_data):,}")
        with col2:
            st.metric("Total Columns", len(st.session_state.merged_data.columns))
        with col3:
            st.metric("Files Merged", len(st.session_state.uploaded_files))
        
        # Configuration
        col1, col2 = st.columns(2)
        
        with col1:
            filename = st.text_input(
                "Filename",
                value=f"merged_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
        
        with col2:
            file_format = st.selectbox(
                "Format",
                options=['csv', 'excel', 'json'],
                index=0
            )
        
        # Preview
        with st.expander("👁️ Preview Data", expanded=True):
            st.dataframe(st.session_state.merged_data.head(20), use_container_width=True)
        
        # Download section
        st.markdown("---")
        st.markdown("### 📥 Download Your File")
        
        # Create download button
        download_placeholder = st.empty()
        
        if st.button("⬇️ PREPARE DOWNLOAD", type="primary", use_container_width=True):
            with st.spinner("🔄 Preparing download..."):
                time.sleep(1)
                
                # Prepare download data
                download_info = self.prepare_download_data(
                    st.session_state.merged_data,
                    file_format
                )
                
                if download_info:
                    # Create download link
                    file_extension = download_info['file_extension']
                    download_filename = f"{filename}.{file_extension}"
                    
                    # Store download data in session state
                    st.session_state.download_ready = True
                    st.session_state.download_filename = download_filename
                    st.session_state.download_b64 = download_info['b64']
                    st.session_state.download_mime = download_info['mime_type']
                    
                    st.success(f"✅ {download_filename} ready for download!")
                    
                    # Create and display download link
                    download_link = f"""
                    <a href="data:{download_info['mime_type']};base64,{download_info['b64']}" 
                       download="{download_filename}"
                       style="text-decoration: none;">
                        <button class="download-btn">
                            📥 CLICK TO DOWNLOAD<br>
                            <small>{download_filename}</small>
                        </button>
                    </a>
                    """
                    
                    download_placeholder.markdown(download_link, unsafe_allow_html=True)
        
        # Back button
        if st.button("← Back to Configure", type="secondary"):
            st.session_state.step = 2
            st.rerun()
    
    def render_sidebar(self):
        """Render sidebar"""
        with st.sidebar:
            st.markdown("""
            <div style="text-align: center;">
                <h2>🚀 Quick Guide</h2>
                <hr>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            **3 Simple Steps:**
            1. Upload Files
            2. Configure Merge
            3. Download
            
            ---
            
            **📁 Supported Formats:**
            - CSV (.csv)
            - Excel (.xlsx, .xls)
            - JSON (.json)
            - Text (.txt)
            
            ---
            
            **Perfect for merging 30-40 files**
            """)
            
            if st.button("🔄 Reset Application", use_container_width=True, type="secondary"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
    
    def run(self):
        """Main application runner"""
        # Header
        st.markdown('<h1 class="main-header">📊 File Merger Pro</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; color: #6B7280;">Merge 30-40 files with similar columns</p>', unsafe_allow_html=True)
        
        # Step indicator
        self.render_step_indicator()
        
        # Render current step
        if st.session_state.step == 1:
            self.render_step1_upload()
        elif st.session_state.step == 2:
            self.render_step2_configure()
        elif st.session_state.step == 3:
            self.render_step3_download()
        
        # Render sidebar
        self.render_sidebar()
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #6B7280; padding: 1rem;">
            <p>Merge unlimited files effortlessly • Perfect for handling 30-40 files with similar columns</p>
        </div>
        """, unsafe_allow_html=True)

def main():
    app = FileMergerApp()
    app.run()

if __name__ == "__main__":
    main()
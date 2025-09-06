import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import io
from typing import List, Dict, Tuple
import re

# Configure page
st.set_page_config(
    page_title="Occupation Automation Probability Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .occupation-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e1e5e9;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .occupation-card:hover {
        border-color: #1f77b4;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .selected-occupation {
        border-color: #1f77b4;
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and cache the probability data"""
    import os
    import glob
    
    # Get current directory
    current_dir = os.getcwd()
    
    # List all files in current directory for debugging
    all_files = os.listdir(current_dir)
    excel_files = [f for f in all_files if f.endswith(('.xlsx', '.xls'))]
    
    # Debug information
    st.sidebar.markdown("### 🔍 Debug Info")
    st.sidebar.write(f"Current directory: `{current_dir}`")
    st.sidebar.write(f"All files found: {len(all_files)}")
    st.sidebar.write("Excel files found:")
    for f in excel_files:
        st.sidebar.write(f"- `{f}`")
    
    # Try different possible file names and locations
    possible_cdf_names = [
        "Probas CDFs.xlsx",
        "Probas_CDFs.xlsx", 
        "probas cdfs.xlsx",
        "probas_cdfs.xlsx",
        "PROBAS CDFS.xlsx"
    ]
    
    possible_pdf_names = [
        "Probas PDFs.xlsx",
        "Probas_PDFs.xlsx",
        "probas pdfs.xlsx", 
        "probas_pdfs.xlsx",
        "PROBAS PDFS.xlsx"
    ]
    
    cdf_file = None
    pdf_file = None
    
    # Find CDF file
    for name in possible_cdf_names:
        if os.path.exists(name):
            cdf_file = name
            break
    
    # Find PDF file  
    for name in possible_pdf_names:
        if os.path.exists(name):
            pdf_file = name
            break
    
    # If exact names not found, try pattern matching
    if not cdf_file:
        cdf_matches = [f for f in excel_files if 'cdf' in f.lower()]
        if cdf_matches:
            cdf_file = cdf_matches[0]
    
    if not pdf_file:
        pdf_matches = [f for f in excel_files if 'pdf' in f.lower()]
        if pdf_matches:
            pdf_file = pdf_matches[0]
    
    # Show what files we're trying to load
    st.sidebar.write("Attempting to load:")
    st.sidebar.write(f"CDF file: `{cdf_file if cdf_file else 'NOT FOUND'}`")
    st.sidebar.write(f"PDF file: `{pdf_file if pdf_file else 'NOT FOUND'}`")
    
    try:
        if not cdf_file or not pdf_file:
            missing_files = []
            if not cdf_file:
                missing_files.append("CDF file")
            if not pdf_file:
                missing_files.append("PDF file")
            
            st.error(f"⚠️ Could not find {' and '.join(missing_files)}.")
            st.error("**Available Excel files:**")
            if excel_files:
                for f in excel_files:
                    st.error(f"- {f}")
            else:
                st.error("No Excel files found in the current directory.")
            st.error("**Please check:**")
            st.error("1. File names are exactly correct")
            st.error("2. Files are in the same folder as app.py") 
            st.error("3. Files are not corrupted")
            return None, None
        
        # Try to load the files
        cdf_data = pd.read_excel(cdf_file)
        pdf_data = pd.read_excel(pdf_file)
        
        st.sidebar.success(f"✅ Successfully loaded {len(cdf_data)} occupations!")
        
        return cdf_data, pdf_data
        
    except Exception as e:
        st.error(f"❌ Error loading data files: {str(e)}")
        st.error("**Possible solutions:**")
        st.error("1. Make sure the Excel files are not open in another program")
        st.error("2. Check if files are corrupted")
        st.error("3. Verify file permissions")
        return None, None

def search_occupations(data: pd.DataFrame, search_term: str) -> pd.DataFrame:
    """Search occupations by SOC code or title (fuzzy matching)"""
    if not search_term:
        return data
    
    search_term = search_term.lower()
    
    # Search in both SOC code and title columns
    soc_matches = data.iloc[:, 0].astype(str).str.lower().str.contains(search_term, na=False)
    title_matches = data.iloc[:, 1].astype(str).str.lower().str.contains(search_term, na=False)
    
    return data[soc_matches | title_matches]

def create_probability_plots(selected_occupations: List[Dict], cdf_data: pd.DataFrame, pdf_data: pd.DataFrame):
    """Create CDF and PDF plots for selected occupations"""
    if not selected_occupations:
        return None, None
    
    # Prepare data for plotting
    years = list(range(2017, 2087))
    
    # Create CDF plot
    fig_cdf = go.Figure()
    
    # Create PDF plot  
    fig_pdf = go.Figure()
    
    colors = px.colors.qualitative.Set3
    
    for i, occ in enumerate(selected_occupations):
        color = colors[i % len(colors)]
        
        # Find the occupation in both datasets
        cdf_row = cdf_data[cdf_data.iloc[:, 1] == occ['title']]
        pdf_row = pdf_data[pdf_data.iloc[:, 1] == occ['title']]
        
        if not cdf_row.empty:
            # CDF data (skip first two columns: SOC code and title)
            cdf_values = cdf_row.iloc[0, 2:].values
            fig_cdf.add_trace(go.Scatter(
                x=years,
                y=cdf_values,
                mode='lines+markers',
                name=f"{occ['title'][:30]}..." if len(occ['title']) > 30 else occ['title'],
                line=dict(color=color, width=3),
                marker=dict(size=6),
                hovertemplate=f"<b>{occ['title']}</b><br>Year: %{{x}}<br>Cumulative Probability: %{{y:.4f}}<extra></extra>"
            ))
        
        if not pdf_row.empty:
            # PDF data (skip first two columns: SOC code and title)  
            pdf_values = pdf_row.iloc[0, 2:].values
            fig_pdf.add_trace(go.Scatter(
                x=years[1:],  # PDF starts from 2018
                y=pdf_values,
                mode='lines+markers',
                name=f"{occ['title'][:30]}..." if len(occ['title']) > 30 else occ['title'],
                line=dict(color=color, width=3),
                marker=dict(size=6),
                hovertemplate=f"<b>{occ['title']}</b><br>Year: %{{x}}<br>Probability: %{{y:.4f}}<extra></extra>"
            ))
    
    # Update CDF layout
    fig_cdf.update_layout(
        title={
            'text': "Cumulative Distribution Function (CDF) - Automation Probability Over Time",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#1f77b4'}
        },
        xaxis_title="Year",
        yaxis_title="Cumulative Probability",
        height=500,
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    # Update PDF layout
    fig_pdf.update_layout(
        title={
            'text': "Probability Density Function (PDF) - Annual Automation Probability",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#ff7f0e'}
        },
        xaxis_title="Year",
        yaxis_title="Annual Probability",
        height=500,
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    return fig_cdf, fig_pdf

def export_data(data: pd.DataFrame, filename: str, file_format: str):
    """Export data to CSV or Excel format"""
    buffer = io.BytesIO()
    
    if file_format.lower() == 'csv':
        csv_data = data.to_csv(index=False)
        return csv_data.encode('utf-8'), f"{filename}.csv", "text/csv"
    else:
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            data.to_excel(writer, sheet_name='Data', index=False)
        return buffer.getvalue(), f"{filename}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

def main():
    # Header
    st.markdown('<h1 class="main-header">🤖 Occupation Automation Probability Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Load data
    cdf_data, pdf_data = load_data()
    
    if cdf_data is None or pdf_data is None:
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 📊 Data Overview")
        st.info(f"**Total Occupations:** {len(cdf_data)}")
        st.info(f"**Time Range:** 2017-2086")
        
        st.markdown("## 📥 Download Full Datasets")
        
        # Download CDF data
        col1, col2 = st.columns(2)
        with col1:
            cdf_csv, cdf_csv_name, cdf_csv_type = export_data(cdf_data, "CDF_Data", "csv")
            st.download_button(
                label="📄 CDF CSV",
                data=cdf_csv,
                file_name=cdf_csv_name,
                mime=cdf_csv_type
            )
        
        with col2:
            cdf_excel, cdf_excel_name, cdf_excel_type = export_data(cdf_data, "CDF_Data", "excel")
            st.download_button(
                label="📊 CDF Excel",
                data=cdf_excel,
                file_name=cdf_excel_name,
                mime=cdf_excel_type
            )
        
        # Download PDF data
        col3, col4 = st.columns(2)
        with col3:
            pdf_csv, pdf_csv_name, pdf_csv_type = export_data(pdf_data, "PDF_Data", "csv")
            st.download_button(
                label="📄 PDF CSV",
                data=pdf_csv,
                file_name=pdf_csv_name,
                mime=pdf_csv_type
            )
        
        with col4:
            pdf_excel, pdf_excel_name, pdf_excel_type = export_data(pdf_data, "PDF_Data", "excel")
            st.download_button(
                label="📊 PDF Excel",
                data=pdf_excel,
                file_name=pdf_excel_name,
                mime=pdf_excel_type
            )
    
    # Main content
    tab1, tab2 = st.tabs(["🔍 Search & Analyze", "📋 Browse All Occupations"])
    
    with tab1:
        # Search functionality
        st.markdown('<h2 class="sub-header">🔍 Search Occupations</h2>', unsafe_allow_html=True)
        
        search_term = st.text_input(
            "Search by SOC Code or Occupation Title:",
            placeholder="e.g., 'Chief Executive', '11-1011', 'Software Developer'...",
            help="You can search using partial matches - no need to remember the exact title!"
        )
        
        # Initialize session state for selected occupations
        if 'selected_occupations' not in st.session_state:
            st.session_state.selected_occupations = []
        
        # Search results
        if search_term:
            search_results = search_occupations(cdf_data, search_term)
            
            if not search_results.empty:
                st.success(f"Found {len(search_results)} matching occupation(s)")
                
                # Display search results
                for idx, row in search_results.iterrows():
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        occupation_info = {
                            'soc_code': row.iloc[0],
                            'title': row.iloc[1],
                            'index': idx
                        }
                        
                        # Check if already selected
                        is_selected = any(occ['title'] == occupation_info['title'] for occ in st.session_state.selected_occupations)
                        
                        st.markdown(f"""
                        <div class="occupation-card {'selected-occupation' if is_selected else ''}">
                            <strong>SOC Code:</strong> {occupation_info['soc_code']}<br>
                            <strong>Title:</strong> {occupation_info['title']}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        if is_selected:
                            if st.button(f"Remove", key=f"remove_{idx}", type="secondary"):
                                st.session_state.selected_occupations = [
                                    occ for occ in st.session_state.selected_occupations 
                                    if occ['title'] != occupation_info['title']
                                ]
                                st.rerun()
                        else:
                            if st.button(f"Add", key=f"add_{idx}", type="primary"):
                                st.session_state.selected_occupations.append(occupation_info)
                                st.rerun()
            else:
                st.warning("No occupations found matching your search term.")
        
        # Display selected occupations and plots
        if st.session_state.selected_occupations:
            st.markdown('<h2 class="sub-header">📊 Selected Occupations Analysis</h2>', unsafe_allow_html=True)
            
            # Show selected occupations
            st.markdown("**Selected Occupations:**")
            for i, occ in enumerate(st.session_state.selected_occupations):
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.write(f"{i+1}. {occ['title']} ({occ['soc_code']})")
                with col2:
                    if st.button("❌", key=f"remove_selected_{i}", help="Remove from selection"):
                        st.session_state.selected_occupations.pop(i)
                        st.rerun()
            
            # Create and display plots
            fig_cdf, fig_pdf = create_probability_plots(st.session_state.selected_occupations, cdf_data, pdf_data)
            
            if fig_cdf and fig_pdf:
                st.plotly_chart(fig_cdf, use_container_width=True)
                st.plotly_chart(fig_pdf, use_container_width=True)
                
                # Export selected occupations data
                st.markdown("### 📥 Export Selected Occupations Data")
                
                # Prepare data for selected occupations
                selected_titles = [occ['title'] for occ in st.session_state.selected_occupations]
                selected_cdf = cdf_data[cdf_data.iloc[:, 1].isin(selected_titles)]
                selected_pdf = pdf_data[pdf_data.iloc[:, 1].isin(selected_titles)]
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    sel_cdf_csv, sel_cdf_csv_name, sel_cdf_csv_type = export_data(selected_cdf, "Selected_CDF_Data", "csv")
                    st.download_button(
                        label="📄 Selected CDF CSV",
                        data=sel_cdf_csv,
                        file_name=sel_cdf_csv_name,
                        mime=sel_cdf_csv_type
                    )
                
                with col2:
                    sel_cdf_excel, sel_cdf_excel_name, sel_cdf_excel_type = export_data(selected_cdf, "Selected_CDF_Data", "excel")
                    st.download_button(
                        label="📊 Selected CDF Excel",
                        data=sel_cdf_excel,
                        file_name=sel_cdf_excel_name,
                        mime=sel_cdf_excel_type
                    )
                
                with col3:
                    sel_pdf_csv, sel_pdf_csv_name, sel_pdf_csv_type = export_data(selected_pdf, "Selected_PDF_Data", "csv")
                    st.download_button(
                        label="📄 Selected PDF CSV",
                        data=sel_pdf_csv,
                        file_name=sel_pdf_csv_name,
                        mime=sel_pdf_csv_type
                    )
                
                with col4:
                    sel_pdf_excel, sel_pdf_excel_name, sel_pdf_excel_type = export_data(selected_pdf, "Selected_PDF_Data", "excel")
                    st.download_button(
                        label="📊 Selected PDF Excel",
                        data=sel_pdf_excel,
                        file_name=sel_pdf_excel_name,
                        mime=sel_pdf_excel_type
                    )
        
        # Clear selection button
        if st.session_state.selected_occupations:
            if st.button("🗑️ Clear All Selections", type="secondary"):
                st.session_state.selected_occupations = []
                st.rerun()
    
    with tab2:
        st.markdown('<h2 class="sub-header">📋 Browse All Occupations</h2>', unsafe_allow_html=True)
        
        # Pagination
        items_per_page = 20
        total_items = len(cdf_data)
        total_pages = (total_items - 1) // items_per_page + 1
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            page = st.selectbox("Select Page:", range(1, total_pages + 1), key="page_selector") - 1
        
        start_idx = page * items_per_page
        end_idx = min(start_idx + items_per_page, total_items)
        
        st.info(f"Showing occupations {start_idx + 1}-{end_idx} of {total_items}")
        
        # Display occupations for current page
        page_data = cdf_data.iloc[start_idx:end_idx]
        
        for idx, (_, row) in enumerate(page_data.iterrows()):
            real_idx = start_idx + idx
            occupation_info = {
                'soc_code': row.iloc[0],
                'title': row.iloc[1],
                'index': real_idx
            }
            
            col1, col2 = st.columns([4, 1])
            
            with col1:
                is_selected = any(occ['title'] == occupation_info['title'] for occ in st.session_state.selected_occupations)
                
                st.markdown(f"""
                <div class="occupation-card {'selected-occupation' if is_selected else ''}">
                    <strong>SOC Code:</strong> {occupation_info['soc_code']}<br>
                    <strong>Title:</strong> {occupation_info['title']}
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if is_selected:
                    if st.button(f"Remove", key=f"browse_remove_{real_idx}", type="secondary"):
                        st.session_state.selected_occupations = [
                            occ for occ in st.session_state.selected_occupations 
                            if occ['title'] != occupation_info['title']
                        ]
                        st.rerun()
                else:
                    if st.button(f"Add", key=f"browse_add_{real_idx}", type="primary"):
                        st.session_state.selected_occupations.append(occupation_info)
                        st.rerun()

if __name__ == "__main__":
    main()

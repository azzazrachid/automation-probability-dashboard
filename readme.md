# 🤖 Occupation Automation Probability Dashboard

An interactive Streamlit dashboard for exploring and analyzing automation probability data for various occupations over time (2017-2086).

## Features

### 📊 Data Visualization
- **Cumulative Distribution Function (CDF)** plots showing cumulative automation probability over time
- **Probability Density Function (PDF)** plots showing annual automation probability
- Interactive plots with hover information and zoom capabilities
- Multi-occupation comparison on the same charts

### 🔍 Search & Browse
- **Smart Search**: Search occupations by SOC code or title with partial matching
- **Browse Mode**: Paginated view of all occupations (20 per page)
- **Selection System**: Add/remove occupations to compare multiple at once

### 📥 Export Capabilities
- Download full CDF and PDF datasets (CSV/Excel formats)
- Export selected occupations data for further analysis
- All downloads include proper formatting and headers

### 🎨 User Interface
- Clean, modern design with intuitive navigation
- Responsive layout that works on different screen sizes
- Color-coded visualizations for easy distinction
- Hover effects and interactive elements

## Data Structure

### CDF Data (Cumulative Distribution Function)
- Contains cumulative probabilities from 2017-2086
- Values range from 0 to 1
- Shows the probability that automation will occur by a given year

### PDF Data (Probability Density Function)
- Contains annual probabilities from 2018-2086
- Shows the likelihood of automation occurring in each specific year
- Derived from the CDF data

## Installation & Usage

### Local Testing

1. **Install Python Requirements**
   ```bash
   pip install -r requirements.txt
   ```

2. **Prepare Your Data Files**
   - Place `Probas CDFs.xlsx` in the same directory as the script
   - Place `Probas PDFs.xlsx` in the same directory as the script

3. **Run the Dashboard**
   ```bash
   streamlit run app.py
   ```

4. **Access the Dashboard**
   - Open your browser and go to `http://localhost:8501`

### File Structure
```
your-project-folder/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── Probas CDFs.xlsx      # CDF data file
├── Probas PDFs.xlsx      # PDF data file
└── README.md             # This file
```

## How to Use

### 🔍 Search & Analyze Tab
1. **Search for Occupations**: Use the search box to find occupations by typing partial SOC codes or titles
2. **Add to Selection**: Click "Add" button next to occupations you want to analyze
3. **View Visualizations**: Selected occupations will automatically appear in comparative charts
4. **Export Data**: Download the data for your selected occupations

### 📋 Browse All Occupations Tab
1. **Navigate Pages**: Use the page selector to browse through all occupations
2. **Add Occupations**: Click "Add" to include occupations in your analysis
3. **View in Search Tab**: Switch back to the Search tab to see your visualizations

### 📊 Understanding the Charts
- **CDF Chart**: Shows the cumulative probability of automation by each year
- **PDF Chart**: Shows the annual probability density for each year
- **Multiple Occupations**: Different colors represent different occupations
- **Interactive**: Hover over data points for detailed information

## Technical Details

### Dependencies
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualization library
- **OpenPyXL**: Excel file reading/writing

### Performance Features
- **Data Caching**: Uses Streamlit's caching to improve performance
- **Efficient Search**: Optimized search functionality with partial matching
- **Memory Management**: Efficient handling of large datasets

## Troubleshooting

### Common Issues

1. **"Data files not found" Error**
   - Ensure `Probas CDFs.xlsx` and `Probas PDFs.xlsx` are in the same directory as `app.py`
   - Check that the file names are exactly correct (case-sensitive)

2. **Import Errors**
   - Run `pip install -r requirements.txt` to install all dependencies
   - Make sure you're using a compatible Python version (3.7+)

3. **Performance Issues**
   - The dashboard handles large datasets efficiently, but very large files may require more memory
   - Close other applications if you experience slowness

### Data Format Requirements

Your Excel files should have:
- **First column**: SOC codes
- **Second column**: Occupation titles  
- **Remaining columns**: Years 2017-2086 (CDF) or 2018-2086 (PDF)
- **First row**: Headers
- **Subsequent rows**: Data for each occupation

## Contributing

Feel free to submit issues, feature requests, or improvements to make this dashboard even better!

## License

This project is open source and available under the MIT License.

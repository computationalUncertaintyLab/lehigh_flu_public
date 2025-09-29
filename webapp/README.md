# Flu Forecast Dashboard

A Streamlit web application for visualizing flu incidence forecasts with interactive features.

## Features

### 🏠 Landing Page
- **Current Season Visualization**: Shows observed cases as black dots
- **Historical Seasons**: Toggle to show previous seasons as lines
- **Prediction Intervals**: 80% and 95% prediction intervals as shaded regions
- **Forecast Controls**: Toggle predictions on/off
- **Forecast Text**: Space for entering weekly forecast descriptions
- **Key Metrics**: Current week cases, predicted peak week, peak intensity, forecast horizon

### 📊 Model Analysis (Coming Soon)
- Model parameter analysis
- Convergence diagnostics
- Model comparison
- Uncertainty quantification details

### 🔍 Data Exploration (Coming Soon)
- Interactive data visualization
- Historical trend analysis
- Seasonal pattern exploration

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   streamlit run main.py
   ```

3. **Access the Dashboard**:
   Open your browser to `http://localhost:8501`

## Data Requirements

The app expects the following data structure:
- `./forecasts/2024_25/` - Directory containing forecast pickle files
- `./analysis_data/weekly_data.csv` - Weekly flu case data
- `./analysis_data/influenza_like_illness.csv` - ILI data

## File Structure

```
webapp/
├── main.py                 # Main app with navigation
├── app.py                  # Single-page version
├── requirements.txt        # Python dependencies
├── pages/
│   ├── __init__.py
│   ├── landing_page.py     # Main forecast visualization
│   ├── model_analysis.py   # Model diagnostics (placeholder)
│   └── data_exploration.py # Data exploration (placeholder)
└── README.md
```

## Usage

1. **Navigate**: Use the sidebar to switch between pages
2. **Customize Display**: Toggle historical seasons and predictions
3. **Enter Forecast Text**: Add weekly forecast descriptions
4. **View Metrics**: Check key forecast metrics in the sidebar

## Development

To add new pages:
1. Create a new file in `pages/` directory
2. Add a `show()` function
3. Import and add to the navigation in `main.py`

## Notes

- The app automatically loads the most recent forecast file
- All visualizations are interactive and responsive
- Forecast text can be saved (placeholder functionality)
- Metrics are calculated in real-time from the forecast data


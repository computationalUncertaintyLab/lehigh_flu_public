# Lehigh University Flu Forecast Dashboard

A Streamlit web application for visualizing flu and influenza-like illness (ILI) forecasts at Lehigh University, developed by the Computational Uncertainty Lab.

## Features

### 🔍 Quick Look
- **Current Status Alerts**: Visual indicators showing LOW/MEDIUM/HIGH flu and ILI activity compared to historical data
- **4-Week Ahead Forecasts**: Probability-based forecasts showing chances of increase/decrease
- **Target Selection**: Toggle between ILI and Flu Cases
- **Temporal Forecasts**: 
  - Absolute case counts with 95% prediction intervals
  - Percentage positive trends with historical comparisons
- **Interactive Visualizations**: Altair charts with tooltips and zoom capabilities
- **Current Week Indicator**: Visual marker showing the most recent data point

### 📊 Detailed Look
- **4-Week Panel Views**: Side-by-side comparison of ILI and Flu forecasts
- **Historical Comparisons**: Black dots showing historical averages for the same week across seasons
- **Prediction Intervals**: Blue shaded 80% uncertainty bands
- **Median Forecasts**: Blue dots indicating the predicted median values
- **Weekly Labels**: Clear labeling with MMWR week numbers and end dates

### 📈 Key Metrics
- Current week case counts and percentages
- Historical context for current activity levels
- 4-week horizon forecasts with uncertainty quantification
- Season-specific tracking (currently 2025/26 season)

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

## Data Structure

The app expects the following data structure:

```
webapp/
├── forecasts/
│   └── 2025_26/
│       └── tempo/
│           ├── flu/
│           │   ├── *_tempo_forecast_flu.csv
│           │   └── *_tempo_forecast_prob_above_median_flu.csv
│           └── ili/
│               ├── *_tempo_forecast_ili.csv
│               └── *_tempo_forecast_prob_above_median_ili.csv
├── analysis_data/
│   ├── weekly_data.csv                    # Lab-confirmed flu cases
│   ├── influenza_like_illness.csv         # ILI diagnoses
│   └── from_week_to_season_week.csv       # Week mapping data
```

## File Structure

```
webapp/
├── main.py                    # Main app with data loading and navigation
├── app.py                     # Single-page version (legacy)
├── requirements.txt           # Python dependencies
├── complogo.001.png          # Lab logo
├── pages/
│   ├── __init__.py
│   ├── quick_look.py         # Main forecast page with alerts and selections
│   └── detailed_look.py      # 4-week panel comparison view
├── forecasts/                # Forecast data organized by season
└── analysis_data/            # Historical and current observation data
```

## Usage

1. **Navigate**: Use the sidebar dropdown to switch between "Quick Look" and "Detailed Look"
2. **Select Target**: In Quick Look, toggle between ILI and Flu Cases using the segmented control
3. **View Alerts**: Check the colored alert boxes for current activity levels
4. **Interpret Forecasts**: 
   - Red/upward: Probability of increase above historical median
   - Blue/downward: Probability of decrease below historical median
5. **Explore Data**: Hover over charts for detailed tooltips, zoom and pan for closer inspection

## Forecast Interpretation

- **ILI (Influenza-Like Illness)**: Diagnosed when fever >38°C with respiratory symptoms
- **Flu Cases**: Lab-confirmed influenza via testing
- **Historical Average**: Black dots represent the mean of past observations for that week
- **Predicted Median**: Blue dots show the forecast median
- **80% PI**: Blue shaded region containing 80% of probable outcomes
- **95% PI**: Wider interval shown in temporal charts

## Development

To add new pages:
1. Create a new file in `pages/` directory with a `show()` function
2. Import the module in `main.py`
3. Add to the page selection dropdown in the sidebar

## Team

**Computational Uncertainty Lab, Lehigh University**
- PI: Prof. Thomas McAndrew
- Flu-Crew Team: Kelechi Anyanwu, Ava Baker, Ava Delauro, Eric Shapiro, Holden Engelhardt, Lela Boermeester

## IRB Approval

This project was determined to be not human subjects research by the Lehigh University IRB (2367498-1) on September 24, 2025.

## Resources

- [Computational Uncertainty Lab](https://compuncertlab.org/)
- [Pennsylvania Department of Health Respiratory Dashboard](https://www.pa.gov/agencies/health/diseases-conditions/infectious-disease/respiratory-viruses/respiratory-virus-dashboard)
- [CDC Influenza Information](https://www.cdc.gov/flu/index.html)
- [WHO Influenza Information](https://www.who.int/news-room/fact-sheets/detail/influenza-(seasonal))
- [Lehigh University Health and Wellness Center](https://studentaffairs.lehigh.edu/content/health-wellness-center)


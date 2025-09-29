import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
from datetime import datetime
import os

def load_latest_forecast():
    """Load the most recent forecast data."""
    forecasts_dir = "./forecasts/2024_25/"
    
    if not os.path.exists(forecasts_dir):
        st.error("Forecast directory not found. Please run the forecasting model first.")
        return None
    
    # Find the most recent forecast file
    forecast_files = [f for f in os.listdir(forecasts_dir) if f.endswith('.pkl')]
    
    if not forecast_files:
        st.error("No forecast files found. Please run the forecasting model first.")
        return None
    
    # Sort by modification time to get the most recent
    forecast_files.sort(key=lambda x: os.path.getmtime(os.path.join(forecasts_dir, x)), reverse=True)
    latest_file = forecast_files[0]
    
    try:
        with open(os.path.join(forecasts_dir, latest_file), 'rb') as f:
            samples = pickle.load(f)
        
        # Load the corresponding data
        data = pd.read_csv("./analysis_data/weekly_data.csv")
        ili_data = pd.read_csv("./analysis_data/influenza_like_illness.csv")
        data = data.merge(ili_data, on=["MMWR_YR", "MMWR_WK", "season", "season_week"])
        
        return samples, data, latest_file
    except Exception as e:
        st.error(f"Error loading forecast data: {e}")
        return None

def create_forecast_plot(samples, data, show_historical=True, show_predictions=True):
    """Create the main forecast visualization."""
    
    # Prepare data
    nseasons = len(data.season.unique())
    cases = np.array(data["pos_cases"]).reshape(nseasons, 33)
    N = (np.array(data["N"]).reshape(nseasons, 33)).astype(float)
    
    # Handle missing data
    for (row, col) in np.argwhere(N == -1):
        cases[row, col] = np.nan
        N[row, col] = np.nan
    
    # Determine forecast horizon
    nobs = np.min(np.where(np.isnan(cases[-1, :]))[0]) if np.any(np.isnan(cases[-1, :])) else 33
    
    # Get predicted cases
    cases_predicted_samples = samples["cases_predicted"]  # Shape: [n_samples, nseasons, ntimes]
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Plot historical seasons if requested
    if show_historical:
        colors = ['lightblue', 'lightgreen', 'orange', 'purple']
        season_names = data.season.unique()
        
        for i in range(nseasons - 1):  # Exclude current season
            cases_season = cases_predicted_samples[:, i, :]
            med = np.median(cases_season, axis=0)
            
            # Plot historical seasons as scatter plots only (no lines)
            observed_mask = ~np.isnan(cases[i])
            if np.any(observed_mask):
                ax.scatter(np.arange(33)[observed_mask], cases[i][observed_mask], 
                          color=colors[i], s=30, alpha=0.8, zorder=5,
                          label=f'{season_names[i]} (historical)')
    
    # Plot current season observed data as scatter
    current_season_idx = nseasons - 1
    observed_mask = ~np.isnan(cases[current_season_idx])
    if np.any(observed_mask):
        ax.scatter(np.arange(33)[observed_mask], cases[current_season_idx][observed_mask], 
                  color='black', s=40, alpha=0.9, zorder=6, label='Current season (observed)')
        
        # Also plot as line for current season to show trajectory
        observed_weeks = np.arange(33)[observed_mask]
        observed_values = cases[current_season_idx][observed_mask]
        ax.plot(observed_weeks, observed_values, 
               color='black', alpha=0.7, linewidth=2, zorder=5)
    
    # Plot predictions if requested
    if show_predictions and nobs < 33:
        cases_current_season = cases_predicted_samples[:, current_season_idx, :]
        
        # Calculate percentiles
        low_10, med, high_90 = np.percentile(cases_current_season, [10, 50, 90], axis=0)
        low_5, _, high_95 = np.percentile(cases_current_season, [5, 50, 95], axis=0)
        
        # Plot forecast period
        forecast_weeks = np.arange(nobs, 33)
        
        # 95% prediction interval
        ax.fill_between(forecast_weeks, low_5[nobs:], high_95[nobs:], 
                       alpha=0.2, color='red', label='95% Prediction Interval')
        
        # 80% prediction interval
        ax.fill_between(forecast_weeks, low_10[nobs:], high_90[nobs:], 
                       alpha=0.3, color='red', label='80% Prediction Interval')
        
        # Median forecast
        ax.plot(forecast_weeks, med[nobs:], color='red', linewidth=3, 
               label='Median Forecast')
        
        # Mark forecast horizon
        ax.axvline(x=nobs, color='red', linestyle='--', alpha=0.7, 
                  label=f'Forecast Start (Week {nobs})')
    
    # Add current week vertical line
    try:
        from datetime import datetime
        from epiweeks import Week
        
        # Get current week info
        current_date = datetime.now()
        current_week = Week.fromdate(current_date.date())
        
        # Calculate weeks since academic year start (assuming fall start)
        fall_2025_start_week = Week(2025, 35)  # Week 35 of 2025 (late August)
        
        if current_week.year >= fall_2025_start_week.year:
            if current_week.year > fall_2025_start_week.year:
                weeks_since_start = (current_week.year - fall_2025_start_week.year) * 52 + current_week.week - fall_2025_start_week.week
            else:
                weeks_since_start = current_week.week - fall_2025_start_week.week
            
            if 0 <= weeks_since_start <= 32:
                ax.axvline(x=weeks_since_start, color='orange', linestyle='-', 
                          alpha=0.8, linewidth=2, label='Current Week')
    except Exception:
        pass  # Skip if current week calculation fails
    
    # Styling
    ax.set_xlabel('Week of Season', fontsize=12)
    ax.set_ylabel('Number of Cases', fontsize=12)
    ax.set_title('Flu Incidence Forecast - Current Season', fontsize=16, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Set x-axis to show week numbers
    ax.set_xticks(range(0, 33, 4))
    ax.set_xticklabels([f'W{i}' for i in range(0, 33, 4)])
    
    plt.tight_layout()
    return fig

def show():
    """Show the landing page."""
    
    # Header
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
        }
        .forecast-text {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #1f77b4;
            margin-bottom: 2rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-header">🦠 Flu Forecast Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Loading forecast data..."):
        forecast_data = load_latest_forecast()
    
    if forecast_data is None:
        st.stop()
    
    samples, data, latest_file = forecast_data
    
    # Sidebar controls
    st.sidebar.header("📊 Display Options")
    
    show_historical = st.sidebar.checkbox("Show Historical Seasons", value=True)
    show_predictions = st.sidebar.checkbox("Show Predictions", value=True)
    
    # Forecast information
    st.sidebar.header("📈 Forecast Info")
    st.sidebar.info(f"**Latest Forecast:** {latest_file}")
    st.sidebar.info(f"**Generated:** {datetime.fromtimestamp(os.path.getmtime(f'./forecasts/2024_25/{latest_file}')).strftime('%Y-%m-%d %H:%M')}")
    
    # Main content area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Forecast text area
        st.markdown('<div class="forecast-text">', unsafe_allow_html=True)
        st.markdown("### 📝 This Week's Forecast")
        
        # Text input for forecast description
        forecast_text = st.text_area(
            "Enter forecast description:",
            value="Based on current trends and historical patterns, flu activity is expected to...",
            height=100,
            help="Describe the current week's forecast and key insights"
        )
        
        if st.button("💾 Save Forecast Text"):
            st.success("Forecast text saved!")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Main forecast plot
        fig = create_forecast_plot(samples, data, show_historical, show_predictions)
        st.pyplot(fig)
    
    with col2:
        # Key metrics
        st.markdown("### 📊 Key Metrics")
        
        # Calculate some basic metrics
        cases_predicted_samples = samples["cases_predicted"]
        current_season_idx = len(data.season.unique()) - 1
        current_season_cases = cases_predicted_samples[:, current_season_idx, :]
        
        # Current week cases (if available)
        nobs = np.min(np.where(np.isnan(np.array(data["pos_cases"]).reshape(len(data.season.unique()), 33)[-1, :]))[0]) if np.any(np.isnan(np.array(data["pos_cases"]).reshape(len(data.season.unique()), 33)[-1, :])) else 33
        
        if nobs > 0:
            current_week_cases = np.median(current_season_cases[:, nobs-1])
            st.metric("Current Week Cases", f"{current_week_cases:.0f}")
        
        # Peak week prediction
        peak_weeks = np.argmax(current_season_cases, axis=1)
        peak_week_median = np.median(peak_weeks)
        st.metric("Predicted Peak Week", f"Week {peak_week_median:.0f}")
        
        # Peak intensity prediction
        peak_intensities = np.max(current_season_cases, axis=1)
        peak_intensity_median = np.median(peak_intensities)
        st.metric("Predicted Peak Intensity", f"{peak_intensity_median:.0f} cases")
        
        # Forecast horizon
        forecast_horizon = 33 - nobs
        st.metric("Forecast Horizon", f"{forecast_horizon} weeks")
        
        # Additional info
        st.markdown("### ℹ️ Additional Info")
        st.info("""
        **Prediction Intervals:**
        - 80%: Most likely range
        - 95%: Wider uncertainty range
        
        **Data Sources:**
        - Historical flu surveillance data
        - Current season observations
        - Bayesian forecasting model
        """)


#mcandrew

import streamlit as st
import os
import pandas as pd
from epiweeks import Week


def grab_forecast_data(target=None,above=False,THISSEASON=None):
    this_season = THISSEASON.replace("/","_")
    
    from pathlib import Path
    ROOT = Path(__file__).resolve().parent  # folder containing landing_page.py
    WEBAPP = ROOT#.parent 

    if above:
        folder = WEBAPP /"forecasts" / this_season / "tempo" / target
        forecast_files = list(folder.glob("*above_median*"))
    else:
        folder = WEBAPP /"forecasts" / this_season / "tempo" / target
        forecast_files = list(folder.glob("*tempo_forecast_{:s}*".format(target)))
        
    latest_file         = max(forecast_files, key=os.path.getmtime)
    forecast_data   = pd.read_csv(latest_file)
    forecast_data   = forecast_data.rename(columns = {"MMWR_week":"MMWR_WK"})
    return forecast_data

def grab_ili_data():
    from pathlib import Path
    ROOT = Path(__file__).resolve().parent  # folder containing landing_page.py
    WEBAPP = ROOT#.parent 

    ili_data_file = WEBAPP / "analysis_data" / "influenza_like_illness.csv"
    ili           = pd.read_csv(ili_data_file)
    ili["value"] = [3 if x<3 and x>0 else x for x in ili.ILI]

    return ili

def grab_flu_data():
    from pathlib import Path
    ROOT = Path(__file__).resolve().parent  # folder containing landing_page.py
    WEBAPP = ROOT#.parent 

    flu_data_file = WEBAPP / "analysis_data" / "weekly_data.csv"
    flu           = pd.read_csv(flu_data_file)
    flu["value"] = [3 if x<3 and x>0 else x for x in flu.pos_cases]
    return flu

def collect_time_data(observations,THISSEASON):
    subset = observations.loc[observations.season==THISSEASON]
    subset = subset.dropna()
    last_row = subset.iloc[-1]

    next_four_weeks = []
    next_four_week_enddates = []
    w = Week(last_row["MMWR_YR"],last_row["MMWR_WK"])+1
    for _ in range(0,3+1):
        next_four_weeks.append(w.week)
        next_four_week_enddates.append(w.enddate().strftime("%b %d"))
        w = w+1
    
    time_data = {"MMWR_YR"     :last_row["MMWR_YR"]
                 ,"MMWR_WK"    :last_row["MMWR_WK"]
                 ,"end_date"   :last_row["end_date"]
                 ,"start_date" : last_row["start_date"]
                 ,"season"      :last_row["season"]
                 , "next_four_weeks":next_four_weeks
                 , "next_four_week_enddates":next_four_week_enddates
                 ,"season_week":last_row["season_week"]}
    
    return time_data

# Import page modules
from pages import detailed_look, quick_look

# Page configuration
st.set_page_config(
    page_title="Flu Forecast Dashboard",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_data():
    """Load data into session state if not already loaded."""
    if "observed_data" not in st.session_state:
        #--temporal forecast datasets
        THISSEASON="2025/26"

        forecast_data  = {"ILI":{},"Flu Cases":{}}
        forecast_data["ILI"]["temporal"]       = grab_forecast_data("ili", above=False, THISSEASON=THISSEASON)
        forecast_data["Flu Cases"]["temporal"] = grab_forecast_data("flu", above=False, THISSEASON=THISSEASON)

        #--Above median dataset
        forecast_data["ILI"]["above"]       = grab_forecast_data("ili",above=True, THISSEASON=THISSEASON)
        forecast_data["Flu Cases"]["above"] = grab_forecast_data("flu",above=True, THISSEASON=THISSEASON)

        #--observed data
        observed_data = {}
        observed_data["ILI"]       = grab_ili_data()
        observed_data["Flu Cases"] = grab_flu_data()

        #--collect temporal information about this week
        time_data = collect_time_data(observed_data["ILI"],THISSEASON)

        st.session_state["observed_data"] = observed_data
        st.session_state["forecast_data"] = forecast_data
        st.session_state["SEASON"]        = THISSEASON
        st.session_state["time_data"]     = time_data

def main():
    initialize_session_data()
    
    # Sidebar navigation
    st.sidebar.title("🦠 Flu Forecast Dashboard")
    
    # Page selection
    page = st.sidebar.selectbox(
        "Navigate to:",
        ["Quick Look","Detailed Look"]
    )
    
    # Route to appropriate page
    if page == "Detailed Look":
        detailed_look.show()
    elif page =="Quick Look":
        quick_look.show()
        

if __name__ == "__main__":
    main()


#mcandrew

import os
import sys
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

import streamlit as st

from glob import glob

import altair as alt
from pathlib import Path
import json
import scipy.stats

#--temporal forecast datasets


def grab_forecast_data(target,above=False):

    from pathlib import Path
    ROOT = Path(__file__).resolve().parent  # folder containing landing_page.py
    WEBAPP = ROOT.parent 

    if above:
        folder = WEBAPP /"forecasts" / "tempo" / target
        forecast_files = list(folder.glob("*above_median*"))
    else:
        folder = WEBAPP /"forecasts" / "tempo" / target
        forecast_files = list(folder.glob("*tempo_forecast_{:s}*".format(target)))
        
    latest_file         = max(forecast_files, key=os.path.getmtime)
    forecast_data   = pd.read_csv(latest_file)
    forecast_data   = forecast_data.rename(columns = {"MMWR_week":"MMWR_WK"})
    return forecast_data

forecast_data  = {"ILI":{},"Flu Cases":{}}
forecast_data["ILI"]["temporal"]       = grab_forecast_data("ili")
forecast_data["Flu Cases"]["temporal"] = grab_forecast_data("flu")

#--Above median dataset
forecast_data["ILI"]["above"]       = grab_forecast_data("ili",above=True)
forecast_data["Flu Cases"]["above"] = grab_forecast_data("flu",above=True)

#--observed data
observed_data = {}

def grab_ili_data():
    from pathlib import Path
    ROOT = Path(__file__).resolve().parent  # folder containing landing_page.py
    WEBAPP = ROOT.parent 

    ili_data_file = WEBAPP / "analysis_data" / "influenza_like_illness.csv"
    ili           = pd.read_csv(ili_data_file)
    ili["value"] = [3 if x<3 and x>0 else x for x in ili.ILI]

    return ili
observed_data["ILI"] = grab_ili_data()

def grab_flu_data():
    from pathlib import Path
    ROOT = Path(__file__).resolve().parent  # folder containing landing_page.py
    WEBAPP = ROOT.parent 

    flu_data_file = WEBAPP / "analysis_data" / "weekly_data.csv"
    flu           = pd.read_csv(flu_data_file)
    flu["value"] = [3 if x<3 and x>0 else x for x in flu.pos_cases]
    return flu

observed_data["Flu Cases"] = grab_flu_data()

st.set_page_config(
    # Title and icon for the browser's tab bar:
    page_title="Lehigh Flucast",
    page_icon="XXX",
    # Make the content take up the width of the page:
    layout="wide",
)


def display_todays_data(target,cols, observed_data,THISSEASON):
    from epiweeks import Week

    data = observed_data[target]
    data = data.dropna()
    data = data.loc[data.season==THISSEASON]
    data = data.iloc[:-1]

    with cols[0].container(border=True, height="stretch"):
        most_recent_value = data["value"].values[-1]
        most_recent_N     = data["N"].values[-1]

        todays_target = most_recent_value
        todays_N      = most_recent_N
        todays_p      = todays_target/todays_N

        st.markdown('''As of,   
        *{:s}*'''.format(data.iloc[-1]["end_date"]))

        st.markdown('''{:s} counts | {:d}   
                     {:s} Perc      | {:.0f}%'''.format(target, int(todays_target), target, 100*(todays_p) ))
        

def prob_box(target, cols, forecast_row, date):

    def make_bar(color="red", width=64, height=6):
        """
        Create a thin horizontal bar image in the given color.
        """
        from PIL import Image, ImageDraw
        img = Image.new("RGBA", (width, height), (255, 255, 255, 0))  # transparent bg
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, width, height], fill=color)
        return img

    above_median_value = forecast_row.above_median
    
    with cols.container(border=True, height="stretch"):
        st.markdown("##### {:s}".format(date))

        if above_median_value>0.50:
            up_bar = make_bar("red",height=2)
            st.image(up_bar, width="stretch")
            st.markdown( '{:.0f}% chance <span style="color:red; font-weight:bold;">increase</span>'.format(100*above_median_value) ,unsafe_allow_html=True)
        else:
            down_bar = make_bar("blue",height=2)
            st.image(down_bar, width=32)
            st.markdown( '{:.0f}% chance <span style="color:blue; font-weight:bold;">decrease</span>'.format(100*(1-above_median_value)) ,unsafe_allow_html=True)
 

from epiweeks import Week

def collect_time_data(observations,THISSEASON):
    subset = observations.loc[observations.season==THISSEASON]
    subset = subset.dropna()
    last_row = subset.iloc[-1]

    next_four_weeks = []
    w = Week(last_row["MMWR_YR"],last_row["MMWR_WK"])+1
    for _ in range(0,3+1):
        next_four_weeks.append(w.week)
        w = w+1
    
    time_data = {"MMWR_YR"     :last_row["MMWR_YR"]
                 ,"MMWR_WK"    :last_row["MMWR_WK"]
                 ,"end_date"   :last_row["end_date"]
                 ,"start_date" : last_row["start_date"]
                 ,"season"     :last_row["season"]
                 , "next_four_weeks":next_four_weeks
                 ,"season_week":last_row["season_week"]}
    
    return time_data

import scipy.stats

def show():
    
    THISSEASON="2025/26"

    #--APP--------------------------------------------------------------------------------------------
    alt.renderers.set_embed_options(actions={"export": True, "source": False, "compiled": False})

    with st.container(horizontal=False, gap="medium"):
        #--SELECTION OF TARGET------------------------------------------------------------------------
        cols = st.columns([1], gap="small",width=850)
        with cols[0]:
            st.markdown("## ")

            ili_observations = observed_data["ILI"]
            time_data        = collect_time_data(ili_observations,THISSEASON)
            ili_most_recent  = ili_observations.loc[ (ili_observations.season==THISSEASON) &  (ili_observations.season_week == time_data["season_week"]-1)]
            ili_past_weeks   = ili_observations.loc[ (ili_observations.season!=THISSEASON) &  (ili_observations.season_week == time_data["season_week"]-1)] 

            flu_observations = observed_data["Flu Cases"]
            flu_most_recent  = flu_observations.loc[ (flu_observations.season==THISSEASON) &  (flu_observations.season_week == time_data["season_week"]-1)]
            flu_past_weeks   = flu_observations.loc[ (flu_observations.season!=THISSEASON) &  (flu_observations.season_week == time_data["season_week"]-1)]

            if np.all( np.isnan(flu_past_weeks.value.values) ):
                alert0 = "LOW:"
                alert1 = "In the past, no influenza tests were administered on this week."
            else:
                perc = scipy.stats.norm( np.nanmean(flu_past_weeks.value.values), np.nanstd(flu_past_weeks.value.values) ).cdf( float(flu_most_recent.value.values))
                if perc <0.50:
                    alert0 = "LOW:"
                    alert1 = "Compared to past data, the number of positive flu tests is small"
                elif perc>=0.50 and perc <=0.75:
                    alert0 = "MEDIUM:"
                    alert1 = "Compared to past data, the number of positive flu tests this week is larger than normal"
                elif perc >0.75:
                    alert0 = "HIGH:"
                    alert1 = "Compared to past data, the number of positive flu tests this week is <b>much</b> larger than normal"
                
            st.markdown(
                """
                <div style="background-color: lightblue; padding: 20px; border-radius: 10px;">
                <h3>This week Flu is {alert0:s}</h3> 
                <p> {alert1:s} The most recent week of data is week {season_week:d}, ending on  {date:s}, for the {season:s} season.</p>
                <p> This week there are <b>{ili:d} reported cases</b> of Influenza-like illness and <b>{flu:d} cases </b> of lab-confirmed flu.</p>
                </div>
                """.format( alert0=alert0
                            ,alert1=alert1
                            ,date = time_data["end_date"]
                            ,season = time_data["season"]
                            ,season_week = time_data["season_week"]
                            ,ili  =int(ili_most_recent.value.values)
                            ,flu =int(flu_most_recent.value.values))
                ,unsafe_allow_html=True
            )


        #--4 WEEK ahead forecasts--------------------------------------------------------------------
        with st.container(horizontal=True, gap="medium"):
            cols = st.columns([1], gap="small",width=850)
            with cols[0]:

                target="ILI"
                next_four_weeks = forecast_data[target]["above"]
                ili_next_four_weeks = next_four_weeks.loc[ (next_four_weeks.week>time_data["season_week"]+1) & (next_four_weeks.week<=time_data["season_week"]+4+1) ]

                target="Flu Cases"
                next_four_weeks = forecast_data[target]["above"]
                flu_next_four_weeks = next_four_weeks.loc[ (next_four_weeks.week>time_data["season_week"]+1) & (next_four_weeks.week<=time_data["season_week"]+4+1) ]

                dates = [ (Week(time_data["MMWR_YR"],time_data["MMWR_WK"])+int(x)).enddate().strftime("%Y-%m-%d") for x in np.arange(1,4+1) ]

                ili_name = "Chance > {:d} ILI cases".format(int(ili_most_recent.value.values))
                flu_name =  "Chance > {:d} Flu cases".format(int(flu_most_recent.value.values))


                #--MEDIAN FORECASTS
                ili_forecasts    = forecast_data["ILI"]["temporal"]
                flu_forecasts    = forecast_data["Flu Cases"]["temporal"]

                median_ili_forecasts = ili_forecasts.loc[ ili_forecasts["percentile"] == 0.50]
                median_ili_forecasts = median_ili_forecasts.loc[ median_ili_forecasts.MMWR_WK.isin(time_data["next_four_weeks"]) ] 

                median_flu_forecasts = flu_forecasts.loc[ flu_forecasts["percentile"] == 0.50]
                median_flu_forecasts = median_flu_forecasts.loc[ median_flu_forecasts.MMWR_WK.isin(time_data["next_four_weeks"]) ]


                #--WHERE DOES THE MEDIAN FALL COMPARED TO PAST YEARS?

                ili_past_weeks   = ili_observations.loc[ (ili_observations.season!=THISSEASON) &  (ili_observations.MMWR_WK.isin(time_data["next_four_weeks"])) ]
                alerts_ili           = []
                for i,mmwr_week in enumerate(time_data["next_four_weeks"]):
                    past_season_data = ili_past_weeks.loc[ ili_past_weeks.MMWR_WK == mmwr_week ]

                    mu = np.nanmean(past_season_data.value.values)
                    sd = np.nanstd(past_season_data.value.values)

                    fcast = float(median_ili_forecasts.iloc[i].percentile_value_cases)
                    perc = scipy.stats.norm(mu,sd).cdf( fcast )

                    if perc <0.50:
                        alerts_ili.append("LOW")
                    elif perc>=0.50 and perc <=0.75:
                        alerts_ili.append("MEDIUM")
                    elif perc >0.75:
                        alerts_ili.append("HIGH")

                flu_past_weeks   = flu_observations.loc[ (flu_observations.season!=THISSEASON) &  (flu_observations.MMWR_WK.isin(time_data["next_four_weeks"])) ]
                alerts_flu           = []
                for i,mmwr_week in enumerate(time_data["next_four_weeks"]):
                    past_season_data = flu_past_weeks.loc[ flu_past_weeks.MMWR_WK == mmwr_week ]
                    fcast = float(median_flu_forecasts.iloc[i].percentile_value_cases)

                    if np.all(np.isnan(past_season_data["value"])):
                        alerts_flu.append("LOW")
                    elif len(past_season_data.value.dropna()) <3:
                        mu = np.nanmean(past_season_data.value.values)
                        if fcast > mu:
                            alerts_flu.append("Above average")
                        else:
                            alerts_flu.append("Below average")
                    else:
                        mu = np.nanmean(past_season_data.value.values)
                        sd = np.nanstd(past_season_data.value.values)

                        
                        perc = scipy.stats.norm(mu,sd).cdf( fcast )

                        if perc <0.50:
                            alerts_flu.append("LOW")
                        elif perc>=0.50 and perc <=0.75:
                            alerts_flu.append("MEDIUM")
                        elif perc >0.75:
                            alerts_flu.append("HIGH")
                print(alerts_flu)

                display_table = { "Week":[]
                                  ,"Predicted ILI":[]
                                  , ili_name:[]
                                  ,"ILI Status":[]
                                  ,"Predicted Flu":[]
                                  , flu_name:[]
                                  , "Flu Status":[]}

                display_table["Week"] = dates
                display_table["Predicted ILI"] = [ "{:d}".format(int(x)) for x in median_ili_forecasts.percentile_value_cases.values]
                display_table["Predicted Flu"] = ["{:d}".format(int(x)) for x in median_flu_forecasts.percentile_value_cases.values]
                
                display_table[ili_name]  = [ "{:d}".format(int(x))+"%" for x in 100*ili_next_four_weeks.above_median.values]
                display_table[flu_name]  = [ "{:d}".format(int(x))+"%" for x in 100*flu_next_four_weeks.above_median.values ]

                display_table["ILI Status"] = alerts_ili
                display_table["Flu Status"] = alerts_flu

                st.table( pd.DataFrame(display_table).set_index("Week") )

        with st.container(horizontal=False, gap="medium"):
            cols = st.columns([1,1], gap="medium", width=850)

            with cols[0].container(border=True, height="stretch"):
                st.markdown('''
                ### Contact information''')

                ROOT   = Path(__file__).resolve().parent  # folder containing landing_page.py
                WEBAPP = ROOT.parent
                st.image( WEBAPP / "complogo.001.png")
                
                st.markdown('''
                [Computational Uncertainty Lab](https://compuncertlab.org/)   
                [PI (Prof McAndrew)](https://compuncertlab.org/members/mcandrew/)   
                email: mcandrew@lehigh.edu

                *Flu-Crew team (alphabetical order)*   
                [Kelechi Anyanwu](https://compuncertlab.org/members/anyanwu_kelechi/)    
                [Ava Baker](https://compuncertlab.org/members/baker_ava/)   
                [Ava Delauro](https://compuncertlab.org/members/delauro_ava/)   
                [Eric Shapiro](https://compuncertlab.org/members/shapiro_eric/)   
                [Holden Engelhardt](https://compuncertlab.org/members/engelhardt_holden/)   
                [Lela Boermeester](https://compuncertlab.org/members/boermeester_lela/)
                ''')

            with cols[1].container(border=True, height="stretch"):
                st.markdown('''
                ### More Flu information
                - [Pennsylvania Department of Health Respiratory Dashboard](https://www.pa.gov/agencies/health/diseases-conditions/infectious-disease/respiratory-viruses/respiratory-virus-dashboard)   
                - [CDC Influenza info](https://www.cdc.gov/flu/index.html)   
                - [WHO Influenza Info](https://www.who.int/news-room/fact-sheets/detail/influenza-(seasonal))   
                ''')
            with cols[1].container(border=True, height="stretch"):
                st.markdown('''
                ### Lehigh specific resources
                [Lehigh University Health and Wellness Center](https://studentaffairs.lehigh.edu/content/health-wellness-center)''')

        with st.container(horizontal=False, gap="medium"):
            st.caption( "This project was determined to be not human subjects research by the Lehigh University IRB (2367498-1) on Sept 24, 2025" )

if __name__ == "__main__":
    
    show()


    


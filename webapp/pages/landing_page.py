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

import json

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

    time_data = {"MMWR_YR"     :last_row["MMWR_YR"]
                 ,"MMWR_WK"    :last_row["MMWR_WK"]
                 ,"end_date"   :last_row["end_date"]
                 ,"start_date" : last_row["start_date"]
                 ,"season"     :last_row["season"]
                 ,"season_week":last_row["season_week"]}
    return time_data

def show():
    
    THISSEASON="2025/26"

    #--APP--------------------------------------------------------------------------------------------
    alt.renderers.set_embed_options(actions={"export": True, "source": False, "compiled": False})
    
    with st.container(horizontal=False, gap="medium"):
        #--SELECTION OF TARGET------------------------------------------------------------------------
        cols = st.columns([2,1,3], gap="small",width=900)
        with cols[0]:
            st.markdown("## 4 week Flucast")
 
        with cols[1]:
            help_text = '''
                **ILI** stands for influenza-like illness. An individual is diagnosed with ILI if they have a fever above 38 C and have symptoms consistent with a respiratory virus.   
                **Flu cases** stands for lab-confirmed influenza. A test was administered to an individual and the results of this test confirmed that they have the influenza virus present in their body.
            '''
            target = st.segmented_control("Respiratory targets", options=["ILI", "Flu Cases"], default="ILI",label_visibility="visible")
        with cols[2]:
            st.caption(help_text)

        observations = observed_data[target]
        forecasts    = forecast_data[target]

        time_data = collect_time_data(observations,THISSEASON)

        #--4 WEEK ahead forecasts--------------------------------------------------------------------
        with st.container(horizontal=True, gap="medium"):
            cols = st.columns([1.5,2,2,2,2], gap="medium", width=900)
            display_todays_data( target, cols, observed_data, THISSEASON )

            next_four_weeks = forecast_data[target]["above"]
            next_four_weeks = next_four_weeks.loc[ (next_four_weeks.week>time_data["season_week"]+1) & (next_four_weeks.week<=time_data["season_week"]+4+1) ]

            start_week = Week(time_data["MMWR_YR"],time_data["MMWR_WK"])+1
            for i, (idx, d) in enumerate(next_four_weeks.iterrows()):

                prob_box(target,cols[1:][i], d, start_week.enddate().strftime("%Y-%m-%d") )
                start_week = start_week+1

        #--TEMPORAL FORECASTS---------------------------------------------------------------------
        with st.container(horizontal=False, gap="medium"):

            cols = st.columns(2, gap="medium", width=900)

            observations            = observations.replace(-1,np.nan)
            observations["enddate"] = [ Week(row.MMWR_YR,row.MMWR_WK).enddate().strftime("%Y-%m-%d") for idx,row in observations.iterrows()]
            observations["p"]       = 100*observations["value"] / observations["N"]

            subset_observations            = observations.dropna()

            this_season_observations = subset_observations[subset_observations.season==THISSEASON]

            #--forecast data absolute values------------
            target_forecast_data     = forecast_data[target]["temporal"]
            
            def grab_week_to_season_data():
                from pathlib import Path
                ROOT   = Path(__file__).resolve().parent  # folder containing landing_page.py
                WEBAPP = ROOT.parent
                d = pd.read_csv( WEBAPP / "analysis_data" / "from_week_to_season_week.csv")
                return d
            from_week_to_season_week = grab_week_to_season_data()

            target_forecast_data     = target_forecast_data.merge(from_week_to_season_week, on = ["MMWR_YR","MMWR_WK"], how="left")

            forecast                 = pd.pivot_table(index="season_week",columns = ["percentile"], values = ["percentile_value_cases"], data = target_forecast_data)
            forecast.columns         = ["{:.3f}".format(y) for x,y in forecast.columns]
            forecast                 = forecast.reset_index()

            forecast                 = forecast.rename(columns = {"0.025":"q100","0.975":"q900","0.500":"q500"})
            forecast                 = forecast.loc[forecast.season_week>time_data["season_week"]]

            
            this_week_data = int( this_season_observations.loc[ this_season_observations.season_week==time_data["season_week"]-1,"value"].values)
            this_week_data = pd.DataFrame({"season_week":[time_data["season_week"]]
                                           ,"q100":[this_week_data]
                                           ,"q900":[this_week_data]
                                           ,"q500":[this_week_data]})
            forecast_for_abs_values = pd.concat([this_week_data,forecast])


            target_forecast_data["percentile_value_inc"] = target_forecast_data.percentile_value_inc*100

            #--forecast data
            forecast         = pd.pivot_table(index="season_week",columns = ["percentile"], values = ["percentile_value_inc"], data = target_forecast_data)
            forecast.columns = ["{:.3f}".format(y) for x,y in forecast.columns]
            forecast         = forecast.reset_index()

            forecast = forecast.rename(columns = {"0.025":"q100","0.975":"q900","0.500":"q500"})
            forecast = forecast.loc[forecast.season_week>time_data["season_week"]]

            this_week_data = float(subset_observations.loc[ (subset_observations.season==THISSEASON) & (subset_observations.season_week==time_data["season_week"]-1),"p"].values)
            this_week_data = pd.DataFrame({"season_week":[time_data["season_week"]]
                                           ,"q100":[this_week_data]
                                           ,"q900":[this_week_data]
                                           ,"q500":[this_week_data]})

            forecast_for_perc_values = pd.concat([this_week_data,forecast])

            lab_df       = from_week_to_season_week.loc[from_week_to_season_week.season==THISSEASON]
            label_map    = {sw: dt for sw, dt in zip(lab_df["season_week"], lab_df["end_date"])}
            label_map_js = json.dumps(label_map)

            x_axis = alt.X(
                "season_week:Q",
                title="Week",
                axis=alt.Axis(
                    labelExpr=f"({label_map_js})[datum.value] || ''",
                    labelAngle=-45,
                    ticks=True
                )
            )

            with cols[0].container(border=True, height="stretch"):
                    points = alt.Chart(observations).mark_circle(size=40, color="black",opacity=0.10).encode(
                        x=x_axis,
                        y=alt.Y("value", title="Number of ILI cases" if target == "ILI" else "Number of flu cases", scale = alt.Scale(domain=[0,np.nanmax(observations["value"])])),
                        tooltip=["season", "season_week", "value"]
                    )
                    points_this_season = alt.Chart(this_season_observations).mark_circle(size=40, color="blue").encode(
                        x=x_axis,
                        y=alt.Y("value", title="", scale = alt.Scale(domain=[0,np.nanmax(observations["value"])])),
                        tooltip=["season", "season_week", "value"]
                    )
                    band = alt.Chart(forecast_for_abs_values).mark_area(opacity=0.5).encode(
                        x=x_axis,
                        y="q100:Q",
                        y2="q900:Q",
                        fill=alt.Fill(
                            "legend:N",
                            scale=alt.Scale(domain=["95% PI"], range=["lightblue"]),
                            legend=alt.Legend(
                                title="Forecast",
                                orient="none",        # allow manual placement
                                legendX=250,          # x offset (pixels from left)
                                legendY=20,           # y offset (pixels from top)
                                direction="horizontal" # lay out entries in a row
                            )
                        )
                    ).transform_calculate(
                        legend='"95% PI"'
                    )

                    line = alt.Chart(forecast_for_abs_values).mark_line(strokeWidth=2).encode(
                        x=x_axis,
                        y="q500:Q",
                        stroke=alt.Stroke(
                            "legend:N",
                            scale=alt.Scale(domain=["Median"], range=["darkblue"]),
                            legend=alt.Legend(
                                title="",
                                orient="none",
                                legendX=250,
                                legendY=60,
                                direction="horizontal"
                            )
                        )
                    ).transform_calculate(
                        legend='"Median"'
                    )

                    df_vline = pd.DataFrame({"season_week": [time_data["season_week"]], "label": ["Current week"]})
                    vline = alt.Chart(df_vline).mark_rule(
                        color="black",
                        strokeWidth=2,
                        baseline="top"

                    ).encode(
                        x=x_axis
                    )
                    vtext = alt.Chart(df_vline).mark_text(
                            angle=270,         # rotate 90° counter-clockwise
                            dx=-5,             # horizontal offset from the line
                            dy=-10,              # vertical offset
                            fontWeight="bold",
                            color="black",
                            baseline="top"
                        ).encode(
                            x=x_axis,
                            y=alt.value(50),  # fixed vertical placement (adjust to your scale)
                            text="label"
                        )

                    #chart = (points + points_this_season +band+line+vline+vtext).properties(width="container", height=300).interactive()
                    st.altair_chart((points + points_this_season +band+line+vline+vtext).properties(width="container", height=300).interactive())

            with cols[1].container(border=True, height="stretch"):
               points = alt.Chart(observations).mark_circle(size=40, color="black",opacity=0.10).encode(
                        x=alt.X("season_week:Q", title=""),
                        y=alt.Y("p", title="% positive", scale = alt.Scale(domain=[0,np.nanmax(observations.p)])),
                        tooltip=["season", "season_week", "value"]
                    )
               points_this_season = alt.Chart(this_season_observations).mark_circle(size=40, color="blue").encode(
                        x=alt.X("season_week:Q", title=""),
                        y=alt.Y("p", title="", scale = alt.Scale(domain=[0,np.nanmax(observations.p)])),
                        tooltip=["season", "season_week", "value"]
                    )
               band = alt.Chart(forecast_for_perc_values).mark_area(opacity=0.5, color="lightblue").encode(
                        x  = alt.X("season_week:Q"),
                        y  = alt.Y("q100:Q"),  
                        y2 = alt.Y2("q900:Q")
                    )
               line = alt.Chart(forecast_for_perc_values).mark_line(color="darkblue", strokeWidth=2).encode(
                        x="season_week:Q",
                        y="q500:Q"   # median column (rename '0.500' to 'q500' earlier)
                    )
               df_vline = pd.DataFrame({"season_week": [time_data["season_week"]], "label": ["Current week"]})

               vline = alt.Chart(df_vline).mark_rule(
                   color="black",
                   strokeWidth=2,
                   baseline="top"

               ).encode(
                   x=x_axis
               )
               vtext = alt.Chart(df_vline).mark_text(
                   angle=270,         # rotate 90° counter-clockwise
                   dx=-5,             # horizontal offset from the line
                   dy=-10,              # vertical offset
                   fontWeight="bold",
                   color="black",
                   baseline="top"
               ).encode(
                    x=x_axis,
                    y=alt.value(50),  # fixed vertical placement (adjust to your scale)
                    text="label"
               )
               st.altair_chart((points + points_this_season +band+line+vline+vtext).properties(width="container", height=300).interactive())

        with st.container(horizontal=False, gap="medium"):
            cols = st.columns([1,2], gap="medium", width=900)

            with cols[0].container(border=True, height="stretch"):
                st.markdown('''
                ### Contact information''')
                st.image("./complogo.001.png")
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


    

    
    
    





    


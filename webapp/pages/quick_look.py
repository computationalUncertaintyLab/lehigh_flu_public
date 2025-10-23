#mcandrew

# st.set_page_config(
#     # Title and icon for the browser's tab bar:
#     page_title="Lehigh Flucast",
#     page_icon="XXX",
#     # Make the content take up the width of the page:
#     layout="wide",
# )



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

from epiweeks import Week

import json
import scipy.stats


def display_todays_data(target,cols, observed_data,THISSEASON):
    from epiweeks import Week

    data = observed_data[target]
    data = data.dropna()
    data = data.loc[data.season==THISSEASON]
    #data = data.iloc[:-1]

    print("hellow")
    print(data.iloc[-2:])
    
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
 

def show():
    # Ensure data is loaded into session state
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from main import initialize_session_data
    initialize_session_data()

    import boto3
    from botocore.exceptions import NoCredentialsError

    observed_data = st.session_state["observed_data"]
    forecast_data = st.session_state["forecast_data"]
    time_data     = st.session_state["time_data"]
    THISSEASON    = st.session_state["SEASON"]

    #--APP--------------------------------------------------------------------------------------------
    alt.renderers.set_embed_options(actions={"export": True, "source": False, "compiled": False})

    with st.container(horizontal=False, gap="medium"):

        cols = st.columns(1, gap="small",width=850)
        with cols[0]:
            s3 = boto3.client('s3', region_name='us-east-1')
            bucket_name = "flucasts202526"
            video_key = "FLU CREW 10-21-25.mov"
            
            try:
                # Generate a presigned URL (valid for 1 hour)
                presigned_url = s3.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': bucket_name, 'Key': video_key},
                    ExpiresIn=3600  # URL expires in 1 hour
                )
                
                # Debug: show the URL
                #st.text(f"Video URL: {presigned_url}")
                
                # Display the video using the presigned URL
                st.video(presigned_url)

            except NoCredentialsError:
                st.error("AWS credentials not found. Please configure your credentials.")
            except Exception as e:
                st.error(f"Error retrieving video from S3: {e}")
            
            #st.video("https://flucasts202526.s3.us-east-1.amazonaws.com/videos/2025_26/FLU%20CREW%2010-7-25.mov")
        
        #--SELECTION OF TARGET------------------------------------------------------------------------
        cols = st.columns(2, gap="small",width=850)

        with cols[0]:
            st.markdown("## ")

            ili_observations = observed_data["ILI"]
            ili_most_recent  = ili_observations.loc[ (ili_observations.season==THISSEASON) &  (ili_observations.season_week == time_data["season_week"]-0)]
            
            ili_past_weeks   = ili_observations.loc[ (ili_observations.season!=THISSEASON) &  (ili_observations.season_week == time_data["season_week"]-0)] 

            if np.all( np.isnan(ili_past_weeks.value.values) ):
                alert0 = "LOW:"
                alert1 = "In the past, no ILI diagnoses were made on this week."
            else:
                perc = np.mean( ili_most_recent.value.values < ili_observations.value.values )
                
                if perc <0.50:
                    alert0 = "LOW:"
                    alert1 = "Compared to past data, the number of ILI diagnoses is small"
                elif perc>=0.50 and perc <=0.75:
                    alert0 = "MEDIUM:"
                    alert1 = "Compared to past data, the number of ILI diagnoses this week is larger than normal"
                elif perc >0.75:
                    alert0 = "HIGH:"
                    alert1 = "Compared to past data, the number of ILI diagnoses this week is <b>much</b> larger than normal"
                
            st.markdown(
                """
                <div style="background-color: lightblue; padding: 20px; border-radius: 10px;">
                <h3>This week ILI is {alert0:s}</h3> 
                <p> This week there are <b>{ili:d} reported cases</b> of Influenza-like illness.
                {alert1:s}. The most recent week of data is week {season_week:d}, ending on  {date:s}, for the {season:s} season.</p>
                
                </div>
                """.format( alert0       = alert0
                            ,alert1      = alert1
                            ,date        = time_data["end_date"]
                            ,season      = time_data["season"]
                            ,season_week = time_data["season_week"]
                            ,ili         = int(ili_most_recent.value.values)
                            )
                ,unsafe_allow_html=True
            )
            
        with cols[1]:
            st.markdown("## ")

            flu_observations = observed_data["Flu Cases"]
            flu_most_recent  = flu_observations.loc[ (flu_observations.season==THISSEASON) &  (flu_observations.season_week == time_data["season_week"]-0)]
            flu_past_weeks   = flu_observations.loc[ (flu_observations.season!=THISSEASON) &  (flu_observations.season_week == time_data["season_week"]-0)]

            if np.all( np.isnan(flu_past_weeks.value.values) ):
                alert0 = "LOW:"
                alert1 = "In the past, no influenza tests were administered on this week."
            else:
                #perc = scipy.stats.norm( np.nanmean(flu_past_weeks.value.values), np.nanstd(flu_past_weeks.value.values) ).cdf( float(flu_most_recent.value.values))
                perc = np.mean( flu_most_recent.value.values < flu_observations.value.values )
                
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
                <p> This week there are <b>{flu:d} cases </b> of lab-confirmed flu.
                 {alert1:s} The most recent week of data is week {season_week:d}, ending on  {date:s}, for the {season:s} season.</p>
                </div>
                """.format( alert0       = alert0
                            ,alert1      = alert1
                            ,date        = time_data["end_date"]
                            ,season      = time_data["season"]
                            ,season_week = time_data["season_week"]
                            ,flu         = int(flu_most_recent.value.values))
                ,unsafe_allow_html=True
            )

        #--4 WEEK ahead forecasts--------------------------------------------------------------------
        with st.container(horizontal=False):
            cols = st.columns([1,1,2])   # adjust widths as you like

            with cols[0]:
                st.markdown("● **Historical average**", unsafe_allow_html=True)

            with cols[1]:
                st.markdown("<span style='color:blue'>●</span> **Predicted median**", unsafe_allow_html=True)

            with cols[2]:
                st.markdown(
                    "<span style='display:inline-block; width:20px; height:12px; background-color:blue;'></span> **80% uncertainty**",
                    unsafe_allow_html=True
                )


        with st.container(horizontal=True, gap="medium"):
            cols = st.columns(2, gap="small",width=850,border=True)
            
            with cols[0]:
                ILI_forecasts = forecast_data["ILI"]["temporal"]
                ILI_forecasts = ILI_forecasts.loc[ILI_forecasts.MMWR_WK.isin(time_data["next_four_weeks"])]
                ILI_forecasts = ILI_forecasts.loc[ ILI_forecasts["percentile"].isin([0.10,0.50,0.90]) ]

                ILI_data      = observed_data["ILI"]
                ILI_data      = ILI_data.loc[ILI_data.MMWR_WK.isin(time_data["next_four_weeks"])]


                st.markdown("### ILI • 4-week panel")

                # ---------------------------
                # 2) FILTER to current season’s 4 weeks (40..43) and build PI table
                # ---------------------------
                TARGET_SEASON = "2025/26"
                TARGET_SEMESTER = "Fall"
                WEEKS = time_data["next_four_weeks"]#[40, 41, 42, 43]

                fc4 = ILI_forecasts.rename(columns={"percentile_value_cases":"value"})

                # Pivot percentiles 0.1, 0.5, 0.9 -> lo80, median, hi80
                fc_wide = (
                    fc4.pivot_table(index="MMWR_WK", columns="percentile", values="value")
                       .rename(columns={0.1:"lo80", 0.5:"median", 0.9:"hi80"})
                       .reset_index()
                )

                # Add neat labels (row order is 40,41,42,43)
                fc_wide = fc_wide.sort_values("MMWR_WK").reset_index(drop=True)
                fc_wide["horizon"] = fc_wide.index  # 0..3
                week_enddates = list(time_data["next_four_week_enddates"])
                fc_wide["row_label"] = fc_wide["horizon"].map(lambda h: f"This wk ( ending on {week_enddates[h]})" if h == 0 else f"+{h} wk ({week_enddates[h]})")
 
                
                fc_wide["week_label"] = "MMWR " + fc_wide["MMWR_WK"].astype(str)

                # ---------------------------
                # 3) Historical dots for the SAME week number (across years), excluding NaNs
                # ---------------------------
                hist = (
                    ILI_data.loc[ILI_data["MMWR_WK"].isin(WEEKS), ["MMWR_YR","MMWR_WK","value"]]
                          .dropna(subset=["value"])
                          .rename(columns={"value":"hist_value"})
                )

                # Attach horizon/labels to history by week number
                hist_aug = hist.merge(fc_wide[["MMWR_WK","horizon","row_label","week_label"]], on="MMWR_WK", how="inner")

                hist_mean = (
                    hist_aug.groupby(["MMWR_WK","row_label","week_label","horizon"], as_index=False)
                    .agg(hist_mean=("hist_value","mean"))
                )
                hist_mean["y0"] = 0

                print(hist_aug)

                # Also add y0 to forecast rows
                fc_plot = fc_wide.assign(y0=0)

                # ---------------------------
                # 4) Build 4 separate rows and vconcat — no facet
                # ---------------------------
                HIST_DOT_SIZE = 70
                MEDIAN_SIZE   = 70
                PI_THICKNESS  = 6
                ROW_HEIGHT    = 48

                # Shared x-domain
                xmin = min(0, float(min(hist_mean["hist_mean"].min() if len(hist_mean) else 0,
                                        fc_plot["lo80"].min())))
                xmax = float(max(hist_mean["hist_mean"].max() if len(hist_mean) else 1,
                                 fc_plot["hi80"].max()))
                pad = 0.06*(xmax - xmin) if xmax > xmin else 1.0
                x_domain = [xmin - pad, xmax + pad]

                def row_layer(mmwr_wk: int, row_lab: str):
                    # filter to one row’s week
                    fc_row   = fc_plot.loc[fc_plot["MMWR_WK"] == mmwr_wk].copy()
                    hist_row = hist_mean.loc[hist_mean["MMWR_WK"] == mmwr_wk].copy()

                    # safety: enforce single row per side
                    if len(fc_row) != 1:
                        fc_row = fc_row.drop_duplicates(subset=["MMWR_WK"]).head(1)
                    if len(hist_row) != 1:
                        hist_row = hist_row.groupby(["MMWR_WK"], as_index=False).agg(hist_mean=("hist_mean","mean"))
                        hist_row["y0"] = 0
                        hist_row["week_label"] = f"MMWR {mmwr_wk}"

                    # encodings (shared x scale)
                    x_lo  = alt.X("lo80:Q",    title=None, scale=alt.Scale(domain=x_domain))
                    x2_hi = alt.X2("hi80:Q")
                    x_med = alt.X("median:Q",  title=None, scale=alt.Scale(domain=x_domain))
                    x_mu  = alt.X("hist_mean:Q", title="ILI cases", scale=alt.Scale(domain=x_domain))
                    y0    = alt.Y("y0:Q", axis=None)

                    # layers
                    pi_bar = alt.Chart(fc_row).mark_bar(size=PI_THICKNESS, opacity=0.4).encode(
                        x=x_lo, x2=x2_hi, y=y0,
                        tooltip=["week_label:N","lo80:Q","hi80:Q"]
                    )

                    med_dot = alt.Chart(fc_row).mark_point(size=MEDIAN_SIZE, color="blue", filled=True).encode(
                        x=x_med, y=y0,
                        tooltip=["week_label:N","median:Q"]
                    )

                    hist_dot = alt.Chart(hist_row).mark_point(size=HIST_DOT_SIZE, color="black", filled=True).encode(
                        x=x_mu, y=y0,
                        tooltip=["week_label:N","hist_mean:Q"] if "week_label" in hist_row.columns else [alt.TooltipValue(f"MMWR {mmwr_wk}")]
                    )

                    # row label on the left as a subtitle
                    return (pi_bar + hist_dot + med_dot).properties(
                        height=ROW_HEIGHT,
                        title=alt.TitleParams(text=row_lab, anchor="start", fontSize=12, dy=-6)
                    )

                # Build rows in the correct order
                rows = []
                for _, r in fc_wide.sort_values("horizon").iterrows():
                    rows.append(row_layer(int(r["MMWR_WK"]), r["row_label"]))
                chart = alt.vconcat(*rows, spacing=8).resolve_scale(x="shared")

                st.altair_chart(chart, use_container_width=True)


            with cols[1]:

                FLU_forecasts = forecast_data["Flu Cases"]["temporal"]
                FLU_forecasts = FLU_forecasts.loc[FLU_forecasts.MMWR_WK.isin(time_data["next_four_weeks"])]
                FLU_forecasts = FLU_forecasts.loc[ FLU_forecasts["percentile"].isin([0.10,0.50,0.90]) ]

                FLU_data      = observed_data["Flu Cases"]
                FLU_data      = FLU_data.loc[FLU_data.MMWR_WK.isin(time_data["next_four_weeks"])]


                st.markdown("### FLU • 4-week panel")

                # ---------------------------
                # 2) FILTER to current season’s 4 weeks (40..43) and build PI table
                # ---------------------------
                TARGET_SEASON = "2025/26"
                TARGET_SEMESTER = "Fall"
                WEEKS = time_data["next_four_weeks"]#[40, 41, 42, 43]

                fc4 = FLU_forecasts.rename(columns={"percentile_value_cases":"value"})

                # Pivot percentiles 0.1, 0.5, 0.9 -> lo80, median, hi80
                fc_wide = (
                    fc4.pivot_table(index="MMWR_WK", columns="percentile", values="value")
                       .rename(columns={0.1:"lo80", 0.5:"median", 0.9:"hi80"})
                       .reset_index()
                )

                # Add neat labels (row order is 40,41,42,43)
                fc_wide = fc_wide.sort_values("MMWR_WK").reset_index(drop=True)
                fc_wide["horizon"] = fc_wide.index  # 0..3

                week_enddates = list(time_data["next_four_week_enddates"])
                fc_wide["row_label"] = fc_wide["horizon"].map(lambda h: f"This wk (ending on {week_enddates[h]})" if h == 0 else f"+{h} wk ({week_enddates[h]})")

                fc_wide["week_label"] = "MMWR " + fc_wide["MMWR_WK"].astype(str)

                # ---------------------------
                # 3) Historical dots for the SAME week number (across years), excluding NaNs
                # ---------------------------
                hist = (
                    FLU_data.loc[FLU_data["MMWR_WK"].isin(WEEKS), ["MMWR_YR","MMWR_WK","value"]]
                          .dropna(subset=["value"])
                          .rename(columns={"value":"hist_value"})
                )

                # Attach horizon/labels to history by week number
                hist_aug = hist.merge(fc_wide[["MMWR_WK","horizon","row_label","week_label"]], on="MMWR_WK", how="inner")

                #print(hist_aug)
                
                hist_mean = (
                    hist_aug.groupby(["MMWR_WK","row_label","week_label","horizon"], as_index=False)
                    .agg(hist_mean=("hist_value","mean"))
                )
                hist_mean["y0"] = 0

                # Also add y0 to forecast rows
                fc_plot = fc_wide.assign(y0=0)

                # ---------------------------
                # 4) Build 4 separate rows and vconcat — no facet
                # ---------------------------
                HIST_DOT_SIZE = 70
                MEDIAN_SIZE   = 70
                PI_THICKNESS  = 6
                ROW_HEIGHT    = 48

                # Shared x-domain
                xmin = min(0, float(min(hist_mean["hist_mean"].min() if len(hist_mean) else 0,
                                        fc_plot["lo80"].min())))
                xmax = float(max(hist_mean["hist_mean"].max() if len(hist_mean) else 1,
                                 fc_plot["hi80"].max()))
                pad = 0.06*(xmax - xmin) if xmax > xmin else 1.0
                x_domain = [xmin - pad, xmax + pad]

                def row_layer(mmwr_wk: int, row_lab: str):
                    # filter to one row’s week
                    fc_row   = fc_plot.loc[fc_plot["MMWR_WK"] == mmwr_wk].copy()
                    hist_row = hist_mean.loc[hist_mean["MMWR_WK"] == mmwr_wk].copy()

                    # safety: enforce single row per side
                    if len(fc_row) != 1:
                        fc_row = fc_row.drop_duplicates(subset=["MMWR_WK"]).head(1)
                    if len(hist_row) != 1:
                        hist_row = hist_row.groupby(["MMWR_WK"], as_index=False).agg(hist_mean=("hist_mean","mean"))
                        hist_row["y0"] = 0
                        hist_row["week_label"] = f"MMWR {mmwr_wk}"

                    # encodings (shared x scale)
                    x_lo  = alt.X("lo80:Q",    title=None, scale=alt.Scale(domain=x_domain))
                    x2_hi = alt.X2("hi80:Q")
                    x_med = alt.X("median:Q",  title=None, scale=alt.Scale(domain=x_domain))
                    x_mu  = alt.X("hist_mean:Q", title="ILI cases", scale=alt.Scale(domain=x_domain))
                    y0    = alt.Y("y0:Q", axis=None)

                    # layers
                    pi_bar = alt.Chart(fc_row).mark_bar(size=PI_THICKNESS, opacity=0.4).encode(
                        x=x_lo, x2=x2_hi, y=y0,
                        tooltip=["week_label:N","lo80:Q","hi80:Q"]
                    )

                    med_dot = alt.Chart(fc_row).mark_point(size=MEDIAN_SIZE, color="blue", filled=True).encode(
                        x=x_med, y=y0,
                        tooltip=["week_label:N","median:Q"]
                    )

                    hist_dot = alt.Chart(hist_row).mark_point(size=HIST_DOT_SIZE, color="black", filled=True).encode(
                        x=x_mu, y=y0,
                        tooltip=["week_label:N","hist_mean:Q"] if "week_label" in hist_row.columns else [alt.TooltipValue(f"MMWR {mmwr_wk}")]
                    )

                    # row label on the left as a subtitle
                    return (pi_bar + hist_dot + med_dot).properties(
                        height=ROW_HEIGHT,
                        title=alt.TitleParams(text=row_lab, anchor="start", fontSize=12, dy=-6)
                    )

                # Build rows in the correct order
                rows = []
                for _, r in fc_wide.sort_values("horizon").iterrows():
                    rows.append(row_layer(int(r["MMWR_WK"]), r["row_label"]))
                chart = alt.vconcat(*rows, spacing=8).resolve_scale(x="shared")

                st.altair_chart(chart, use_container_width=True)


                


                

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
                [Elmira Stepanyan](https://compuncertlab.org/members/stepanyan_elmira/)   
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


    


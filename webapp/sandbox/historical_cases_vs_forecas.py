#delauro

import numpy as np
import pandas as pd

import sys

#sys.path.append("./weekly_outputs/")
#from helper_files.helper_files import *

import plotly.express as px
import plotly.graph_objects as go

def collect_most_recent_week_of_data(d,ed):
    return d.loc[d.end_date==ed]

from datetime import datetime, timedelta
from epiweeks import Week

from pathlib import Path
# Add parent directory to path so we can import main
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from main import *

if __name__ == "__main__":

    THISSEASON       = "2025/26"
    this_MMWRWK      = (Week.thisweek()-1)
    this_end_date    = this_MMWRWK.enddate().strftime("%Y-%m-%d")

    next_four_weeks         = [ (this_MMWRWK+x).week  for x in range(1,4+1) ]
    next_four_week_enddates = [ (this_MMWRWK+x).enddate().strftime("%Y-%m-%d")  for x in range(1,4+1) ]


    #--historical cases + average
    weekly_data = pd.read_csv("./analysis_data/weekly_data.csv")

    # First, create a pivot table to have each season as a separate column
    weekly_pivot             = weekly_data.pivot(index='MMWR_WK', columns='MMWR_YR', values='pos_cases')
    weekly_pivot['Average']  = weekly_pivot.mean(axis=1)

    # Re-arrange weeks so that weeks 35-52 come first, then 1-34
    
    # split dataframe into two parts
    ordered_weeks = pd.DataFrame({"MMWR_WK":list(np.arange(35,52+1)) + list(np.arange(1,34+1)) })
    new_df        = ordered_weeks.merge( weekly_pivot, left_on = "MMWR_WK", right_index=True) 

    #--FLU-----------------------------------------------------------------------------------
    
    
    flu       = grab_flu_data()
    flu_weeks = flu.loc[flu.season==THISSEASON].copy()
    flu_weeks["pos_cases"] = np.nan_to_num(flu_weeks.pos_cases.values, nan=0)

    this_week        = int(str(this_MMWRWK)[-2:])
    this_season_week = int(flu_weeks.loc[flu_weeks.MMWR_WK==this_week].season_week.values[0])
    this_value       = float(flu_weeks.loc[flu_weeks.season_week==this_season_week,"pos_cases"].iloc[0])
    
    flu_fc    = grab_forecast_data(target="flu", above=False, THISSEASON=THISSEASON)
    time_data = pd.read_csv("./analysis_data/from_week_to_season_week.csv")
    time_data = time_data.loc[time_data.season==THISSEASON]
   
    flu_fc = flu_fc.merge( time_data[["MMWR_YR","MMWR_WK","season","semester","season_week","end_date"]], on=["MMWR_YR","MMWR_WK","season","semester"], how="left")

    fc         = pd.pivot_table( flu_fc, index="season_week", columns="percentile", values="percentile_value_cases").sort_index()
    fc.columns = [float(c) for c in fc.columns]  # ensure 0.1, 0.5, 0.9
    
    fc.loc[this_season_week, [0.1, 0.5, 0.9]] = this_value
    fc = fc.sort_index()
    
    # Forecast segment
    future_mask = fc.index >= this_season_week
    f_sw        = fc.index[future_mask].to_numpy(int)
    
    f_med       = fc.loc[future_mask, 0.5].to_numpy(float)
    f_lo        = fc.loc[future_mask, 0.1].to_numpy(float)
    f_hi        = fc.loc[future_mask, 0.9].to_numpy(float)

    # Create the interactive plot
    fig = go.Figure(
        layout=go.Layout(
            xaxis=dict(title="Season Week"),
            yaxis=dict(title="Flu Cases"),
            template="plotly_white",
            hovermode="x unified"
        )
    )

    # fill in na values, create average line across seasons, customize hovertemplate

    new_df.fillna(0, inplace=True)
    customdata = weekly_pivot.values # shape: (53, n_years + 1)

    fig.add_trace(go.Scatter(
        x=new_df.index,
        y=new_df['Average'],  # y-axis is average
        mode='lines+markers',
        name='Average',
        line=dict(color='green', width=3),
        customdata=customdata,
        hovertemplate=(
            "Week: %{x}<br>" +
            "Average: %{y}<br>" +
            "2121-22: %{customdata[0]}<br>" +
            "2222-23: %{customdata[1]}<br>" +
            "2323-24: %{customdata[2]}<br>" +
            "2424-25: %{customdata[3]}<br>" +
            "2525-26: %{customdata[4]}"
        )
    ))
   

    # Add forecast median line
    fig.add_trace(go.Scatter(
        x=f_sw,
        y=f_med,
        mode='lines',
        name='Forecast Median',
        line=dict(color='#2563eb', width=3, dash='dash')
    ))

    # Add forecast 10-90% band
    fig.add_trace(go.Scatter(
        x=np.concatenate([f_sw, f_sw[::-1]]),
        y=np.concatenate([f_hi, f_lo[::-1]]),
        fill='toself',
        fillcolor='rgba(147,197,253,0.5)',
        line=dict(color='rgba(255,255,255,0)'),
        showlegend=True,
        name='Forecast 10-90%'
    ))

    # Customize layout
    fig.update_layout(
    title={
        'text': f"Flu Forecast for the {THISSEASON} Season",
        'x':0.5,           # center title
        'xanchor': 'center',
        'yanchor': 'top',
        'font': dict(size=20, color='black')
    })

    # Map season_week → formatted date
    sw_to_end = dict(zip(time_data.season_week.values, time_data.end_date.values))

    def fmt_mon_day(dlike):
        if not dlike or pd.isna(dlike):
            return ""
        dt = pd.to_datetime(dlike)
        return f"{dt.strftime('%b')} {dt.day}"

    # Select every 3rd tick
    xticks = sorted(time_data.season_week.unique())
    xticks = xticks[::3] if len(xticks) else []

    # Update x-axis with formatted tick labels
    fig.update_xaxes(
        tickvals=xticks,
        ticktext=[fmt_mon_day(sw_to_end.get(x, "")) for x in xticks],
        tickangle=35,
        title_text="Season week"
    )

    # Update y-axis title
    fig.update_yaxes(title_text="Flu cases")

    # Add vertical line for the current week
    print(this_season_week)
    fig.add_vline(
        x=this_season_week,
        line=dict(color="#f59e0b", width=2, dash="dash"),  # ACCENT_2 equivalent
        annotation_text="This week",
        annotation_position="top right",
        annotation_font=dict(color="#f59e0b", size=11)
    )
    
    fig.show()

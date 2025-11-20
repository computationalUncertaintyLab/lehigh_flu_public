#boermeester

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

if __name__ == "__main__":

    flu = pd.read_csv("./analysis_data/weekly_data.csv")
    ili = pd.read_csv("./analysis_data/influenza_like_illness.csv")

    flu_and_ili = flu.merge(ili, on = ["MMWR_YR","MMWR_WK"] )
    

    def collect_peak_week_from_single_season(subset):
        pass#<--code goes here

    def collect_peak_cases_from_single_season(subset):
        pass#<--code goes here
 
    peak_weeks__flu = flu_and_ili.groupby(["season"]).apply( collect_peak_week_from_single_season )
    peak_cases__flu = flu_and_ili.groupby(["season"]).apply( collect_peak_cases_from_single_season )

    peak_weeks__ili = flu_and_ili.groupby(["season"]).apply( collect_peak_week_from_single_season )
    peak_cases__ili = flu_and_ili.groupby(["season"]).apply( collect_peak_cases_from_single_season )


    #--then stack these datasets above on top of one an other.
    #--add in two columns that describe the target (flu or ili) and the target type (peak_week or peak_cases)
    #--write out that file as a csv. This is good practice and lets you view the raw data that will be plotted.
    #--Then plot (below). 
    

    import matplotlib.pyplot as plt
    import seaborn as sns

    flu_only = peaks[peaks["target"] == "flu"]
    ili_only = peaks[peaks["target"] == "ili"]

    st.title("Peak Timing and Intensity KDE")
    st.subheader("Lela Boermeester", divider ="blue")

    fig,ax =plt.subplots(1,2)
    sns.kdeplot(
        data=flu_only,
        x="peak_week",
        y="peak_value",
        fill = True,
        clip = (0,300),
        ax = ax[0]
    )
    sns.scatterplot(
        data=flu_only,
        x="peak_week",
        y="peak_value",
        color="black",
        edgecolor="black",
        ax = ax[0]
    )

    for i, row in flu_only.iterrows():
        ax[0].text(
            row["peak_week"] + 0.6,  
            row["peak_value"] + 0.6,  
            str(row["MMWR_YR"]),       
            fontsize=8,
            color="black"
        )


    ax[0].set_title("FLU Joint Density Estimation")
    ax[0].set_xlabel("Peak Week")
    ax[0].set_xlim(0, 37)
    ax[0].set_ylabel("Peak Value")
    ax[0].set_ylim(0, 120)
    ax[0].grid(True, linestyle="--", alpha=0.7)


    sns.kdeplot(
        data=ili_only,
        x="peak_week",
        y="peak_value",
        fill = True,
        color = "orange",
        clip = (0,300),
        ax = ax[1]
    )
    sns.scatterplot(
        data=ili_only,
        x="peak_week",
        y="peak_value",
        color="black",
        edgecolor="black",
        ax = ax[1]
    )

    for i, row in ili_only.iterrows():
        ax[1].text(
            row["peak_week"] + 0.6,   
            row["peak_value"] + 0.6,  
            str(row["MMWR_YR"]),      
            fontsize=8,
            color="black"
        )


    ax[1].set_title("ILI Joint Density Estimation")
    ax[1].set_xlabel("Peak Week")
    ax[1].set_xlim(0, 37)
    ax[1].set_ylabel("Peak Value")
    ax[1].set_ylim(0, 300)
    ax[1].grid(True, linestyle="--", alpha=0.7)
    plt.tight_layout()
    st.pyplot(fig)

    st.divider()
    st.markdown("Join Density Estimate of the weeks at which :blue-background[Flu] and :orange-background[ILI] and the number of cases at the peak for the past 4 years. ")

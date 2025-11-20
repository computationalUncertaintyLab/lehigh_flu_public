#surname

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

if __name__ == "__main__":

    flu = pd.read_csv("./analysis_data/weekly_data.csv")
    ili = pd.read_csv("./analysis_data/influenza_like_illness.csv")

    flu_and_ili = flu.merge(ili, on = ["MMWR_YR","MMWR_WK"] )
 

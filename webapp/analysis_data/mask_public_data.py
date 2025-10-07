#mcandrew

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

if __name__ == "__main__":

    ili = pd.read_csv("./analysis_data/influenza_like_illness.csv")
    ili["ILI"] = [3 if x in {1,2} else x for x in ili.ILI.values]
    ili.to_csv("./analysis_data/influenza_like_illness.csv",index=False)

    flu = pd.read_csv("./analysis_data/weekly_data.csv")
    flu["pos_cases"] = [3 if x in {1,2} else x for x in flu.pos_cases.values]
    flu.to_csv("./analysis_data/weekly_data.csv",index=False)




    


import pandas as pd
import numpy as np
import glob

training_data_dir = "/Users/davidnull/phd/data/3rd_stage_base_training/"
    
for data_dir in glob.glob(training_data_dir + "/*"):
    filename = data_dir + "/new_data.csv"
    df = pd.read_csv(filename)
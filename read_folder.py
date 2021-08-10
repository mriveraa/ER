# -*- coding: utf-8 -*-
"""
Created on Mon Jun 21 10:16:20 2021

@author: mriveraa
"""
import csv
from itertools import takewhile
# Import Module
import os
import pandas as pd
from os.path import join, dirname

# Read txt file
file_path = r"O:\200\290_AMK\90_Studenten\Mariella_Rivera\phD\ER_Software-Benchmarking\energy_rating_v06_MR\example_data\Round_robin_inputfile.txt"

from io import StringIO
import pandas as pd

subfiles = [StringIO()]

with open(file_path) as bigfile:
    for line in bigfile:
        if line.strip() == "": # blank line, new subfile                                                                                                                                       
            subfiles.append(StringIO())
        else: # continuation of same subfile                                                                                                                                                   
            subfiles[-1].write(line)

df ={}
df_names = ["Module Parameters", "Spectral responsivity","Power Rating Matrix", "Angle of incidence", "Thermal coefficients"]
i = 0
for subfile in subfiles:
    subfile.seek(0)
    table = pd.read_csv(subfile, sep='\t')
    df[df_names[i]] = table
    i = i + 1


# Module parameters
mod_parameters = df['Module Parameters'].T
# Module Area
module_area = float(mod_parameters["Module_Area_[m2]"])
# Technology
tech = str(mod_parameters["Technology"][0])


# Spectral responsivity
df['Spectral responsivity'].reset_index(level=0, inplace=True)
spec_resp = df['Spectral responsivity']
spec_resp.drop(0, inplace=True)
spec_resp.columns = ['wavelength', 'spec_resp']
spec_resp = spec_resp.astype(float)


# Power Rating Matrix
power_matrix = df['Power Rating Matrix'].reset_index(level=[0,1])
power_matrix.drop(0, inplace=True)
power_matrix.columns = ['gmean', 'temp', 'pmpp']
power_matrix = power_matrix.astype(float)

# Angle of incidence
ar= df['Angle of incidence']
ar = ar['[Angle of incidence]'][0]


# Thermal coefficients
u0= df['Thermal coefficients']
u0 = u0['[Thermal coefficients]'][0]

u1= df['Thermal coefficients']
u1 = u1['[Thermal coefficients]'][1]



#%%
# Folder Path
path = r"O:\200\290_AMK\90_Studenten\Mariella_Rivera\phD\ER_Software-Benchmarking\energy_rating_v06_MR\example_data"
  
# Change the directory
os.chdir(path)
  
  
# iterate through all file
for file in os.listdir():
    # Check whether file is in text format or not
    if file.endswith(".txt"):
        file_path = f"{path}\{file}"
        print(file_path)
        
        # call read text file function
        with open(file_path) as f:
            csv_reader = csv.reader(f, delimiter="\t",skipinitialspace=True)
            tables = {}
            try:
                while True:
                    title = next(f).rstrip()
                    stanza = takewhile(lambda row: row, csv_reader)
                    tables[title] = [next(stanza)] + \
                                    [row for row in stanza]
            except StopIteration:
                pass    # EOF while reading title or header row
    
        # Module parameters
        parameters = pd.DataFrame(tables['[Module parameters]'])
        mod_parameters = parameters.T
        mod_parameters.columns = mod_parameters.iloc[0]
        mod_parameters.drop(mod_parameters.index[0], inplace=True)
        # Module Area
        module_area = float(mod_parameters.loc[1, "Module_Area_[m2]"])
        # Technology
        tech = str(mod_parameters.loc[1, "Technology"])
        
        # Spectral responsivity
        spec_resp = pd.DataFrame(tables['[Spectral responsivity]'], columns=['wavelength', 'spec_resp'])
        spec_resp.drop(spec_resp.index[0], inplace=True)
        spec_resp = spec_resp.astype(float)
        spec_resp = pd.Series(spec_resp['spec_resp'].values, index=spec_resp['wavelength'].values)
        
        # Power Rating Matrix
        power_matrix = pd.DataFrame(tables['[Power Rating Matrix]'], columns=['gmean', 'temp', 'pmpp'])
        power_matrix.drop(power_matrix.index[0], inplace=True)
        power_matrix = power_matrix.astype(float)
        
        # Angle of incidence
        ar= float(tables['[Angle of incidence]'][0][1])
        
        # Thermal coefficients
        u0 = float(tables['[Thermal coefficients]'][0][1])
        u1 = float(tables['[Thermal coefficients]'][1][1])
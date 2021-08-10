# -*- coding: utf-8 -*-
"""
This file contains the functions to read the input data for energy rating and
PVsim for Callab results.

@author: dguzmanr
@modified: mriveraa
"""
# Importing libraries
from os.path import join, dirname
import pandas as pd
import numpy as np

def read_standard_locations(location):
    
    # =======================================================================
    # Definitions from the Standard
    # =======================================================================
    # Locations standard
    locs = ["Tropical humid", "Subtropical arid (desert)", "Subtropical coastal",
            "Temperate coastal", "High elevation (above 3 000 m)",
            "Temperate continental"]
    # Latitudes in the standard
    lats = [-1, 33.500000, 33.4, 56, 34, 57]
    # Longitud in the standard
    lons = [11, -112, 130.5, -4, 83, -112]
    # Elevation in the standard
    eles = [325, 368, 132, 169, 4968, 465]
    # File names of the standard's files
    loc_names = ["enra_tropical_humid.csv", "enra_subtropical_arid.csv",
                 "enra_subtropical_coastal.csv", "enra_temperate_coastal.csv",
                 "enra_highelevation.csv", "enra_temperate_continental.csv"]
    # Tilt angle
    pv_tilt = 20
    # Azimuth angle
    pv_azimuth = 180
    
    locations_std = {"loc" : loc_names[location],
                     "site_lat" : lats[location],
                     "site_lon" : lons[location],
                     "site_ele" : eles[location],
                     "site_name": locs[location],
                     "pv_tilt" : pv_tilt,
                     "pv_azimuth" : pv_azimuth
                     }
    
    return locations_std
    
    
def read_callab_data(path, folder_modules, data_file):
    """
    This function reads the data of modules from the Callab results.

    Parameters
    ----------
    path : String
        Path to where the Callab list is.
    folder_modules: String
        Name of folder where all the Callab results are
    data_file : String
        Name of the file with the Callab results summary.

    Returns
    -------
    list_callab : Pandas DataFrame
        Dataframe with the module's results from Callab.

    """
    # Get modules file
    # Reading callab modules
    file = join(path, data_file)
    list_callab = pd.read_excel(file)
    module_callab = list_callab.iloc[10]
    
    # Gettin data from xlsx file CalLab
    module_specs = {"alpha" : module_callab.TK_Pmpp_rel / 100,
                    "tech" : module_callab.Technology_tk,
                    "module_id_callab" : module_callab.Measurement_ID_tk,
                    "mod_area" : module_callab.Module_Area_tk 
                    }
    
    path_to = join(path, folder_modules)
    name_file = "%s_customer.txt" % module_specs["module_id_callab"]
    file_mod = join(path_to, name_file)
    
    # Reading file
    succes = False
    nrows = 45
    while not succes:
        try:
            mod_file = pd.read_csv(file_mod, skiprows=10,
                                   encoding="ISO-8859-1",
                                   header=0, sep="\t", nrows=nrows)
            succes = True
        except:
            nrows = nrows - 1
            pass
    mod_file.columns = ["temp", "isc", "uoc", "impp", "umpp", "pmpp",
                        "ff", "eta", "gmean", "tmod", "hyst"]
    
    mod_file['temp'] = mod_file['temp'].map(lambda x: x.rstrip(' °C'))
    mod_file['temp'] = pd.to_numeric(mod_file['temp'], downcast="float")
    
    return mod_file, module_specs


#def read_callab_stdfile(path):
#    import csv
#    from itertools import takewhile
#    
#    with open(path) as f:
#        csv_reader = csv.reader(f, delimiter="\t",skipinitialspace=True)
#        tables = {}
#        try:
#            while True:
#                title = next(f).rstrip()
#                stanza = takewhile(lambda row: row, csv_reader)
#                tables[title] = [next(stanza)] + \
#                                [row for row in stanza]
#        except StopIteration:
#            pass    # EOF while reading title or header row
#    
#    # Module parameters
#    parameters = pd.DataFrame(tables['[Module parameters]'])
#    mod_parameters = parameters.T
#    mod_parameters.columns = mod_parameters.iloc[0]
#    mod_parameters.drop(mod_parameters.index[0], inplace=True)
#    # Module Area
#    module_area = float(mod_parameters.loc[1, "Module_Area_[m2]"])
#    # Technology
#    tech = str(mod_parameters.loc[1, "Technology"])
#    
#    # Spectral responsivity
#    spec_resp = pd.DataFrame(tables['[Spectral responsivity]'], columns=['wavelength', 'spec_resp'])
#    spec_resp.drop(spec_resp.index[0], inplace=True)
#    spec_resp = spec_resp.astype(float)
#    spec_resp = pd.Series(spec_resp['spec_resp'].values, index=spec_resp['wavelength'].values)
#    
#    # Power Rating Matrix
#    power_matrix = pd.DataFrame(tables['[Power Rating Matrix]'], columns=['gmean', 'temp', 'pmpp'])
#    power_matrix.drop(power_matrix.index[0], inplace=True)
#    power_matrix = power_matrix.astype(float)
#    
#    # Angle of incidence
#    ar= float(tables['[Angle of incidence]'][0][1])
#    
#    # Thermal coefficients
#    u0 = float(tables['[Thermal coefficients]'][0][1])
#    u1 = float(tables['[Thermal coefficients]'][1][1])
    
#   return mod_parameters, spec_resp, power_matrix, ar, u0, u1, module_area, tech
    
def read_callab_stdfile(path):
    from io import StringIO
    import pandas as pd
    
    subfiles = [StringIO()]
    
    with open(path) as bigfile:
        for line in bigfile:
            if line.strip() == "": # blank line, new subfile                                                                                                                                       
                subfiles.append(StringIO())
            else: # continuation of same subfile                                                                                                                                                   
                subfiles[-1].write(line)
    
    df ={}
    df_names = ["Module Parameters", "Spectral responsivity",
                "Power Rating Matrix", "Angle of incidence",
                "Thermal coefficients"]
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
    # ID
    int_id = str(mod_parameters["Internal_ID"][0])
    
    
    # Spectral responsivity
    df['Spectral responsivity'].reset_index(level=0, inplace=True)
    spec_resp = df['Spectral responsivity']
    spec_resp.drop(0, inplace=True)
    spec_resp.columns = ['wavelength', 'spec_resp']
    spec_resp = spec_resp.astype(float)
    spec_resp = pd.Series(spec_resp['spec_resp'].values, index=spec_resp['wavelength'].values)
    
    
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

    return mod_parameters, spec_resp, power_matrix, ar, u0, u1, module_area, tech, int_id

def read_climate_locs(folder_locations, loc_name):
    """
    This function reads the climate locations from the standard based on the
    loc_name variable. The locations are given in IEC61853-4 [1].

    Parameters
    ----------
    folder_locations : String
        Path like. Path to where the standard locations files are.
    loc_name : String
        Name of the file for the location.

    Returns
    -------
    ret_df : Pandas DataFrame
        Dataframe with the location whather data information with Datetime
        index.

    References
    ----------
    .. [1] Energy Rating Standard IEC61853-4.
    """
    path_locations = join(dirname(__file__), folder_locations)
    file_loc = join(path_locations, loc_name)
    ret_df = pd.read_csv(file_loc, sep=",", encoding="ISO-8859-1")
    # Getting time from Hour solar
    ret_df["hour"] = ret_df["Hour solar"].apply(np.floor)
    MM = (ret_df["Hour solar"] - ret_df["hour"]) * 60
    ret_df["minute"] = MM.apply(np.floor)
    ret_df["second"] = ((MM - MM.apply(np.floor)) * 60).apply(np.floor)
    ret_df["time"] = pd.to_datetime(ret_df[["Year", "Month", "Day",
                                            "hour", "minute", "second"]])
    # Setting Datetimeindex
    ret_df = ret_df.set_index(pd.DatetimeIndex(ret_df.time))
    ret_df = ret_df.drop(["Year", "Month", "Day",
                          "hour", "minute", "second", "Hour solar", "time"],
                         axis=1)
    return ret_df


def change_names_climate_df(climate_df):
    """
    This function changes the names of the columns from the
    Energy rating standard IEC61853-4 [1] locations in order to be used in
    the PVsim sumulation.

    Parameters
    ----------
    climate_df : Pandas DataFrame
        DataFrame with the location info from the standard.

   climate_df : Pandas DataFrame
        A copy of "climate_df" input with different column names and 1 extra
        column:"dhor" (diffuse horizontal irradiance).

    References
    ----------
    .. [1] Energy Rating Standard IEC61853-4.
    """
    # Changing the column names for the simulation
    translation = {'Gh (W/m2)': 'ghor',
                   'Bh (W/m2)': 'ihor',
                   'Ambient temperature (øC)': 'T_amb',
                   'Sun elevation (ø)': 'elev_sun',
                   'G (W/m2)': 'G_tlt',
                   'B (W/m2)': 'I_tlt',
                   'Wind speed (m/s)': "wind",
                   'Sun incidence angle (ø)': "IncidentAngle"}
    climate_df.rename(columns=translation, inplace=True)
    # Adding additional columns for the simulation
    climate_df["dhor"] = climate_df["ghor"] - climate_df["ihor"]
    climate_df["D_tlt"] = climate_df["G_tlt"] - climate_df["I_tlt"]
    return climate_df

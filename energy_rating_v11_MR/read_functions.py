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
from io import StringIO

def read_standard_locations(location):
    """
    This function returns the paramaters given by the standard climate file
    from the norm IEC61853-4.

    Parameters
    ----------
    location: Float
        Number of the location to be read:
        0 : 'Tropical humid', 1: 'Subtropical arid (desert)',
        2 : 'Subtropical coastal', 3: 'Temperate coastal',
        4 : 'High elevation (above 3 000 m)', 5: 'Temperate continental'

    Returns
    -------
    locations_std : Dictionary
        Parameters from the chosen location are given: file name, azimuth,
        tilt angle, elevation, latitude, longitude and site name.

    References
    ----------
    .. [1] Energy Rating Standard IEC61853-4
    """
    # =======================================================================
    # Definitions from the Standard
    # =======================================================================
    # Locations standard
    locs = ["Tropical humid", "Subtropical arid (desert)",
            "Subtropical coastal", "Temperate coastal",
            "High elevation (above 3 000 m)",
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


def read_callab_stdfile(path):
    """
    This function reads the file given by CalLab.

    Parameters
    ----------
    path: String
        The path to the CalLab file.

    Returns
    -------
    mod_paramters: Pandas DataFrame
        Information about the measured module, e.g: Internal_ID, Technology,
        Measures, Area, etc.
    spec_resp: Series
        Module's Spectral Response, where the index are the wavelenghts (nm).
    power_matrix: Pandas DataFrame
        Power matrix measured in CalLab, with irradiance('gmean') in W/m²,
        temperature('temp') in °C and maximum power point('pmpp') in W.
    a_r : Float
        Angular response factor. The default is 0.16.
    u0 : Float
        Combined heat loss factor coefficient. The default value is one
        determined by Faiman for 7 silicon modules. [W/(m^2 C)].
    u1 : Float
        Combined heat loss factor influenced by wind. The default value is one
        determined by Faiman for 7 silicon modules. [(W/m^2 C)(m/s)].
    module_area: Float
        Module area in m²
    tech: String
        Module's technology
    int_id: String
        Name or ID of the module.
    """

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
    loc_name variable. The locations are given in [1].

    Parameters
    ----------
    folder_locations : String
        Path like. Path to where the standard locations files are.
    loc_name : String
        Name of the file for the location.

    Returns
    -------
    ret_df : Pandas DataFrame
        Dataframe with the location weather data information with Datetime
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
    the simulation.

    Parameters
    ----------
    climate_df : Pandas DataFrame
        DataFrame with the location info from the standard.

   climate_df : Pandas DataFrame
        A copy of "climate_df" input with different column names and extra
        columns:"dhor" (diffuse horizontal irradiance) and
        "D_tlt" (diffuse tilted irradiance).

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

# -*- coding: utf-8 -*-
"""
Climate Specific Energy Rating (CSER)

@author: dguzmanr
@modified: mriveraa
"""
# Importing the Steps Function
import sim_steps
# Importing the Energy rating functions
import energy_rating_functions as energy_rating
# Importing read functions
import read_functions
import pandas as pd
# Importing execution functions
import utils
import plotting
# Import Module
import os



def get_ini_data(module_df, eta, module_area, folder_locations, site_name):
    """
    This function reads/gets the initial dataframe from the standard climate
    files.
    Calculates the nominal power, generates the ETA matrix and it's
    interpolation object.

    Parameters
    ----------
    module_df : Pandas DataFrame
        The power matrix data: irradiance, temperature and power
        measurements.
    eta : Boolean
        If false, the function calculates the efficiency ETA.
    module_area: Float
        Module's area in m².
    folder_locations: String/path
        The name or path of the folder with the six standard climate data
        files.
    site_name: String
        Name of the standard climate data file to read.

    Returns
    -------
    eta_interpolated: Object.
        This object gets the ETA if a irradiance and temperature are given.
        Please check the function "get_eta_interpolation"..
    pnom : Float
        Module's nominal power.
    eta_matrix: Pandas DataFrame
        Matrix with ETA realative to STC at different irradiances and
        temperature levels.
    climate_data : Pandas DataFrame
        DataFrame with the data from the standard climate given by the
        IEC61853-4.
        
    """

    # Get ETA interpolation object from CalLab measurements
    eta_interpolated, pnom, eta_matrix =\
        energy_rating.get_eta_interpolation(module_df= module_df,
                                            module_area= module_area,
                                            eta_calc= eta)

    # Reading standard climate data
    climate_data = read_functions.read_climate_locs(
        folder_locations=folder_locations,
        loc_name=site_name)
    
    # Changing names to climate dataframe for simulation
    climate_data = read_functions.change_names_climate_df(
        climate_df=climate_data)
    return (eta_interpolated, pnom, eta_matrix, climate_data)


def get_simulation(climate_data, lat, lon, ele, tech, pnom, mod_area,
                   eta_interpolated, u0, u1, a_r, power_matrix, eta_matrix,
                   pv_azimuth=180, pv_tilt=20, spec_resp_factor=1.0):
    """
    This function calls for the Energy Rating steps.
    Please check the function ersim_dc_steps() in sim_steps.py
    
    """

    cser_er, eta_avg_er, sim_er_df = sim_steps.ersim_dc_steps(
        climate_data=climate_data.copy(),
        pv_tilt=pv_tilt,
        eta_interpolated=eta_interpolated,
        pnom=pnom,
        mod_area=mod_area,
        u0=u0,
        u1=u1,
        a_r=a_r,
        spec_resp_factor=spec_resp_factor,
        power_matrix= power_matrix,
        eta_matrix=eta_matrix)
    # Creating a DataFrame with results
    ret_df = pd.DataFrame(columns=["cser_ER", "eta_avg_ER"])
    ret_df.at[0, "cser_ER"] = cser_er
    ret_df.at[0, "eta_avg_ER"] = eta_avg_er
    return sim_er_df, ret_df


def simulation_er(folder):
    """
    This function calls for the simulation that follow the method in the
    Energy rating standard IEC61853-3, it takes a given data file(s) with
    measurements done by Callab.
    
    Returns
    -------
    Figures:
        Efficiency ETA for each standard climate, e.g:
            ETA_Module-name_Standard-climate-name.png
            ETA_Standard_Climates_Module-name.png
        Climate Specific Energy Rating from the six standard climates, e.g:
            CSER_Module-name.png
            CSER_RoundRobin_format_Module-name.png
            CSER_Summary.png
        Average ETA from all standard climates as bar plot comparision with
        all module input data files, e.g:
            ETA_Summary.png
    Excel file:
        ETA and CSER values of all standard climates for each module input
        data, e.g:
            results_cser_eta.xlsx
    """
    # =======================================================================
    # Folder and paths info
    # =======================================================================
    # Folder with the standard's files
    folder_locations = "the_standard"
    # Change the directory
    os.chdir(folder)
    #Creating directory
    os.makedirs('results/plots', exist_ok=True)
    
    #Create data frame for results
    climate = ['Tropical humid', 'Subtropical arid (desert)',
               'Subtropical coastal', 'Temperate coastal',
               'High elevation (above 3 000 m)', 'Temperate continental']
    results_df_cser = pd.DataFrame({"Std_climate": climate})
    results_df_eta = pd.DataFrame({"Std_climate": climate})

    # =======================================================================
    # Simulation for the 6 standard climates
    # =======================================================================

    # iterate through all file
    for file in os.listdir():
        # Check whether file is in text format or not
        if file.endswith(".txt"):
            file_path = f"{folder}\{file}"
    
            (mod_parameters, spec_resp, power_matrix, ar,
             u0, u1, module_area, tech, int_id) = read_functions.read_callab_stdfile(path = file_path)
            print('Module: ', int_id)
            cser = []
            eta = []
            eta_dataframes = {}

            for location in range(6):
                print("Location #", location)
                std_location = read_functions.read_standard_locations(location)
                # Getting initial data
                (eta_interpolated, pnom, eta_matrix,
                 climate_data) = get_ini_data(
                            module_df = power_matrix,
                            eta= False,
                            module_area = module_area,
                            folder_locations=folder_locations,
                            site_name=std_location["loc"])
                            
                # Running simulations
                sim_er_df, ret_df = get_simulation(
                    climate_data=climate_data,
                    lat=std_location["site_lat"],
                    lon=std_location["site_lon"],
                    ele=std_location["site_ele"],
                    tech=tech,
                    pnom=pnom,
                    mod_area=module_area,
                    eta_interpolated=eta_interpolated,
                    u0=u0,
                    u1=u1,
                    pv_azimuth=std_location["pv_azimuth"],
                    pv_tilt=std_location["pv_tilt"],
                    a_r=ar,
                    spec_resp_factor=spec_resp,
                    power_matrix= power_matrix,
                    eta_matrix=eta_matrix)
                
                # Results
                cser.append(float(ret_df["cser_ER"]))
                eta.append(float(ret_df["eta_avg_ER"]))
    
                # Plot ETA
                plotting.plot_eta(df = sim_er_df,
                                  res_folder= rf'{folder}\results\plots',
                                  module_id = int_id,
                                  location = std_location)
                
                eta_dataframes[std_location["site_name"]] = sim_er_df

            results_df_cser["cser_%s"%(int_id)] = cser
            results_df_eta["eta_%s"%(int_id)] = eta
            
            # Plot CSER
            plotting.plot_cser(df = results_df_cser,
                              res_folder= rf'{folder}\results\plots',
                              module_id = int_id)
            
            # Round Robin comparision plot 
            # (other format of plotting.plot_cser())
            plotting.round_robin_plot(df=results_df_cser,
                              module_id=int_id,
                              res_folder=rf'{folder}\results')
    
            #Plot ETA from all the standard sites
            plotting.eta_all_sites(df = eta_dataframes,
                               module_id = int_id,
                               res_folder= rf'{folder}\results\plots')

    # Excel file
    utils.write_results(df_1 = results_df_cser,
                        df_2 = results_df_eta,
                        folder= rf'{folder}\results')

    # Summary plot
    plotting.plot_summary_cser(df= results_df_cser,
                               res_folder= rf'{folder}\results')
    plotting.plot_summary_eta(df= results_df_eta,
                              res_folder= rf'{folder}\results')

    return
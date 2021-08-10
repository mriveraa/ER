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
    # Get the interpolation object with eta, temp, irradiance, etc
    # From CalLab measurements
    eta_interpolated, pnom, eta_matrix, hey_matrix, alpha =\
        energy_rating.get_eta_interpolation(module_df= module_df,
                                            module_area= module_area,
                                            eta_calc= eta)

    # Reading climate data
    climate_data = read_functions.read_climate_locs(
        folder_locations=folder_locations,
        loc_name=site_name)
    
    # Changing names to climate df for simulation
    climate_data = read_functions.change_names_climate_df(
        climate_df=climate_data)
    return (eta_interpolated, pnom, eta_matrix, hey_matrix, climate_data, alpha)


def get_simulation(climate_data, lat, lon, ele, alpha, tech, pnom, mod_area,
                   eta_interpolated, u0, u1, a_r, power_matrix, pv_azimuth=180, pv_tilt=20,
                   spec_resp_factor=1.0):

    # =======================================================================
    # Energy rating Module
    # =======================================================================
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
        power_matrix= power_matrix)
    # Creating a DataFrame with results
    ret_df = pd.DataFrame(columns=["cser_ER", "eta_avg_ER"])
    ret_df.at[0, "cser_ER"] = cser_er
    ret_df.at[0, "eta_avg_ER"] = eta_avg_er
    return sim_er_df, ret_df



def simulation_er(folder):

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
    
            cser = []
            eta = []
            for location in range(6):
                
                std_location = read_functions.read_standard_locations(location)
                # Getting initial data
                (eta_interpolated, pnom, eta_matrix, hey_matrix,
                climate_data, alpha) = get_ini_data(
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
                    alpha=alpha,
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
                    power_matrix= power_matrix)
                
                # Results
                cser.append(float(ret_df["cser_ER"]))
                eta.append(float(ret_df["eta_avg_ER"]))
    
                # Plot ETA
                plotting.plot_eta(df = sim_er_df,
                                  res_folder= rf'{folder}\results\plots',
                                  module_id = int_id,
                                  location = std_location)

            results_df_cser["cser_%s"%(int_id)] = cser
            results_df_eta["eta_%s"%(int_id)] = eta
            
            # Plot CSER
            plotting.plot_cser(df = results_df_cser,
                              res_folder= rf'{folder}\results\plots',
                              module_id = int_id)
    
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
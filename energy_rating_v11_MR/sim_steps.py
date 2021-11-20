# -*- coding: utf-8 -*-
"""
This file contains the simulation steps for the Energy rating standard.

@author: dguzmanr
@modified: mriveraa
"""
# Importing the Energy rating functions
import energy_rating_functions as energy_rating
# Importing utils
import utils


def ersim_dc_steps(climate_data, eta_interpolated, pnom, mod_area, u0, u1, a_r,
                   power_matrix, eta_matrix, pv_tilt=20, spec_resp_factor=1.0):
    """
    This function has the steps for Energy Rating.

    Parameters
    ----------
    climate_data : Pandas DataFrame
        Climate data.
    eta_interpolated: Object.
        This object gets the ETA if a irradiance and temperature are given.
        Please check the function "get_eta_interpolation".
    pnom : Float
        Module's nominal power.
    mod_area: Float
        Module's area in m$^2$.
    u0 : numeric, default 25.0
        Combined heat loss factor coefficient. The default value is one
        determined by Faiman for 7 silicon modules. [W/(m^2 C)].
    u1 : numeric, default 6.84
        Combined heat loss factor influenced by wind. The default value is one
        determined by Faiman for 7 silicon modules. [(W/m^2 C)(m/s)].
    a_r : Float, optional
        Angular response factor. The default is 0.16.
    power_matrix : Pandas DataFrame
        Power Matrix measured by Callab containing also the calcualted 'eta'
    eta_matrix: Pandas DataFrame
        Power Matrix with ETA values as pivot, irradiances as index and
        temperatures as columns.
    pv_tilt : Float, optional
        PV tilt angle. The default is 20.
    spec_resp_factor : float, optional
        Spectral response from the module. The default is 1.0.

    Returns
    -------
    cser : Float
        Climate Specific Energy Rating.
    eta_avg : Float
        Average ETA.
    climate_data : Pandas DataFrame
        DataFrame from the standard climate file including the columns
        calculated from the simulation: 'ghor', 'D_tlt', 'b_aoi', 'g_aoi',
        'spectral_modifier', 'g_spec', 'T_mod', 'eta_rel', 'eta' & 'Pout'.

    """
    # AOI correction (Martin & Ruiz correction)
    climate_data = energy_rating.aoi_correction(
        climate_df=climate_data,
        a_r=a_r,
        pv_tilt=pv_tilt)
    
    #Spectral correction
    climate_data = energy_rating.spec_correction(
        climate_df=climate_data,
        spec_resp_factor=spec_resp_factor)
    
    # Module Temperature
    climate_data = energy_rating.temp_correction(
        climate_df=climate_data,
        u0=u0, u1=u1)

    # Instantaneous Module power
    climate_data = energy_rating.module_power_er(
        climate_df=climate_data,
        eta_interpolated=eta_interpolated,
        power_matrix=power_matrix,
        module_area = mod_area)

    # Calculating Climate Specific Energy Rating (CSER)
    # Droping NaN values
    climate_data = climate_data.dropna()
    cser = utils.get_cser(power_series=climate_data["Pout"],
                          gpoa_series=climate_data["G_tlt"],
                          pnom=pnom)
    eta_avg = ((climate_data.Pout / mod_area ) / climate_data.G_tlt).mean()

    return cser, eta_avg, climate_data

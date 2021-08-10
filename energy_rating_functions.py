# -*- coding: utf-8 -*-
"""
This file contains the functions for the Module's energy rating calculations
based on IEC61853.

@author: dguzmanr
@modified: mriveraa
"""
# Import libraries
from scipy.stats import linregress

# Importing the IEC91853 standard's code
import pvpltools_python.pvpltools.iec61853 as std


def aoi_correction(climate_df, a_r, pv_tilt=20):
    """
    This function AOI corrects the Global irradiance in the POA based on the
    Martin and Ruiz functions from iec61853.py file based on
    the Energy rating standard IEC61853-3 [1]. It corrects the direct
    irradiance in POA and the Diffuse irradiance in POA separately.

    For more detailes, please check the .py file with the functions and
    the document of the standard.

    Parameters
    ----------
    climate_df : Pandas DataFrame
        DataFrame with the location info from the standard and a column named
        "I_tlt" (Direct irradiance in POA AOI corrected) and "D_tlt" (Diffise
        irradiance in POA).
    pv_tilt: float, optional.
        PV tilt angle. The default is 20.
    a_r : Float, optional
        Angular response factor. The default is 0.16.

    Returns
    -------
    climate_df : Pandas DataFrame
        A copy of "climate_df" with 3 extra columns: "b_aoi" (direct
        irradiance in POA aoi corrected), "d_aoi" (Diffuse irradiance
        in POA aoi corrected) and "g_aoi" (Global irradiance in POA aoi
        corrected).

    References
    ----------
    .. [1] Energy Rating Standard IEC61853-3.
    """
    # Getting the direct incident angle modifier
    b_mod = std.martin_ruiz(aoi=climate_df.IncidentAngle, a_r=a_r)
    # Direct in POA correction
    climate_df["b_aoi"] = climate_df["I_tlt"] * b_mod
    # Getting the diffuse incident angle modifier
    d_mod_sky, d_mod_ground = std.martin_ruiz_diffuse(surface_tilt=pv_tilt,
                                                      a_r=a_r, c1=0.4244,
                                                      c2=None)
    # Diffuse in POA correction
    climate_df["d_aoi"] = climate_df["D_tlt"] * d_mod_sky
    # Global in POA AOI correction
    climate_df["g_aoi"] = climate_df["d_aoi"] + climate_df["b_aoi"]
    return climate_df


def spec_correction(climate_df, spec_resp_factor=1.0):
    """
    Corrects the global irradiance in the POA spectrally. It takes the
    functions from iec61853.py file based on spectral correction model from
    the Energy rating standard IEC61853-3 [1].

    For more detailes, please check the .py file with the functions and
    the document of the standard.

    Parameters
    ----------
    climate_df : Pandas DataFrame
        DataFrame with the location info from the standard and a column named
        "g_aoi" (Global irradiance in POA AOI corrected).
    spec_resp_factor : float, optional
        Spectral response from the module. The default is 1.0.

    Returns
    -------
    climate_df : Pandas DataFrame
        A copy of "climate_df" with an extra column named "g_spec".

    References
    ----------
    .. [1] Energy Rating Standard IEC61853-3.
    """
    # Get spectral dataframe
    spec_resp = get_spectral_df(climate_df=climate_df)
    # Convert spectral from std to band
    spec_resp_banded = std.convert_to_banded(spectral_reponse=spec_resp)
    # flat Spectral Responsivity beyond limts
#    sr = pd.Series([spec_resp_factor, spec_resp_factor], [200, 5000])
#    fsr = std.convert_to_banded(sr)
    fsr = std.convert_to_banded(spec_resp_factor)
    # Get the spectral modifier
    spectral_modifier = std.calc_spectral_factor(spec_resp_banded, fsr)
    # Global in POA Spectral correction
    climate_df["g_spec"] = climate_df["g_aoi"] * spectral_modifier
    return climate_df


def get_spectral_df(climate_df):
    """
    Extracts the Spectral DataFrame from the climate_df DataFrame from the
    Energy rating standard IEC61853-4 [1] locations.

    Parameters
    ----------
    climate_df : Pandas DataFrame
        DataFrame with the location info from the standard.

    Returns
    -------
    df_spec : Pandas DataFrame
        Sum of the irradiance divided by longitude of spectrum, lower limits
        as index and sum as column values.

    References
    ----------
    .. [1] Energy Rating Standard IEC61853-4.
    """
    # Get the spectral columns
    df_spec = climate_df[[
        'Inclined global spectral irradiance,306.8-327.8nm',
        '327.8-362.5nm', '362.5-407.5nm', '407.5-452.0nm', '452.0nm-517.7nm',
        '517.7-540.0nm', '540.0-549.5nm', '549.5-566.6nm', '566.6-605.0nm',
        '605.0-625.0nm', '625.0-666.7nm', '666.7-684.2nm', '684.2-704.4nm',
        '704.4-742.6nm', '742.6-791.5nm', '791.5-844.5nm', '844.5-889.0nm',
        '889.0-974.9nm', '974.9-1045.7nm', '1045.7-1194.2nm',
        '1194.2-1515.9nm', '1515.9-1613.5nm', '1613.5-1964.8nm',
        '1964.8-2153.5nm', '2153.5-2275.2nm', '2275.2-3001.9nm',
        '3001.9-3635.4nm', '3635.4-3991.0nm', '3991.0-4605.65nm']]
    df_spec = df_spec.reset_index(drop=True)
    # Transposing columns
    df_spec = df_spec.T
    df_spec.index = [
        306.8, 327.8, 362.5, 407.5, 452.0,
        517.7, 540.0, 549.5, 566.6, 605.0,
        625.0, 666.7, 684.2, 704.4, 742.6,
        791.5, 844.5, 889.0, 974.9, 1045.7,
        1194.2, 1515.9, 1613.5, 1964.8, 2153.5,
        2275.2, 3001.9, 3635.4, 3991.0]
    # Get total irradiance by spectral limits
    df_spec = df_spec.sum()
    return df_spec


def temp_correction(climate_df, u0, u1):
    """
    This function calls the temperature correction function from
    iec61853.py file based on faiman model from the
    Energy rating standard IEC61853-3 [1].

    For more detailes, please check the .py file with the faiman function and
    the document of the standard.


    Parameters
    ----------
    climate_df : Pandas DataFrame
        DataFrame with "g_aoi" (irradiance AOI corrected), "T_amb" (Ambient
        temperature) and "wind" column.

    Returns
    -------
    climate_df : Pandas DataFrame
        Copy of "climate_df" with an extra column named "T_mod" with
        the module's temperature calculated.

    References
    ----------
    .. [1] Energy Rating Standard IEC61853-3.
    """
    # Get module temperature
    climate_df["T_mod"] = std.faiman(poa_global=climate_df["g_aoi"],
                                     temp_air=climate_df["T_amb"],
                                     wind_speed=climate_df["wind"],
                                     u0=u0, u1=u1)
    return climate_df


def module_power_er(climate_df, eta_interpolated, pnom, power_matrix):
    """
    Calculates the instantaneous power from the energy rating simulation. This
    function is based on the equation 8.5 from Energy rating standard
    documentation:

        n(G,T) = P(G,T)/G

        Where:
            P(G,T) is the instantaneous power at certain level of irradiance
                    and temperature
            G is the Globlal irradiance in the plane of array
            n(G,T) is the efficiency of the module at that irradiance and
                    temperature levels.

    for more details, please check [1].

    Parameters
    ----------
    climate_df : Pandas DataFrame
        DataFrame containing the global irradiance in POA spectrally corrected
        ("g_spec"), the Module temperature calculated ("T_mod") and the global
        iirradiance in POA without corrections ("G_tlt"), based on [1].
    eta_interpolated: Object.
        This object gets the ETA if a irradiance and temperature are given.
        Please check the function "get_eta_interpolation"
    pnom: Float.
        Module's nominal power in kWp.

    Returns
    -------
    climate_df : Pandas DataFrame
        a copy of climate_df DataFrame with an extra column named "Pout",
        containing the instantaneous power calculated.

    References
    ----------
    .. [1] Energy Rating Standard IEC61853-3.
    """
    # Calculate instantaneous power at G and T
    climate_df["eta_rel"] = eta_interpolated(climate_df[["g_spec"]],
                                         climate_df[["T_mod"]])
    climate_df["eta"] = (climate_df["eta_rel"] * power_matrix.query("g_round == 1000")["eta"].mean())
    
    climate_df["Pout"] = climate_df["eta_rel"] * climate_df["G_tlt"] * pnom
    return climate_df


def get_eta_interpolation(module_df, module_area, eta_calc):
    """
    This function returns the ETA interpolated object using the function in
    iec61853.py file based on the bilinear interpolation from the
    Energy rating standard IEC61853-3 [1].

    For more detailes, please check the .py file with the bilinear
    interpolation code.

    Parameters
    ----------
    module_id_callab : String
        Measurement_ID_tk module results from Callab.
    folder_callab: String
        Path to the callab modules information.
    folder_module: String
        Name of the module with the callab measurements files.

    Returns
    -------
    eta_interpolated: Object.
        This object gets the ETA if a irradiance and temperature are given.
    pnom: Float
        Nominal power measured in kWp.
    eta_matrix: Pandas DataFrame
        Matrix with ETA realative to STC at different irradiances and
        temperature levels.
    hey_matrix: Pandas DataFrame
        Matrix with eta and Gpoa values for HEY model[2].

    References
    ----------
    .. [1] Energy Rating Standard IEC61853-3.
    .. [2] Heydenreich, et al. "Describing the wolrd with three parameters:
            a new approach to PV module power modeling". 2008.
    """
 
    
    if eta_calc == False:
        # Calculate ETA (relative efficiency)     
        module_df['eta'] = ((module_df["pmpp"] / module_area ) / module_df["gmean"])
        

    module_df["g_round"] = module_df["gmean"].round(decimals=-2)
    module_df["t_round"] = module_df["temp"].round()
    module_df["t_round"] = 5 * round(module_df["t_round"] / 5)
    module_df = module_df.drop_duplicates(["g_round", "t_round"])
    # get pmax from measurements
    pnom = module_df.query('g_round == 1000 and t_round == 25')["pmpp"].values
    
    
    #Calculate the power temperature coefficient (alpha)
    x = linregress(module_df["temp"], module_df["pmpp"])
    slope = x[0]
    alpha = slope/pnom
        
    # For HEY model
    hey_matrix = module_df.query('t_round == 25')[["gmean", "eta", "g_round"]]
    hey_matrix["eta_rel"] = (hey_matrix["eta"] /
                             hey_matrix.query("g_round == 1000")["eta"].values)
    # Get the eta relative matrix interpolated
    eta_matrix = module_df.pivot(index='g_round',
                                columns='t_round',
                                values="eta")
    eta_matrix = (eta_matrix /
                  float(hey_matrix.query("g_round == 1000")["eta"].values))
    if 45 in eta_matrix.columns:
        eta_matrix.drop(columns=[45], inplace=True)
    # get the bilinear interpolation
    eta_interpolated = std.BilinearInterpolator(matrix=eta_matrix)
    return eta_interpolated, float(pnom)/1000, eta_matrix, hey_matrix, alpha



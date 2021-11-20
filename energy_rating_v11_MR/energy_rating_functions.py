# -*- coding: utf-8 -*-
"""
This file contains the functions for the Module's energy rating calculations
based on IEC61853.

@author: dguzmanr
@modified: mriveraa
"""
# Import libraries
# Importing the IEC91853 standard's code
import pvpltools_python.pvpltools.iec61853 as std
import pandas as pd

def aoi_correction(climate_df, a_r, pv_tilt=20):
    """
    This function AOI corrects the Global irradiance in the POA based on the
    Martin and Ruiz functions from iec61853.py file based on
    the Energy rating standard IEC61853-3 [1]. It corrects the direct
    irradiance in POA and the Diffuse irradiance in POA separately.

    For more detailes, please check the iec61853.py file with the functions
    and the document of the standard.

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
    .. [1] Energy Rating Standard IEC61853-3
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


def spec_correction(climate_df, spec_resp_factor=None):
    """
    Corrects the global irradiance in the POA spectrally. It takes the
    functions from iec61853.py file based on spectral correction model from
    the Energy rating standard IEC61853-3 [1].

    For more detailes, please check the iec61853.py file with the functions
    and the document of the standard.

    Parameters
    ----------
    climate_df : Pandas DataFrame
        DataFrame with the location info from the standard and a column named
        "g_aoi" (Global irradiance in POA AOI corrected).
    spec_resp_factor : float, optional
        Spectral response from the module. When 'None' the default would be 1.0.

    Returns
    -------
    climate_df : Pandas DataFrame
        A copy of "climate_df" with an extra column named "g_spec".

    References
    ----------
    .. [1] Energy Rating Standard IEC61853-3.
    """

    # Get just the spectral irradiance
    spec_bands = [
        'Inclined global spectral irradiance,306.8-327.8nm',
        '327.8-362.5nm', '362.5-407.5nm', '407.5-452.0nm', '452.0nm-517.7nm',
        '517.7-540.0nm', '540.0-549.5nm', '549.5-566.6nm', '566.6-605.0nm',
        '605.0-625.0nm', '625.0-666.7nm', '666.7-684.2nm', '684.2-704.4nm',
        '704.4-742.6nm', '742.6-791.5nm', '791.5-844.5nm', '844.5-889.0nm',
        '889.0-974.9nm', '974.9-1045.7nm', '1045.7-1194.2nm',
        '1194.2-1515.9nm', '1515.9-1613.5nm', '1613.5-1964.8nm',
        '1964.8-2153.5nm', '2153.5-2275.2nm', '2275.2-3001.9nm',
        '3001.9-3635.4nm', '3635.4-3991.0nm', '3991.0-4605.65nm']
    spec_g = pd.DataFrame()
    for band in spec_bands:
        spec_g[band]= climate_df[band]

    # Convert the spectral response to banded (29 bands)
    if spec_resp_factor is None:
        spec_resp_factor = 1.0
        # flat Spectral Responsivity beyond limts
        sr = pd.Series([spec_resp_factor, spec_resp_factor], [200, 5000])
        fsr = std.convert_to_banded(sr)
    else:
        fsr = std.convert_to_banded(spec_resp_factor)
    
    c_j = []
    #Get the spectral modifier for each hour (C_j) - EQ.6
    for i in range(8760):
        spectral_factor = std.calc_spectral_factor(spec_g.iloc[i], fsr)
        c_j.append(spectral_factor)
        
    
    climate_df["spectral_modifier"] = c_j
    climate_df["g_spec"] = climate_df["spectral_modifier"] * climate_df["g_aoi"]
    climate_df = climate_df.fillna(0)

    return climate_df


def temp_correction(climate_df, u0, u1):
    """
    This function calls the temperature correction function from
    iec61853.py file based on faiman model from the
    Energy rating standard IEC61853-3 [1].

    For more detailes, please check the iec61853.py file with the faiman
    function and the document of the standard.

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


def module_power_er(climate_df, eta_interpolated, power_matrix, module_area):
    """
    Calculates the instantaneous power from the energy rating simulation. This
    function is based on the equation 8.5 from Energy rating standard
    documentation:

        n(G,T) = P(G,T)/G

        Where:
            P(G,T) is the instantaneous power at certain level of irradiance
                    and temperature
            G is the corrected global irradiance in the plane of array
            n(G,T) is the efficiency of the module at that irradiance and
                    temperature levels.

    for more details, please check [1].

    Parameters
    ----------
    climate_df : Pandas DataFrame
        DataFrame containing the global irradiance in POA spectrally corrected
        ("g_spec"), the Module temperature calculated ("T_mod") based on [1].
    eta_interpolated: Object.
        This object gets the ETA if a irradiance and temperature are given.
        Please check the function "get_eta_interpolation"

    Returns
    -------
    climate_df : Pandas DataFrame
        a copy of climate_df DataFrame with an extra column named "Pout",
        containing the instantaneous power calculated.

    References
    ----------
    .. [1] Energy Rating Standard IEC61853-3.
    """
    # Calculate relative ETA at G and T
    climate_df["eta_rel"] = eta_interpolated(climate_df[["g_spec"]],
                                         climate_df[["T_mod"]])

    # Calculates ETA
    climate_df["eta"] = (climate_df["eta_rel"] 
                         * power_matrix.query("g_round == 1000 and t_round == 25")["eta"].values)

    climate_df["Pout"] = climate_df["eta"] * climate_df["g_spec"] *module_area

    return climate_df


def get_eta_interpolation(module_df, module_area, eta_calc):
    """
    This function returns the ETA interpolated object using the function in
    iec61853.py file based on the bilinear interpolation from the
    Energy rating standard IEC61853-3 [1].

    For more detailes, please check the iec61853.py file with the bilinear
    interpolation code.

    Parameters
    ----------
    module_df: Pandas DataFrame
        Power matrix with the irradiance, temperature and power measurements.
    module_area: Float
        Module area in m²
    eta_calc: Boolean
        If False then efficiency ETA is calcualted from the power matrix

    Returns
    -------
    eta_interpolated: Object.
        This object gets the ETA if a irradiance and temperature are given.
    pnom: Float
        Nominal power measured in kWp.
    eta_matrix: Pandas DataFrame
        Matrix with ETA realative to STC at different irradiances and
        temperature levels.

    References
    ----------
    [1] Energy Rating Standard IEC61853-3.
    """

    if eta_calc == False:
        # Calculate ETA 
        module_df['eta'] = (module_df["pmpp"] / module_area)/ module_df["gmean"]


    module_df["g_round"] = module_df["gmean"].round(decimals=-2)
    module_df["t_round"] = module_df["temp"].round()
    module_df["t_round"] = 5 * round(module_df["t_round"] / 5)
    module_df = module_df.drop_duplicates(["g_round", "t_round"])
    
    # get nominal power from measurements
    pnom = module_df.query('g_round == 1000 and t_round == 25')["pmpp"].values


    # Get the eta relative matrix interpolated
    eta_matrix = module_df.pivot(index='g_round',
                                columns='t_round',
                                values="eta")
    eta_matrix = (eta_matrix /
                  float(module_df.query("g_round == 1000 and t_round ==25")["eta"].values))

    # get the bilinear interpolation
    eta_interpolated = std.BilinearInterpolator(matrix=eta_matrix)

    return eta_interpolated, float(pnom)/1000, eta_matrix
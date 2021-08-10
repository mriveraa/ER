# -*- coding: utf-8 -*-
"""
This file contains the some useful functions for the Energy Rating and PV
simulation.

    - Climate Specific Energy Rating (CSER) based on the Equation 20 from
        IEC61853-3[2].


    References
    ----------
    .. [2] Energy Rating Standard IEC61853-3.

@author: dguzmanr
@modified: mriveraa
"""
import pandas as pd
from os.path import join
import xlsxwriter

def write_results(df_1, df_2, folder):
    """
    This function creates a excel file with .

    Parameters
    ----------
    df_in: DataFrame
        Data frame containing the timestamps, gpyr_col_name and
        g_si_col_name before and after correction ("G_si_corr_calib",
        "G_si_corr_aoi" and "G_si_corr_am").
    res_folder: String
        Path to file where results want to be saved.
    

    Returns
    -------
    results.xlsx : Excel file
        Excel file with .

    Example
    -------
    >>> utils.write_results(df_in = results_df,
    >>>                     mod_parameters = mod_parameters,
    >>>                     folder= r'Results/' )
    """
    
    results = 'results_cser_eta.xlsx'
    file = join(folder, results)
    writer = pd.ExcelWriter(file, engine='xlsxwriter')
    workbook=writer.book
    worksheet=workbook.add_worksheet('Results')
    writer.sheets['Results'] = worksheet
    
    worksheet.write_string(0, 0, "CSER")
    df_1.to_excel(writer,sheet_name='Results',startrow=1 , startcol=0)
    worksheet.write_string(df_1.shape[0] + 6, 0, "ETA")
    df_2.to_excel(writer,sheet_name='Results',startrow=df_1.shape[0] + 7, startcol=0)
    
    writer.save()
    return


def get_cser(power_series, gpoa_series, pnom):
    """
    This functions calculates the Climate Specific Energy Rating (CSER) based
    on the Equation 20 from the IEC61853-3 [1] standard. Need a Instantaneous
    Power series, a Irradiance in plane of Array Series, module data from
    CalLab excel document or nominal power measued.

    Parameters
    ----------
    power_series : Pandas series
        Instantaneous Power calculated.
    gpoa_series : Pandas series.
        Irradiance in Plane of Array.
    pnom : Float.
        Module's nominal power.

    Returns
    -------
    cser : Float
        Climate Specific Energy Rating Value for that module in that location.

    References
    ----------
    .. [1] Energy Rating Standard IEC61853-3.

    """
    if len(power_series.dropna()) != len(gpoa_series.dropna()):
        print("Different series' length. Please make same length.")
        return
    # Total energy over one year (Wh)
    total_e = power_series.sum()
    # Irradiance at STC (W/m2)
    g_stc = 1000
    # Total irradiance in POA over one year (W/m2) * h
    total_g_poa = gpoa_series.sum()
    # Module power under STC (W)
    p_stc = pnom * 1000
    # CSER (climate specific energy rating) over one year
    cser = (total_e * g_stc) / (total_g_poa * p_stc)
    return cser

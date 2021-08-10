# -*- coding: utf-8 -*-
"""
Created on Mon May 17 17:57:25 2021

@author: mriveraa
"""
import matplotlib.pyplot as plt
from os.path import join
import numpy as np

def plot_summary_cser(df, res_folder):
    """
    

    Returns
    -------
    None.

    """
    
    plt.figure()
    ax= df.plot(kind='bar', width=0.8, align='center')
    #ax= results_df_cser.plot.bar()
    
    ax.set_xlabel('Site', fontsize=9)
    ax.set_ylabel('Climate Specific Energy Rating (CSER)', fontsize=9,
                  horizontalalignment='center')
    ax.set_title("CSER for standard climate sites", fontsize=9)
    ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0.)
    
    my_xticks = ('Tro.hum.', 'Sub. ari.','Sub.cos','Tem. cos.' , 'Hig. ele.', 'Tem. con.')
    plt.xticks(df.index, my_xticks, rotation=20)
    plt.tight_layout()

    # Save image
    name = "CSER_summary"
    path = join(res_folder, name)
    plt.savefig(path, dpi=300)

    return

def plot_summary_eta(df, res_folder):
    """
    

    Returns
    -------
    None.

    """
    
    plt.figure()
    ax= df.plot(kind='bar', width=0.8, align='center')
    #ax= results_df_cser.plot.bar()
    
    ax.set_xlabel('Site', fontsize=9)
    ax.set_ylabel('Efficiency ETA', fontsize=9,
                  horizontalalignment='center')
    ax.set_title("ETA for standard climate sites", fontsize=9)
    ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0.)
    
    my_xticks = ('Tro.hum.', 'Sub. ari.','Sub.cos','Tem. cos.' , 'Hig. ele.', 'Tem. con.')
    plt.xticks(df.index, my_xticks, rotation=20)
    plt.tight_layout()

    # Save image
    name = "ETA_summary"
    path = join(res_folder, name)
    plt.savefig(path, dpi=300)

    return

def plot_eta(df, res_folder, module_id, location):
    """
    This function graphs the linear correlation between the irradiance measured
    by pyranometer and Si sensor (uncorrected and in every step correction).

    Parameters
    ----------
    df: DataFrame
        DataFrame containing the timestamps, g_pyr and g_si.
    g_pyr: String
        Name of pyranometer's irradiance column.
    g_si: String
        Name of Si sensor's irradiance column.
    titel: String
        Name of the linear correlation.
    site : String
        Name or ID of monitoring system.
    res_folder: String
        Path to file where results want to be saved.

    Returns
    -------
    A plot containing the linear correlation between the irradiance
    measurements of pyranometer and Si sensor after a correction procedure for
    a year of data.

    Example
    -------
    >>>plotting2.linear(df=merge_df,
    >>>                 g_pyr='G_m_pyr__0',
    >>>                 g_si='G_m_msi__0',
    >>>                 titel='Uncorrected linear correlation"
    >>>                 site='a000279',
    >>>                 res_folder="P:/results")
    """

    fig, ax = plt.subplots(figsize=(5.5, 4), dpi=300)
    ax.set_xlabel('Time of the year', fontsize=9)
    ax.set_ylabel('Efficiency ETA', fontsize=9,
                  horizontalalignment='center')
    ax.set_title("Efficiency ETA in Standard Site: %s" %(location["site_name"]), fontsize=9)

    # Pyranometer's irradiance
    x = df.index
    # Si sensor's irradiance
    y = df["eta"]

    p1, = ax.plot(x, y, '.', label='ETA', markersize=1)
    lns = [p1]
    ax.legend(handles=lns, loc='best', fontsize=9)

    # Save image
    path = "ETA_%s_%s.png" % (module_id, location["site_name"])
    path = join(res_folder, path)
    plt.savefig(path)
    return

def plot_cser(df, res_folder, module_id):
    """
    

    
    """

    fig, ax = plt.subplots(figsize=(5.5, 4), dpi=300)
    ax.set_xlabel('Site', fontsize=9)
    ax.set_ylabel('Climate Specific Energy Rating', fontsize=9,
                  horizontalalignment='center')
    ax.set_title("CSER from standard locations- module: %s" %(module_id), fontsize=9)
    #ax.set_ylim(0.9, 1.025)
    
    # Standard climate names
    xs = df.index.values
    # CSER values
    ys = df["cser_%s"%(module_id)]
    y_mean = [np.mean(ys)]*len(xs)
    
    my_xticks = ['Tro.hum.', 'Sub. ari.','Sub.cos','Tem. cos.' , 'Hig. ele.', 'Tem. con.']
    plt.xticks(xs, my_xticks)
    
    for x,y in zip(xs,ys):
    
        label = "{:.2f}".format(y)
    
        plt.annotate(label, # this is the text
                     (x,y), # this is the point to label
                     textcoords="offset points", # how to position the text
                     xytext=(0,2), # distance from text to points (x,y)
                     ha='center',
                     fontsize=7) # horizontal alignment can be left, right or center

    # Bar plot
    #plt.bar(x, y, align='center')
    #plt.xticks(rotation=45, ha='right')

    p1, = ax.plot(xs, ys, 'o-', label='CSER', markersize=2)
    p2, = ax.plot(xs, y_mean, label='Mean CSER', linestyle='--')
    lns = [p1, p2]
    ax.legend(handles=lns, loc='best', fontsize=9)

    
    # Save image
    path = "CSER_%s.png" % (module_id)
    path = join(res_folder, path)
    plt.savefig(path)
    return


# -*- coding: utf-8 -*-
"""
Created on Mon May 17 17:57:25 2021

@author: mriveraa
"""
import matplotlib.pyplot as plt
from os.path import join
import numpy as np
import seaborn as sns
import matplotlib.dates as mdates
sns.set_theme(style="whitegrid")


def round_robin_plot(df, module_id, res_folder):
    """
    This function generates a figure with the CSER values of a module for each
    standard climate. With the Round Robin figure format for easy comparision.

    Parameters
    ----------
    df: Pandas DataFrame
        Data frame with the CSER values for each of the six standard climates
    module_id: String
        Name or ID of the module
    res_folder: String/Path
        Path where figure should be saved
    """
    fig, ax = plt.subplots(figsize=(5.5, 4), dpi=300)
    ax.set_xlabel('Site', fontsize=9)
    ax.set_ylabel('Climate Specific Energy Rating', fontsize=9,
                  horizontalalignment='center')
    ax.set_title("CSER with RoundRobin format- module: %s" %(module_id),
                 fontsize=9)

    # Standard climate names
    xs = df.index.values
    # CSER values
    ys = df["cser_%s"%(module_id)]
    ys = ys.reindex([1,2,0,5,3,4])
    y_mean = [np.mean(ys)]*len(xs)
    
    my_xticks = ['Sub. ari.','Sub.cos','Tro.hum.','Tem. con.', 'Tem. cos.',
                 'Hig. ele.']
    plt.xticks(xs, my_xticks)
    
    for x,y in zip(xs,ys):
    
        label = "{:.2f}".format(y)
    
        plt.annotate(label, # this is the text
                     (x,y), # this is the point to label
                     textcoords="offset points", # how to position the text
                     xytext=(0,2), # distance from text to points (x,y)
                     ha='center',
                     fontsize=8)

    p1, = ax.plot(xs, ys, 'o-', label='CSER', markersize=2)
    p2, = ax.plot(xs,y_mean, label='Mean CSER', linestyle='--')
    lns = [p1, p2]
    ax.legend(handles=lns, loc='best', fontsize=9)

    plt.yticks(np.arange(0.85, 1.05, step=0.05))
    plt.grid(True)

    # Save image
    name = "CSER_RoundRobin_format_%s.png" %(module_id)
    path = join(res_folder, name)
    plt.savefig(path, dpi=900)

    return

def eta_all_sites(df, module_id, res_folder):
    """
    This function generates a figure of 6 subplots (for each standard climate)
    with the hourly ETA values of a module from the whole year of data given
    by the standard IEC61853-4.

    Parameters
    ----------
    df: Dictionary
        Dictionary with the 6 data frames given by the standard with a
        column of the calculated ETA values ('eta').
    module_id: String
        Name or ID of the module
    res_folder: String/Path
        Path where figure should be saved
    """

    climate = ['Tropical humid', 'Subtropical arid (desert)',
           'Subtropical coastal', 'Temperate coastal',
           'High elevation (above 3 000 m)', 'Temperate continental']

    #  Categorical Data
    a = 2  # number of rows
    b = 3  # number of columns
#    c = 1  # initialize plot counter
    i = 0
    fig, axlist = plt.subplots(a, b, figsize=(14, 10), dpi=300, sharey=True)
    for ax in axlist.flat:

        # Pyranometer's irradiance
        x = df[climate[i]].index
        # Si sensor's irradiance
        y = df[climate[i]]["eta"]

        sns.scatterplot(x=x, y=y, s=3, ax=ax)

        ax.set_xlabel('Time of the year', fontsize=9)
        ax.set_ylabel('Efficiency ETA', fontsize=9,
                      horizontalalignment='center')
        ax.set_title("Module %s in %s" %(module_id, climate[i]), fontsize=9)
        # Text in the x axis will be displayed in format
        #set major ticks format
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
        i = i+ 1

    plt.tight_layout()
    # Save image
    path = "ETA_Standard_Climates_%s.png" % (module_id)
    path = join(res_folder, path)
    plt.savefig(path)
    return

def plot_summary_cser(df, res_folder):
    """
    This function generates a bar plot with the CSER values for each of the
    six standard climates and each of the modules chosen for simulation. As
    a way of comparate perfomance (CSER) of the modules depending on the
    climate.

    Paramaters
    -------
    df : Pandas DataFrame
        Data frame with the CSER results of each module (columns) on the six
        standard climates (rows).
    res_folder: String/Path
        Path where figure should be saved
    """

    ax = df.plot(kind='bar', width=0.8, align='center', figsize=(11, 6.5),
                 fontsize=15)

    ax.set_xlabel('Site', fontsize=17)
    ax.set_ylabel('Climate Specific Energy Rating (CSER)', fontsize=17)
    ax.set_title("CSER for standard climate sites", fontsize=17)
    ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0.)
    
    my_xticks = ('Tro.hum.', 'Sub. ari.','Sub.cos','Tem. cos.' , 'Hig. ele.',
                 'Tem. con.')
    plt.xticks(df.index, my_xticks, rotation=20)
    ymin= min(df.min(numeric_only=True))
    ax.set_ylim([ymin-0.1,None])
    
    plt.tight_layout()

    # Save image
    name = "CSER_summary"
    path = join(res_folder, name)
    plt.savefig(path, dpi=900)

    return

def plot_summary_eta(df, res_folder):
    """
    This function generates a bar plot with the ETA values for each of the
    six standard climates and each of the modules chosen for simulation. As
    a way of comparate perfomance (ETA) of the modules depending on the
    climate.

    Paramaters
    -------
    df : Pandas DataFrame
        Data frame with the ETA results of each module (columns) on the six
        standard climates (rows).
    res_folder: String/Path
        Path where figure should be saved
    """

    ax = df.plot(kind='bar', width=0.8, align='center', figsize=(11, 6.5),
                 fontsize=15)
    
    ax.set_xlabel('Site', fontsize=17)
    ax.set_ylabel('Efficiency ETA', fontsize=17,
                  horizontalalignment='center')
    ax.set_title("ETA for standard climate sites", fontsize=17)
    ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0.)
    
    my_xticks = ('Tro.hum.', 'Sub. ari.','Sub.cos','Tem. cos.' , 'Hig. ele.',
                 'Tem. con.')
    plt.xticks(df.index, my_xticks, rotation=20)
    ymin= min(df.min(numeric_only=True))
    ax.set_ylim([ymin-0.01,None])
    
    plt.tight_layout()

    # Save image
    name = "ETA_summary"
    path = join(res_folder, name)
    plt.savefig(path, dpi=900)

    return

def plot_eta(df, res_folder, module_id, location):
    """
    This function generates a figure with the hourly ETA values of a module in
    an specific climate. The data frame is given by the standard IEC61853-4
    and the 'eta' is calculated by the simulation.

    Parameters
    ----------
    df: Pandas DataFrame
        Data frame given by the standard with a column of the calculated ETA
        values ('eta').
    module_id: String
        Name or ID of the module
    res_folder: String/Path
        Path where figure should be saved
    location: Dictionary
        Dictionary with information from the module taken by the
        'read_standard_locations' function
    """

    fig, ax = plt.subplots(figsize=(6.5, 5), dpi=300)
    ax.set_xlabel('Time of the year', fontsize=9)
    ax.set_ylabel('Efficiency ETA', fontsize=9,
                  horizontalalignment='center')
    ax.set_title("Efficiency ETA in Standard Site: %s" 
                 %(location["site_name"]), fontsize=9)

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
    This function generates a figure with the CSER values of a module for each
    standard climate.

    Parameters
    ----------
    df: Pandas DataFrame
        Data frame with the CSER values for each of the six standard climates
    module_id: String
        Name or ID of the module
    res_folder: String/Path
        Path where figure should be saved
    
    """

    fig, ax = plt.subplots(figsize=(5.5, 4), dpi=300)
    ax.set_xlabel('Site', fontsize=9)
    ax.set_ylabel('Climate Specific Energy Rating', fontsize=9,
                  horizontalalignment='center')
    ax.set_title("CSER from standard locations- module: %s" %(module_id),
                 fontsize=9)

    # Standard climate names
    xs = df.index.values
    # CSER values
    ys = df["cser_%s"%(module_id)]
    y_mean = [np.mean(ys)]*len(xs)
    
    my_xticks = ['Tro.hum.', 'Sub. ari.','Sub.cos','Tem. cos.' , 'Hig. ele.',
                 'Tem. con.']
    plt.xticks(xs, my_xticks)
    
    for x,y in zip(xs,ys):
    
        label = "{:.2f}".format(y)
    
        plt.annotate(label, # this is the text
                     (x,y), # this is the point to label
                     textcoords="offset points", # how to position the text
                     xytext=(0,2), # distance from text to points (x,y)
                     ha='center',
                     fontsize=7)

    p1, = ax.plot(xs, ys, 'o-', label='CSER', markersize=2)
    p2, = ax.plot(xs, y_mean, label='Mean CSER', linestyle='--')
    lns = [p1, p2]
    ax.legend(handles=lns, loc='best', fontsize=9)

    # Save image
    path = "CSER_%s.png" % (module_id)
    path = join(res_folder, path)
    plt.savefig(path)
    return


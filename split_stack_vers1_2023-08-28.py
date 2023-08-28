import pandas as pd
import numpy as np
import regex as re
import glob 


###2023-08-28 #First release

"""When pulling data on a technology using ACE KLARITY, CMP layers and tools are not tidy"""
"""These functions help (1) split the messy df into separate dfs by LAYER and (2) stack TRACK vs CMP tools."""
"""The final output is a LIST of tidied DFs, each one corresponding to a single layer"""
"""WARNING: the input for this function must be limited to a single tech flow (e.g. only T18) """

"""To use this, simply import as "ss" and then "ss.raw_to_layersplit_and_stacked(Filename)" and it should do its thing! """

def num_layers(df):
    """Returns the number of layers in the ACE extract"""
    list_attributes=list(df.axes[1])
    dummylist = [x for x in list_attributes if "AvgLotPolishTime_AVG_AVERAGE" in x]
    num_layers = len(dummylist)/2
    return num_layers


def layer_splitter(df, num_layers):
    """Takes the raw ACE output and returns a list of DFs, each corresponding to a separate layer of the tech."""
    """  ***NOTE: input DF must comprise of only a single tech!!!*** """
    
    #For every unique layer, add a new DF to the list of unique layers
    list_of_uniquelayerdfs = []
    pattern = "(PRODUCT|LOT|OX"
    pattern2 ="CMP)"
    for i in range(0, int(num_layers-1)+1):
        list_of_uniquelayerdfs.append(df.filter(regex=pattern+str(i)+pattern2))
        
    return list_of_uniquelayerdfs


def stacker_trackvscmp(df):
    """Takes in ACE output of TRACK and CMP from OXIDE tools and stacks them together"""
    """ (does this by re-writing OXCMP as OXTRACK)""" 
    
    #Create a new DF of just the TRACK lots, with their product and lot ID intact
    df_track = df.filter(regex=r'(PRODUCT|LOT|TRACK)')
    
    #Create a new DF of just the CMP/standalone lots, with their product and lot ID intact
    df_cmp =  df.filter(regex=r'(PRODUCT|LOT|OXCMP)')
    #And replace "OXCMP" with "OXTRACK" so that it can be stacked on attributes 
    df_cmp.rename(columns=lambda s: s.replace("OXCMP", "OXTRACK"), inplace=True)

    df_all = pd.concat([df_track, df_cmp])
    return df_all

def raw_to_layersplit_and_stacked(filename):
    """Takse a raw ACE output of a tech, SPLITS into df/layer, and STACKS each using three functions above"""
    df = pd.read_excel(format(filename))
    numlayers = num_layers(df)
    list_of_unique_layers = layer_splitter(df, numlayers)
    
    tidied_dfs = []
    for i,dataf in enumerate(list_of_unique_layers):
        tidied_dfs.append( stacker_trackvscmp(dataf) )
    
    return tidied_dfs


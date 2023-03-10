import glob #can 

import pandas as pd
import numpy as np

import iqplot
import colorcet

import bokeh.io
import bokeh.plotting

import regex as re
import glob #can 
bokeh.io.output_notebook()


"""Simple UV exporter (the predescessor) only extracted the bare minimum of x,y,and thickness data """
"""This new version was created to preserve more data from the UV tool, including the date it was run on, lotID, UV recipe, and more"""
"""The fundamental difference is that instead of using for loops to create dataframes, it uses vectorization and pd.melt()"""
"""I hope you like it ;)"""
"""This version is compatible with RAW DATA from UV1050. I have NOT tested from other UV. Do not use cassette or tabulated formats."""

"""To use this, simply import as "melty" and then "melty.self_contained_UVexporter(Filename)" and it should do its thing! """

list_attributes = ['Cassette', 'SLOT', 'LOT ID', 'WAFER ID', 'STATUS', 'DATA TYPE', 'RECIPE', 'RCP CNT',
             'MEAS SET', 'MATERIAL', 'SITE', 'RESULT TYPE', 'MEAN', 'MIN', 'MAX',
             '% STD DEV', '3 SIGMA', 'RANGE', ' SITES']

def melter(df):
    """Takes in a dataframe of raw data from the UV tool. I think you have to delete the 2nd row (empty), but try without doing that"""
    """Melts all non-identifier data (x,y,thickness) into a single column"""
    df_melted = df.melt(
        #id_vars = a list of column names that will remain as they are and not be reshaped, also called identifier variables. If not 
        #provided, all columns will be stacked into 1 column.
        id_vars=list_attributes,
    )
    
    return df_melted

def xydata_separator(df_melted):
    """Creates three dataframes of x,y,data."""
    #df.loc[ df[column] Boolean, [‘column1’, ‘column2’] ]
    df_data= df_melted [df_melted["variable"].str.contains("DATA")]
    df_x= df_melted [df_melted["variable"].str.contains("X")]
    df_y= df_melted [df_melted["variable"].str.contains("Y")]


    #Then, we rename the "value" column of each to a more specific data type
    #rename https://www.kdnuggets.com/2022/11/4-ways-rename-pandas-columns.html
    df_x.columns = df_x.columns.str.replace("value", "X")
    df_y.columns = df_y.columns.str.replace("value", "Y")
    df_data.columns = df_data.columns.str.replace("value", "DATA")

    #Next, we reset index on all the guys (this helps merge later)
    df_x = df_x.reset_index(drop=True)
    df_y = df_y.reset_index(drop=True)
    df_data = df_data.reset_index(drop=True)

    #And finally, we modify the DATA and Y containing DFs to drop all identifier columns (list attributes)
    df_data_only = df_data.drop(columns=list_attributes)
    df_y_only = df_y.drop(columns=list_attributes)
    
    return df_x, df_y_only, df_data_only

def xydata_concat(df_x, df_y_only, df_data_only):
    #We can then concatenate df_x with df_y_only
    horizontal_concat = pd.concat([df_x, df_y_only], axis=1)
    final_concat = pd.concat([horizontal_concat, df_data_only], axis=1)
    return final_concat

def self_contained_UVexporter(filename):
    
    """Takes in an excel file (must be in same filepath) and converts into a tidy dataframe"""
    
    df = pd.read_excel('Data/{}'.format(filename))
    df_melted = melter(df)
    df_list = xydata_separator(df_melted)
    final_df = xydata_concat(df_list[0],df_list[1],df_list[2])
    return final_df
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


"""Hey, hey you! Don't add anything to this that alters the file from the UV tool!"""
"""That means stuff like (1) calculating radii or (2) WIWNU or (3) Roll-off etc..."""



def data_filters(df):
    """takes in a raw dataframe from an excel sheet and separates into three separate dfs of x,y,thickness"""
    """returns a list of just those 3 dfs as "df_list""" 
        
    #Establish names
    filter_x = [col for col in df if col.startswith(' X') or col.startswith('SLOT')]
    x = filter_x
    filter_y = [col for col in df if col.startswith(' Y') or col.startswith('SLOT')]
    y = filter_y
    filter_data = [col for col in df if col.startswith('DATA[') or col.startswith('SLOT')]
    data = filter_data


    #Use list of names to create a list of 3 DFs, 0=x, 1=y, 2=thicknesses
    filters = [x,y,data]
    df_list = []

    #For each type of data, 
    for i,infotype in enumerate(filters):
        df_list.append(df[infotype])
        df_list[i] = df_list[i].set_index('SLOT')
        
    return df_list

###############################################################
def num_slots(df):
    """get the number of slots tested in the first raw Df"""
    num_slots=len(df)
    return num_slots

##################################################################
def slot_ids(df):
    """get the IDs of slots tested from the first raw DF"""
    slot_IDs=df['SLOT'].tolist()
########################################################################

def tidy_dfs(slot_IDs, df_list):
    """Create a DF for EACH wafer, comprising the columns of slot,x,y, and data. Returns a list of DFs"""
    
    #initialize list of tidy dfs
    tidy_df_list=[]
        
        #you want to create a DF for EACH wafer, comprising the columns of slot, x, y, and data
    for i, slot in enumerate(slot_IDs):

        df=pd.DataFrame()

        #take the relevant data of the Slot and turn each of them into a series, then into a DataFrame
        x_data=df_list[0].iloc[i,].to_frame()

        #rename the column entry to the data type (e.g. x, y, or thickness)
        x_data=df_list[0].iloc[i,].to_frame(name='x(mm)')

        #re-index then get rid of old column 'index'
        x_data.reset_index(inplace = True)
        del x_data['index']


        y_data=df_list[1].iloc[i,].to_frame()
        y_data=df_list[1].iloc[i,].to_frame(name='y(mm)')
        y_data.reset_index(inplace = True)
        del y_data['index']


        thick_data=df_list[2].iloc[i,].to_frame()
        thick_data=df_list[2].iloc[i,].to_frame(name='thickness_A')
        thick_data.reset_index(inplace = True)
        del thick_data['index']    

        #And now, create the dataframe of the slot entry
        all_data_of_slot=pd.concat([x_data,y_data,thick_data],
                                  axis=1,
                                  )
        #...and add the column of "slot" with value of current slot
        all_data_of_slot.insert(0, 'slotID', slot)

        tidy_df_list.append(all_data_of_slot)

    return tidy_df_list
###############################################

def jmp_exporter(filename):
    """Takes an EXCEL file (don't forget extension!) and outputs a tidy DF ready for JMP plotting. Excel sheet should be filtered for only one measurement site."""
    
    #read in the sheet
    df = pd.read_excel('Data/{}'.format(filename))
    
    #keep only rows that contain "thickness"
    df_thick= df[df["RESULT TYPE"].str.contains("Thickness",na=False)]
    
    
    #get the number of slots tested
    num_slots=len(df_thick)
    #get the IDs of slots tested
    slot_IDs=df_thick['SLOT'].tolist()
    
    #Generate 3 separate DFs of x,y, and thickness data
    x_y_thickness_dfs=data_filters(df_thick)
    
    #Create a DF for EACH wafer, comprising the columns of slot,x,y, and data. Returns a list of DFs"""
    wafer_dfs=tidy_dfs(slot_IDs, x_y_thickness_dfs)
    
    #Concatenate the df of each slot into one df!
    output_df=pd.concat(wafer_dfs)
    
    
    return output_df

##############################
def add_radius(df):
    """Takes in a tidied DF and adds the measurement site distance from wafer center"""
    df['radius_mm'] =( df['x(mm)']**2 + df['y(mm)']**2 )**0.5
    return df
    
def no_nans(df):
    """Replaces 'site not found' data entries from UV tool with 'NaN' """
    ##https://stackoverflow.com/questions/29287847/string-wildcard-in-pandas-on-replace-function
    
    df['thickness_A']=df['thickness_A'].replace(
    r's.+', #this searches for a string that begins with an 's' of indeterminate length 
    'NaN',
    regex=True
)
    return df


###########################
#The Final result##########
###########################

def self_contained_UVexporter(filename):
    
    """Takes in an excel file (must be in same filepath) and converts into a tidy dataframe"""
    """Output cols: slot, meas site x, meas site y, film thickness, meas site radius, """ 
    """Removes 'site XX not found' with NaNs """
    
    df = jmp_exporter(filename)
    df = add_radius(df)
    df = no_nans(df)
    return df

    
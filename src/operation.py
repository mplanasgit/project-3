# This document contains the functions to be used for analyzing data
# ----------------------------------------------------------------------------------------------------

# Libraries 
import os
import pandas as pd
import time
import re
import io
import requests
import json
from dotenv import load_dotenv
import geopandas as gpd
from cartoframes.viz import Map, Layer, popup_element
import math

# ----------------------------------------------------------------------------------------------------
# Function to between two points given their coordinates

def haversine(coord1, coord2):
 
    # Coordinates in decimal degrees (e.g. 2.89078, 12.79797)
    lon1, lat1 = coord1
    lon2, lat2 = coord2

    R = 6371000  # radius of Earth in meters
    phi_1 = math.radians(lat1)
    phi_2 = math.radians(lat2)

    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi_1) * math.cos(phi_2) * math.sin(delta_lambda / 2.0) ** 2
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    meters = R * c  # output distance in meters
    meters = round(meters)
    
    return meters

# ----------------------------------------------------------------------------------------------------
# Function to add a distance column using the 'haversine' formula

def addDistanceHaversine(df, coord_my_company):
    '''This function receives a dataframe and adds a new column called 'distance'
    which is the distance between my company and the rest of the companies
    '''
    # Reorganizing latitude and longitude
    coord_list = []
    for index, row in df.iterrows():
        coord_list.append([row['longitude'], row['latitude']])
    
    df['coordinates'] = coord_list
    
    # Applying the distance function
    df['distance'] = df['coordinates'].apply(lambda x: haversine(x, coord_my_company))
    
    # Sorting by distance
    df = df.sort_values(by=["distance"])
    
    # Removes rows with distance == 0 (my company) and distance > 5000m:
    df = df[(df['distance'] != 0) & (df['distance'] <= 5000)]
    
    # Add column for later processing
    df['query'] = 'companies nearby' 
    
    return df

# ----------------------------------------------------------------------------------------------------
# Function to adds two columns: 'counts' and 'distance' after grouping the df by the 'query' column.
# This function is used within the concatDataframes function.

def addCountDistance(df):
    '''This function receives a dataframe and adds a 'counts' and a 'distance'
    column to the df.
    '''
    # Grouping by "query" (getting the counts) and adding up all the distances after grouping.
    series = [df.groupby("query").size(), df.groupby("query")["distance"].sum()]
    new_df = pd.concat(series, axis = 1).reset_index().rename(columns={0: 'counts', 'distance': 'sum_distance'})
    
    return new_df

# ----------------------------------------------------------------------------------------------------
# Function to concatenate the companies df and the categories df (the one obtained through API request)

def concatDataframes(*df):
    '''This function receives dataframes, applies the addCountDistanceCategory to each,
    and concatenates them.
    '''
    df_list = []
    for i in df:
        df_list.append(addCountDistance(i))
    
    df1 = pd.concat([df for df in df_list])
    
    return df1

# ----------------------------------------------------------------------------------------------------
# Function to add parameters to the concatenated df based on values passed in dict.

def addParameters(df, *dict_category):
    '''This function receives a dataframe and adds parameters columns to the df.
    '''
    # Creating a template df with the categories values specified in the received dictionaries.
    template_df = pd.DataFrame(dict_category).T.reset_index().rename(columns={"index": "query", 0: "weight", 1: "radius"})
    
    # Mergin the received df to the template.
    df2 = template_df.merge(df, how = "outer")
    
    return df2

# ----------------------------------------------------------------------------------------------------
# Function to calculate and add the weighted average distance as a new column in the df.

def calculateWeighted(df):
    '''This function receives a df and returns a new df where the weighted distance of each category is calculated.
    '''
    # Add columns 'average_distance' and penalizing empty cells based on radius:
    df["avg_distance"] = round(df["sum_distance"] / df["counts"],1)
    df["avg_distance"] = round(df["avg_distance"].fillna(df["radius"]),1)
    
    # Calculating 'weighted average distance'
    df["weighted_avg_distance"] = round(df["avg_distance"] * df["weight"],1)

    return df

# ----------------------------------------------------------------------------------------------------
# Function to create a summary table using previous functions.

def createSummaryTable(df, *dict_category):
    '''This function creates a summary table based on the received concatenated df 
    and the values specified for each category (passed as dictionary)
    '''
    df1 = addParameters(df, *dict_category)
    df2 = calculateWeighted(df1)
    return df2

# ----------------------------------------------------------------------------------------------------
# Function to calculate the total score of each city based on the weighted distances of each activity.

def calculateTotal(*df):
    '''This function receives a dataframe and calculates the total score
    as the sum of the weighted distance. The score is then normalized based on
    the min weighted distance, which is given a score of 100.
    '''
    # Append the sum of weighted avg distance to list.
    total_min = []
    for i in df:
        total_sum = sum(i["weighted_avg_distance"])
        total_min.append(total_sum)
    
    # Normalize based on the minimum value of the previous list.
    total_list = []
    for i in total_min:
        total = round((i * 100 / min(total_min)))
        total_list.append(total)
    
    # Get the names of each df.
    name_list = []
    for i in df:
        name_list.append(i.name)
    
    # Create a df containing the name of the df and the total score
    total_df = pd.concat([pd.Series(name_list), 
                          pd.Series(total_list)], axis = 1).rename(columns={0: 'City', 1: '% Avg distance'})
    
    total_df = total_df.sort_values(by=['% Avg distance']).reset_index(drop = True)
    
    return total_df

# ----------------------------------------------------------------------------------------------------
# Function to rename the columns in a way that they will be used for visualization.

def renameColumns(df):
    '''Function that renames columns latitude and longitude
    '''
    df = df.rename(columns = {"latitude" : "lat", "longitude" : "lon"})
    
    return df


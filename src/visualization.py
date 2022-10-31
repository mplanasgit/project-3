# This document contains the functions to be used for visualizing data
# ----------------------------------------------------------------------------------------------------
#  
# Libraries

import folium
from folium import Choropleth, Circle, Marker, Icon, Map
from folium.plugins import HeatMap, MarkerCluster
import pandas as pd

# ----------------------------------------------------------------------------------------------------
# Function to create a map centered on given coordinates

def createMap(coordinates):
    '''This function receives a list of coodinates in the format [latitude, longitude]
    and creates a map around it, marking your coordinates.
    '''
    # Creating the map
    mapa = Map(location = coordinates, zoom_start = 14, control_scale = True)
    # Creating my icon properties
    my_icon = Icon(color = "black", prefix = "fa", icon = "diamond")
    # Creating and adding my marker
    my_company = Marker(location = coordinates, tooltip = "EpicNice", icon = my_icon)
    my_company.add_to(mapa)
    
    return mapa

# ----------------------------------------------------------------------------------------------------
# Function to add markers to the map 

def addMarkers(df, mapa):
    '''This function adds markers to your map.
    :df: the dataframe from which it takes the coordinates.
    :mapa: your map.
    '''
    for index, row in df.iterrows():

        # Add points coordinates (marker without the icon)
        query = {"location": [row["lat"], row["lon"]], "tooltip": row["name"]}

        # Add icons
        if row["query"] == "school":        
            icon = Icon (color = "blue",
                         prefix = "fa", icon = "graduation-cap")        
        elif row["query"] == "club":
            icon = Icon (color = "red",
                         prefix = "fa", icon = "glass")       
        elif row["query"] == "starbucks":
            icon = Icon (color = "gray",
                         prefix = "fa", icon = "coffee")
        elif row["query"] == "airport":
            icon = Icon (color = "purple",
                         prefix = "fa", icon = "plane")            
        elif row["query"] == "vegan restaurant":
            icon = Icon (color = "green",
                         prefix = "fa", icon = "cutlery")            
        elif row["query"] == "basketball":
            icon = Icon (color = "orange",
                         prefix = "fa", icon = "futbol-o")            
        elif row["query"] == "dog hairdresser":
            icon = Icon (color = "lightgray",
                         prefix = "fa", icon = "paw")
        elif row["query"] == "companies nearby":
            icon = Icon (color = "lightred",
                         prefix = "fa", icon = "building")        

        # Add markers with respective icon
        new_marker = Marker(**query, icon = icon, radius = 2)
        new_marker.add_to(mapa)
        
    return mapa

# ----------------------------------------------------------------------------------------------------
# Function to add HeatMap based on group

def addHeatMap(df, column, featuregroup, mapa):
    '''This function creates a feature group and adds it to the map as a heatmap.
    :df: df, the original df.
    :column: str, the name of the column where to look for the group.
    :featuregroup: str, your subgroup.
    :mapa: map, the map you want the group to be added.
    '''
    # Define the feature group
    df_subset = df[df[column] == featuregroup]
    df_group = folium.FeatureGroup(name = f"{featuregroup}: {df_subset.shape[0]}")
    HeatMap(data = df[["lat", "lon"]], radius = 25, 
        gradient = {0.4: 'yellow', 0.65: 'orange', 1: 'red'}).add_to(df_group)
    df_group.add_to(mapa)
    
    # Add layer control
    folium.LayerControl(collapsed = False, position = "topleft").add_to(mapa)
    
    return mapa




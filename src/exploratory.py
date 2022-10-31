# This document contains the functions to be used for requesting data from foursquare
# ----------------------------------------------------------------------------------------------------

# Libraries
from pymongo import MongoClient
import pandas as pd
import re
import io
import folium
from folium import Choropleth, Circle, Marker, Icon, Map

# ----------------------------------------------------------------------------------------------------
# This function establishes a connection to the specified database and collection

def getCollection(client, database, collection):
    '''This function receives a client, database and collection strings 
    in order to connect to a database stored in MongoDB and access a specified collection.
    All parameters are entered as str.
    '''
    
    client = MongoClient(client)
    db = client[database]
    c = db.get_collection(collection)
    
    return c

# ----------------------------------------------------------------------------------------------------
# This function appends all the values of a specific field into a list

def getField(result, field):
    '''This function returns all the unique values for a specified field (str) 
    from a collection search (result).
    '''
    
    field_list = []
    for i in range(len(result)):
        field_list.append(result[i][field])
    field_list = set(field_list)
    
    return field_list

# ----------------------------------------------------------------------------------------------------
# This function explodes the content within the cell of a column into several rows

def explodeColumns(df, column):
    '''This function receives a df and the name of a column (str),
    and applies the explode method to it.
    '''
    
    df = df.explode(column)
    df = df.reset_index()
    df = df.drop(columns = 'index', axis = 1)
    
    return df

# ----------------------------------------------------------------------------------------------------
# This function extracts info from a crunchbase find result

def extractInfoCrunchbase(df):
    '''This function receives a dataframe from the crunchbase database and extracts the following information:
    office, state_code, country_code, latitude, longitude.
    '''
    city = []
    state_code = []
    country_code = []
    latitude = []
    longitude = []
    
    for index, row in df.iterrows():
        try:
            city.append(row['offices']['city'])
            state_code.append(row['offices']['state_code'])
            country_code.append(row['offices']['country_code'])
            latitude.append(row['offices']['latitude'])
            longitude.append(row['offices']['longitude'])
        except IndexError:
            city.append(None)
            state_code.append(None)
            country_code.append(None)
            latitude.append(None)
            longitude.append(None)
    
    df['city'] = city
    df['state_code'] = state_code
    df['country_code'] = country_code
    df['latitude'] = latitude
    df['longitude'] = longitude
    
    return df

# ----------------------------------------------------------------------------------------------------
# This function creates a map and adds markers

def createMap_addMarkers(coordinates, df):
    '''This function receives a list of coodinates in the format [latitude, longitude]
    and a df and creates a map around it. It adds the markers of every row of your df.
    '''
    # Creating the map
    mapa = Map(location = coordinates, zoom_start = 10, control_scale = True)
    # Creating and adding markers
    for index, row in df.iterrows():
        company = {"location": [row["latitude"], row["longitude"]], "tooltip": row["name"]}
        new_marker = Marker(**company, radius = 2)
        new_marker.add_to(mapa)
    
    return mapa
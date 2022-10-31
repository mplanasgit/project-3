# This document contains the functions to be used for requesting data from foursquare
# ----------------------------------------------------------------------------------------------------

# Libraries

import os
import pandas as pd
import io
import requests
from dotenv import load_dotenv
import geopandas as gpd
import time

# ----------------------------------------------------------------------------------------------------
# Function to perform requests on the Foursquare API

def getFoursquare(query, location, radius, token_fsq, limit=1):
    '''This function requests information from Foursquare Place Search:
    :query: str, your query in Foursquare.
    :location: list, in the format: [latitude, longitude], both int.
    :radius: int, to limit the radius of the request.
    :limit: int, to limit the number of requests. By default 1.
    '''
        
    ll = f"{location[0]}%2C{location[1]}"
    url = f"https://api.foursquare.com/v3/places/search?query={query}&ll={ll}&radius={radius}&sort=DISTANCE&limit={str(limit)}"

    headers = {
        "accept": "application/json",
        "Authorization": token_fsq,
    }
    
    response = requests.get(url, headers=headers).json()
    
    return response

# ----------------------------------------------------------------------------------------------------
# Function to perform requests on the Foursquare API, specifying Category

def getFoursquareCategory(query, location, radius, categories, token_fsq, limit=1):
    '''This function requests information from Foursquare Place Search:
    :query: str, your query in Foursquare.
    :location: list, in the format: [latitude, longitude], both int.
    :radius: int, to limit the radius of the request.
    :categories: str, the category or categories ID, separated by commas.
    :limit: int, to limit the number of requests. By default 1.
    '''
        
    ll = f"{location[0]}%2C{location[1]}"
    url = f"https://api.foursquare.com/v3/places/search?query={query}&ll={ll}&radius={radius}&categories={categories}&sort=DISTANCE&limit={str(limit)}"

    headers = {
        "accept": "application/json",
        "Authorization": token_fsq,
    }
    
    response = requests.get(url, headers=headers).json()
    
    return response

# ----------------------------------------------------------------------------------------------------
# Function to extract info from foursquare

def getInfo(response, query):
    '''This function receives a request response from foursquare and the info you queried, 
    and returns a dataframe with the following information (columns):
    name, distance, address, latitude, longitude and geometry.
    :response: list, the response of the request from foursquare.
    :query: string, the name of your query in foursquare.
    '''
    
    geo_list = []
    
    for i in response["results"]:

        name = i["name"]
        address =  i["location"]["formatted_address"]
        lat = i["geocodes"]["main"]["latitude"]
        lon = i["geocodes"]["main"]["longitude"]
        distance = i["distance"]

        type_geo = {"typepoint": 
                              {"type": "Point", 
                               "coordinates": [lat, lon]}}

        geo_list.append({"query": query,"name":name, "address":address, "distance":distance, "lat":lat, "lon":lon, "type":type_geo})
    
    df = pd.DataFrame(geo_list)
    
    return df

# ----------------------------------------------------------------------------------------------------
# Function to perform API requests, extract it into dataframes and concatenate the info into a single df

def getEverythingFoursquare(city, token_fsq):
    '''This functions receives the coordinates of a city and returns a dataframe with the extracted information.
    :city: list, in the format [latitude, longitude] both integers.
    '''

    # Run all functions
    schools = getFoursquareCategory("school", city, 2000, 12058, token_fsq, limit=5)
    clubs = getFoursquareCategory("night club", city, 2000, 10032, token_fsq, limit=5)
    starbucks = getFoursquare("starbucks", city, 2000, token_fsq, limit=5)
    basketball = getFoursquare("basketball stadium", city, 10000, token_fsq, limit=5)
    dog = getFoursquareCategory("dog grooming", city, 10000, 11134, token_fsq, limit=5)
    airport = getFoursquareCategory("airport", city, 50000, 19040, token_fsq, limit=5)
    vegan = getFoursquareCategory("vegan restaurant", city, 2000, 13377, token_fsq, limit=5)
    
    # Transform to dataframes
    df_1 = getInfo(schools, "school")
    df_2 = getInfo(clubs, "club")
    df_3 = getInfo(starbucks, "starbucks")
    df_4 = getInfo(airport, "airport")
    df_5 = getInfo(vegan, "vegan restaurant")
    df_6 = getInfo(basketball, "basketball")
    df_7 = getInfo(dog, "dog hairdresser")
    
    # Concatenate dataframes
    df = pd.concat([df_1, df_2, df_3, df_4, df_5, df_6, df_7], ignore_index = True, axis = 0)
    
    return df

# ----------------------------------------------------------------------------------------------------
# Function to convert typepoint coordinates so it can be used with CartoFrames

def geoDataframe(df):
    '''This functions converts the typepoint coordinates of a column of a dataframe so it can be used with CartoFrames.
    '''
    df = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["lon"], df["lat"]))
    df = df.drop(columns = 'type', axis = 1)
    return df
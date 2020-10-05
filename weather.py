# -*- coding: utf-8 -*-
'''
Created on Thu Jan  4 20:41:45 2018
Modified Jan 29 2019

@author: hgorr

'''

# weather.py
import csv
import datetime
import json  
import urllib.request

BASE_URL = 'https://api.openweathermap.org/data/2.5/{}?q={},{}&units={}&appid={}'
FORECAST_KEYS = {'current_time':'DateLocal', 'temp':'T', 'deg':'WindDir',
                 'speed':'WindSpd', 'humidity':'RH', 'pressure':'P'}

def read_backup(city):
    '''Read example data from a backup file'''

    with open('backupdata.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for s in [*reader]:
            if s['city'] == city:
                data = dict(s)
                data['City'] = city # Used for error checking below
                # Convert data types
                for k in ('temp', 'pressure', 'humidity', 'temp_min', 
                          'temp_max', 'speed', 'deg', 'lat', 'lon'):
                    data[k] = float(data[k])
                return data
    return None


def get_current_weather(city, country, apikey,**kwargs):  
    '''get current conditions in specified location
    get_current_weather('boston','us',key,units='metric')'''
            
    info = {'units':'imperial'}     
    for key, value in kwargs.items():
        info[key] = value
    # Read current conditions
    try:
        # url = 'https://api.openweathermap.org/data/2.5/weather?q=Boston,us&appid=11111'
        url = BASE_URL.format('weather',city,country,info['units'],apikey)
        json_data = json.loads(urllib.request.urlopen(url).read())        
    except urllib.error.URLError:
        # If weather API doesnt work, read the file
        json_data = read_backup(city)          

    return json_data


def parse_current_json(json_data):
    '''parse and extract json data from the current weather data''' 

    try:
        # select data of interest from dictionary
        weather_info = json_data['main']
        weather_info.update(json_data['wind'])
        weather_info.update(json_data['coord'])
        weather_info['city'] = json_data['name']
        # add current date and time
        weather_info['current_time'] = str(datetime.datetime.now())

    except KeyError as e:
        # use current dictionary (because it probably came from backup file) 
        try:
            # If this fails then the json_data didn't come from backup file
            json_data.pop('City')
            weather_info = json_data
        except:
            # print('Something else went wrong while parsing current json')
            raise e
    
    return weather_info


def get_forecast(city, country, apikey, **kwargs):
    '''get forecast conditions in specified location'''
        
    # include keyword args for numdays=3  and units='metric'    
    info = {'units':'imperial', 'days':5}     
    for key, value in kwargs.items():
        info[key] = value
        
    # get forecast    
    try:
        url = BASE_URL.format('forecast',city,country,info['units'],apikey)
        json_data = json.loads(urllib.request.urlopen(url).read())    
    except: 
        with open('backupforecast.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            json_data = {'City':city}
            for key in FORECAST_KEYS.keys():
                json_data[key] = []
            for s in [*reader]:
                if s['City'] == city:
                    for key,value in FORECAST_KEYS.items():
                        json_data[key].append(dict(s)[value])
    return json_data

def parse_forecast_json(json_data):
    '''parse and extract json data from the weather forecast data'''     
    
    try:
        # parse forecast json data
        data = json_data['list']
        wind_keys = ['deg','speed']
        weather_info = dict(zip(FORECAST_KEYS.keys(), 
                                [[] for i in range(len(FORECAST_KEYS))]))
        for data_point in data[0:40]:
            for k in list(FORECAST_KEYS.keys())[1:]: #Taking a slice so we don't add the city every time
                weather_info[k].append(float(data_point['wind' if k in wind_keys else 'main'][k]))
            weather_info['current_time'].append(data_point['dt_txt'])
    except KeyError as e:
        # use current dictionary (because it probably came from backup file) 
        try:
            # If this fails then the json_data didn't come from backup file
            json_data.pop('City') 
            weather_info = json_data
        except:
            # print('Something else went wrong while parsing forecast json')
            raise e

    return weather_info
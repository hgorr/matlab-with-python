# -*- coding: utf-8 -*-
"""
Created on Thu Jan  4 20:41:45 2018
Modified Jan 29 2019

@author: hgorr

"""

# weather.py
def read_backup(city):
    import csv
    lines = []
    with open('backupdata.csv',newline='') as csvfile:
        reader = csv.DictReader(csvfile,delimiter=',')
        for row in reader:
            lines.append(row)
        data = ""
        for s in lines:
            if (s["city"]==city):
                data = dict(s)
                # Convert data types
                data['temp']=float(data['temp'])
                data['pressure']=int(data['pressure'])
                data['humidity']=int(data['humidity'])
                data['temp_min']=float(data['temp_min'])
                data['temp_max']=float(data['temp_max'])
                data['speed']=float(data['speed'])
                data['deg']=int(data['deg'])
                data['lat']=float(data['lat'])
                data['lon']=float(data['lon'])
    return data


def get_current_weather(city, country, apikey):  
    # get current conditions in specified location
    # get_current_weather('boston','us',key)
    import urllib.request
    import json    
    # read current conditions
#        url = "https://api.openweathermap.org/data/2.5/weather?q=Boston,us&appid=11111"
    try:
        url = "https://api.openweathermap.org/data/2.5/weather?q="+city+","+country+"&units=imperial&appid="+apikey        
        response = urllib.request.urlopen(url)
        html = response.read()
        json_data = json.loads(html)
        
    except urllib.error.URLError:
        # if weather API doesnt work, read the file
        json_data = read_backup(city)
          
    return json_data

def parse_json(json_data):
    # parse and extract json data 
    import datetime
    try:
        #select meteorological and location data from dictionary
        weather_info = json_data['main']
        weather_info.update(json_data['wind'])
        weather_info['city'] = json_data['name']
        weather_info['lat'] = json_data['coord']['lat']
        weather_info['lon'] = json_data['coord']['lon']
#       # add date and time
        now = datetime.datetime.now()
        weather_info['current_time']=str(now)
            
    except KeyError:
        # use current dictionary 
        try:
            json_data.pop('City')
            weather_info = json_data
        except:
            print('Something else went wrong')
    return weather_info

def get_forecast(city, country, apikey):
    # get forecast conditions in specified location
    import urllib.request
    import json   
    try:
        url = "https://api.openweathermap.org/data/2.5/forecast?q="+city+","+country+"&units=imperial&appid="+apikey        
        response = urllib.request.urlopen(url)
        html = response.read()
        json_data = json.loads(html)
    except: 
        import csv
        lines = []
        with open('backupforecast.csv',newline='') as csvfile:
            reader = csv.DictReader(csvfile,delimiter=',')
            for row in reader:
                lines.append(row)
        json_data = ""
        for s in lines:
            if (s["City"]==city):
                json_data = dict(s)        
    return json_data

def parse_forecast(json_data):
    import array
    # parse forecast json data
    try:
        data = json_data['list']
        # create arrays
        temp = array.array('f')
        pressure = array.array('f')
        humidity = array.array('f')
        speed = array.array('f')
        deg = array.array('f')
        date = [];
        
        # loop over all and add to arrays
        for i in range(40):
            x1 = data[i]
            temp.append(x1['main']['temp'])
            pressure.append(x1['main']['pressure'])
            humidity.append(x1['main']['humidity'])
            speed.append(x1['wind']['speed'])
            deg.append(x1['wind']['deg'])
            date.append(x1['dt_txt'])
                       
        # create dictionary
        weather_info = dict(current_time=date,temp=temp,deg=deg,
                                speed=speed,humidity=humidity,pressure=pressure)         
    except KeyError:
        # use current dictionary 
        try:
            json_data.pop('City')
            weather_info = json_data
        except:
            print('Something else went wrong')
    return weather_info



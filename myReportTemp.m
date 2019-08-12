function [t,airQual] = myReportTemp()
 
    apikey = readtable("accessKey.txt","TextType","string"); 
    jsonData = py.weather.get_current_weather("Boston","US",apikey.Key(1));
    weatherData = py.weather.parse_json(jsonData);
    data = struct(weatherData);
    t = data.temp;
    airQual = predictAirQual(weatherData);
    
end 
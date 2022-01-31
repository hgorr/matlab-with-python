function [currentData,forecast] = ReadDataFromWeb(city,apikey)
% CURRENTAIRQUAL Read data from web api and rearrange

% Copyright 2018-2020 The MathWorks, Inc.

% Check inputs

if nargin < 2
    t = readtable("accessKey.txt");
    apikey = t.Key;
end
if nargin < 1
    city = "Boston";
end

city = convertCharsToStrings(city);

if contains(city,",")
    city =  extractBefore(city,",");
    city = strip(city);
end

% Get current weather
try
    response = getCurrentWeather(city,apikey);
    data = parseJSON(response);
    % Convert data types
    currentData = prepData(data);
catch
    % Read backup data
    currentData = readCurrentData(city);
end


% Get forecast data
try
    response = getForecastData(city,apikey);
    forecast = parseJSONforecast(response);
catch
    forecast = readForecastData(city);
end
forecast.DateLocal = datetime(forecast.DateLocal);
forecast = table2timetable(forecast);
% Add DP
forecast.DP = forecast.T-(9/25)*(100-forecast.RH);

% Select data for model prediction
forecast = forecast(:,["T","P",...
    "DP","RH","WindDir","WindSpd"]);

end

%% Helper funs
function response = getCurrentWeather(city,apikey)
url = "https://api.openweathermap.org/data/2.5/weather?q="+city+...
    ",us&units=imperial&appid="+apikey;
response = webread(url);

end

function response = getForecastData(city,apikey)
url = "https://api.openweathermap.org/data/2.5/forecast?q="+city+...
    ",us&units=imperial&appid="+apikey;
response = webread(url);

end

function weather_info = parseJSON(response)
T = response.main.temp;
RH = response.main.humidity;
P = response.main.pressure;
WindDir = response.wind.deg;
WindSpd = response.wind.speed;
DateLocal = datetime('now');
lat = response.coord.lat;
lon = response.coord.lon;
city = string(response.name);
% Create new table
weather_info = table(DateLocal,T,P,...
    WindDir,WindSpd,RH,city,lat,lon);
end

function weather_info = parseJSONforecast(response)
% data = response.forecast.simpleforecast.forecastday;
list = response.list;
% create arrays
weather_info = table('Size',[40,6],'VariableNames',["DateLocal",...
    "T","RH","P","WindDir","WindSpd"],...
    'VariableTypes',["string",repmat("double",1,5)]);

for ii = 1:40
    % extract data
    if isstruct(list)
        x1 = list(ii);
    else
        x1 = list{ii};
    end
    weather_info.DateLocal(ii) = x1.dt_txt;
    weather_info.WindDir(ii) = x1.wind.deg;
    weather_info.WindSpd(ii) = x1.wind.speed;
    weather_info.RH(ii) = x1.main.humidity;
    weather_info.T(ii) = x1.main.temp;
    weather_info.P(ii) = x1.main.pressure;
end

end

function data = readCurrentData(city)
% update outputs
data = readtable("backupdata.csv","TextType","string");
data.StateName = categorical(data.StateName);
[data.yy,data.MM,data.dd] = ymd(data.DateLocal);
data = data(data.City == city,2:end);
end

function data = readForecastData(city)
% update outputs
data = readtable("backupforecast.csv","TextType","string");
data = data(data.City == city,2:end);
end
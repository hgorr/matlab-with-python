function [airQual,T,Tforecast,dates,data,fdata] = CurrentAirQual(loc)
% CURRENTAIRQUAL Read data using Python weather module, then predict using
%   MATLAB machine learning model
%   [airQual,T,Tforecast,dates,data,fdata] = CurrentAirQual("Boston")


% The following is only for deployment, so the compiler will recognize the model
%#function CompactClassificationEnsemble

% Mange inputs
if nargin < 1
    loc = "Boston";
end
loc = convertCharsToStrings(loc);

if contains(loc,",")
    loc =  extractBefore(loc,",");
    loc = strip(loc);
end

% Get access key
% Persist so it's only read once (could write a class, use Redis cache)
persistent apikey;
if isempty(apikey)
    apikey = readtable("accessKey.txt","TextType","string");
end

% Read current weather
try
    jsonData = py.weather.get_current_weather(loc,"US",apikey.Key(1));
    weatherData = py.weather.parse_current_json(jsonData);
    T = weatherData{'temp'};
    
    % Convert data types and predict (return data for use in MATLAB)
    if nargout >= 5
        [airQual,data] = predictAirQual(weatherData);
    else
        airQual = predictAirQual(weatherData);
    end
    
    % 10 day forecast
    if nargout > 2
        jsonData = py.weather.get_forecast(loc,"US",apikey.Key);
        forecast = py.weather.parse_forecast_json(jsonData);
        
        % The last output indicates a MATLAB conversion of all forecast data
        if nargout == 6
            fdata = convertData(forecast);
        end
        % Otherwise, just extract data from dict and convert lists
        % Only need two outputs from dict
        t = forecast{'temp'};
        d = forecast{'current_time'};
        Tforecast = jsondecode(char(t));
        dates = string(cell(d))';
        
    end
    
catch  %Use MATLAB to read the data
    [data,fdata] = ReadDataFromWeb(loc);
    T = data.T;
    airQual = predictAirQual(data);
    dates = string(fdata.DateLocal);
    Tforecast = fdata.T;
    
end

end

function forecastData = convertData(forecast)
% Convert types and rearrange for use in MATLAB
s = struct(forecast);
names = string(fieldnames(s));
s.current_time = string(cell(s.current_time))';
for ii = 2:length(names)
    s.(names(ii)) = jsondecode(char(s.(names(ii))));
end

% Create a table for easy MATLAB data analysis
forecastData = struct2table(s);
% Convert the dates and create a timetable
forecastData.current_time = datetime(forecastData.current_time,...
    "InputFormat","uuuu-MM-dd HH:mm:ss");
% Rename variables
forecastData.Properties.VariableNames = ["DateLocal","T","WindDir",...
    "WindSpd","RH","P"];
forecastData = table2timetable(forecastData);
% Calculate dew point
forecastData.DP = forecastData.T-(9/25)*(100-forecastData.RH);

% Rearrange for app (could also use movevars())
forecastData = forecastData(:,["T","P","DP","RH",...
    "WindDir","WindSpd"]);

end
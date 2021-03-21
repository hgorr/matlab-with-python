% Set up python path
pathToAQ = fileparts(which('weather.py'));
if count(py.sys.path,pathToAQ) == 0
    insert(py.sys.path,int32(0),pathToAQ);
end
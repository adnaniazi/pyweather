from pyowm import OWM
API_key = '1330050f05c5c2c1f05e678136d1ebc2'
owm = OWM(API_key)  # global object

obs = owm.weather_at_place('London,uk')
country = obs._location._country
longitude = obs._location._lon
latitude = obs._location._lat
cityID = obs._location._ID
city = obs._location._name

temperature_avg_min_max = obs._weather._temperature # gives temperature in Kelvin
avg_temp = temperature_avg_min_max['temp']
min_temp = temperature_avg_min_max['temp_min']
max_temp = temperature_avg_min_max['temp_max']

sunrise_time = obs._weather._sunrise_time # unix time
sunset_time = obs._weather._sunset_time
detailed_status = obs._weather._detailed_status # few clouds, heavy rain etc.
visibility_distance = obs._weather._visibility_distance
humiditiy = obs._weather._humidity
wind = obs._weather._wind
pressure = obs._weather._pressure


# make a three hour forecast object fc and extract
fc= owm.three_hours_forecast("London")
number_of_available_observations = fc._forecast.__len__()
for i in range(number_of_available_observations-1, -1, -1):
    three_hour_fc = fc._forecast._weathers.pop(i)
    print(three_hour_fc._reference_time, three_hour_fc._status, three_hour_fc._temperature, three_hour_fc._weather_icon_name)

# make a daily forcast object fd
print("\nDaily forecasts")
fd = owm.daily_forecast(name="London", limit = 7)

number_of_available_observations = fd._forecast.__len__()
print(number_of_available_observations)
for i in range(number_of_available_observations-1, -1, -1):
    three_hour_fd = fd._forecast._weathers.pop(i)
    print(three_hour_fd._reference_time, three_hour_fd._status, three_hour_fd._temperature, three_hour_fd._weather_icon_name)










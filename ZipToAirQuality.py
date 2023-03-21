import json
import requests
from geopy.geocoders import Nominatim

def pretty_print_dict(d):
    print(json.dumps(d, indent=4))

'''
get_air_quality(lat, long)

This function retrieves the latest air quality data for a given latitude and longitude coordinates using the OpenAQ API.

Args:
lat: (float) representing the latitude of the location.
long: (float) representing the longitude of the location.

Returns:
    location (str):     representing the name of the location where the air quality was measured.
    city (str):         representing the name of the city where the air quality was measured.
    lastUpdated (str):  representing the date and time when the air quality data was last updated.
    measurements (dict):containing the air quality measurements with the following keys:
    parameter (str):    representing the type of pollutant being measured (e.g. PM2.5, PM10, O3, NO2).
    value (float):      representing the measured value of the pollutant.
    unit (str):         representing the unit of measurement.
    quality: (str)      representing the air quality index based on the measured value of the pollutant.
        - Possible values for quality are: Hazardous, Very Unhealthy, Unhealthy, Unhealthy for Sensitive Groups, Moderate, Good, Very Good.

Note: If the function is unable to retrieve the air quality data from the OpenAQ API, it returns None.
'''
def get_air_quality(lat, long):
    url = "https://api.openaq.org/v1/latest"
    params = {
        "coordinates": f"{lat},{long}",
        "radius": 10000, # Radius in meters
        "limit": 1, # Limit to one result
        "sort": "desc", # Sort by descending order
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "results" not in data:
        return None

    result = data["results"][0]

    air_quality_data = {
        "location": result["location"],
        "city": result["city"],
        "lastUpdated": result["measurements"][0]["lastUpdated"],
        "measurements": {}
    }

    for measurement in result["measurements"]:
        parameter = measurement["parameter"]
        value = measurement["value"]
        unit = measurement["unit"]
        air_quality_data["measurements"][parameter] = {"value": value, "unit": unit}

        if parameter == "pm25":
            if value > 250.5:
                air_quality_data["measurements"][parameter]["quality"] = "Hazardous"
            elif value > 150.5:
                air_quality_data["measurements"][parameter]["quality"] = "Very Unhealthy"
            elif value > 55.5:
                air_quality_data["measurements"][parameter]["quality"] = "Unhealthy"
            elif value > 35.5:
                air_quality_data["measurements"][parameter]["quality"] = "Unhealthy for Sensitive Groups"
            elif value > 12.1:
                air_quality_data["measurements"][parameter]["quality"] = "Moderate"
            else:
                air_quality_data["measurements"][parameter]["quality"] = "Good"
        elif parameter == "pm10":
            if value > 350.5:
                air_quality_data["measurements"][parameter]["quality"] = "Very Unhealthy"
            elif value > 250.5:
                air_quality_data["measurements"][parameter]["quality"] = "Unhealthy"
            elif value > 150.5:
                air_quality_data["measurements"][parameter]["quality"] = "Poor"
            elif value > 55.5:
                air_quality_data["measurements"][parameter]["quality"] = "Good"
            else:
                air_quality_data["measurements"][parameter]["quality"] = "Very Good"
        elif parameter == "o3":
            if value > 0.125:
                air_quality_data["measurements"][parameter]["quality"] = "Very Unhealthy"
            elif value > 0.095:
                air_quality_data["measurements"][parameter]["quality"] = "Unhealthy"
            elif value > 0.065:
                air_quality_data["measurements"][parameter]["quality"] = "Moderate"
            elif value > 0.035:
                air_quality_data["measurements"][parameter]["quality"] = "Good"
            else:
                air_quality_data["measurements"][parameter]["quality"] = "Very Good"
        elif parameter == "no2":
            if value > 0.2:
                air_quality_data["measurements"][parameter]["quality"] = "Very Unhealthy"
            elif value > 0.1:
                air_quality_data["measurements"][parameter]["quality"] = "Unhealthy"
            elif value > 0.05:
                air_quality_data["measurements"][parameter]["quality"] = "Moderate"
            elif value > 0.025:
                air_quality_data["measurements"][parameter]["quality"] = "Good"
            else:
                air_quality_data["measurements"][parameter]["quality"] = "Very Good"

    return air_quality_data

'''
get_air_quality_by_zip(zip_code: str, country_code: str) -> str

This function retrieves the air quality data for a given zip code and country code. 
It first uses the geopy library's geolocator to convert the zip code and country code into latitude and longitude coordinates. 
If the location is invalid, the function returns an error message. Otherwise, the latitude and longitude coordinates are rounded to 3 decimal places, 
and the get_air_quality() function is called to retrieve the air quality data for that location. The resulting data is then returned.

Args:
    zip_code (str):     A string representing the zip code of the location.
    country_code (str): A string representing the country code of the location.

Returns:
    air_quality_data (dict): A dictionary containing the air quality data for the location, or an error message if the location is invalid.
'''
def get_air_quality_by_zip(zip_code: str, country_code: str) -> str:

    # get lat and long from zip code
    geolocator = Nominatim(user_agent="geoapi")
    location = geolocator.geocode(f"{zip_code}, {country_code}")
    if not location:
        return f"Invalid Zip code or Country code: {zip_code}, {country_code}"

    # extract lat and long from geolocator instance and round to 3 decimal places
    latitude, longitude = round(location.latitude,3), round(location.longitude,3)

    # retrieve the air_quality using openaq
    air_quality_data = get_air_quality(latitude, longitude)

    return air_quality_data

'''
pm25_to_aqi(pm25) and calc_aqi(Cp, Ih, Il, BPh, BPl)

These functions approximate the AQI from the pm2.5 measurement. Typically AQI would be estimated by multiple pm2.5 measurements over a 24 hour period though, which makes this an estiamte.

Args:
    pm25 (float): A float representing the pm25 measurement

Returns:
    AQI (float): a piece-wise linear approximation of the AQI

Important: This is an estimate of aqi and could be improved by getting historic data and averaging the AQI estimates.
'''
def pm25_to_aqi(pm25):
    if pm25 < 0:
        return None
    elif pm25 > 500:
        return 500
    elif pm25 > 350.5:
        return calc_aqi(pm25, 500, 401, 500, 350.5)
    elif pm25 > 250.5:
        return calc_aqi(pm25, 400, 301, 350.4, 250.5)
    elif pm25 > 150.5:
        return calc_aqi(pm25, 300, 201, 250.4, 150.5)
    elif pm25 > 55.5:
        return calc_aqi(pm25, 200, 151, 150.4, 55.5)
    elif pm25 > 35.5:
        return calc_aqi(pm25, 150, 101, 55.4, 35.5)
    elif pm25 > 12.1:
        return calc_aqi(pm25, 100, 51, 35.4, 12.1)
    elif pm25 >= 0:
        return calc_aqi(pm25, 50, 0, 12, 0)

def calc_aqi(Cp, Ih, Il, BPh, BPl):
    a = (Ih - Il)
    b = (BPh - BPl)
    c = (Cp - BPl)
    return round((a/b) * c + Il)

"""
This function retrieves the air quality data by a given zip code and country code, calculates the AQI (Air Quality Index)
for the pm25 measurement and returns all measurements along with the calculated AQI in a dictionary.

Args:
    zip_code (str): A string representing a zip code, default is "19406".
    country (str): A string representing a country code, default is "US".

Returns:
    measurements (dict): A dictionary containing the air quality measurements and the calculated AQI for pm25.
"""
def get_air_quality_measurements_by_zip(zip_code="19406", country="US"):
    air_quality_data = get_air_quality_by_zip(zip_code, country)

    location = air_quality_data['location']

    measurements = air_quality_data['measurements']

    AQI_package = None

    for AQtype in measurements:
        value = measurements[AQtype]['value'] 
        if AQtype == 'pm25':
            AQI = pm25_to_aqi(value)

            AQI_package = {'value': AQI, 'quality': measurements[AQtype]['quality']}
    
    measurements['AQI'] = AQI_package
    measurements['location'] = location

    return measurements

### Main Code ###

# Get Air Quality measurements from a zip code
AQ_measurements = get_air_quality_measurements_by_zip(zip_code="19406")

# Print the returned dictionary using a helper function (pretty_print_dict) Note: AQI means Air Quality Index 
pretty_print_dict(AQ_measurements)

from datetime import datetime
from geopy.exc import GeocoderTimedOut, GeocoderQueryError
from geopy.geocoders import Nominatim
from geopy import geocoders
from c_data_cleaning import *


def earthquakes_data():
    df_earthquake = pd.read_csv('earthquakes.csv', sep=",")

    # Drop columns I dont interest
    df_earthquake = df_earthquake.drop(df_earthquake.columns[8], 1)
    df_earthquake = df_earthquake.drop(df_earthquake.columns[7], 1)

    # Drop rows which has longitude and latitude more than ... because they are not from canada
    # there are some rows that are of usa
    df_earthquake = df_earthquake.drop(
        df_earthquake[(df_earthquake['latitude'] < 42) | (df_earthquake['latitude'] > 83)].index)
    df_earthquake = df_earthquake.drop(
        df_earthquake[(abs(df_earthquake['longitude']) < 53) | (abs(df_earthquake['longitude']) > 141)].index)

    # Fill NaNs of magnitude with 0
    df_earthquake = fix_nans(df_earthquake, 'magnitude type')
    df_earthquake['YEAR'] = pd.to_datetime(df_earthquake['date']).dt.year

    # Drop many rows because due to memory issues I cant work with more
    df_earthquake = df_earthquake.drop(df_earthquake[(df_earthquake['YEAR'] >= 1988)].index)

    # df_tornado.to_csv(r'C:\Users\miksm\Desktop\result.csv')
    print(len(df_earthquake))
    print(df_earthquake.head().to_string())
    return df_earthquake


def wildfires_data():
    df_wildfire = pd.read_csv('wildfare.csv', sep=",")

    # Drop columns I dont interest
    df_wildfire.drop(df_wildfire.columns.difference(['SRC_AGENCY', 'LATITUDE', 'LONGITUDE', 'YEAR', 'MONTH',
                                                     'DAY', 'DECADE', 'SIZE_HA', 'CAUSE']), 1, inplace=True)

    # Drop rows from year = -999
    df_wildfire = df_wildfire.drop(df_wildfire[(df_wildfire['YEAR'] == -999)].index)
    # Drop some rows because I cannot execute it in my computer due to memory issues
    df_wildfire = df_wildfire.drop(df_wildfire[(df_wildfire['YEAR'] <= 2005)].index)
    df_wildfire = df_wildfire.drop(df_wildfire[(df_wildfire['YEAR'] >= 2012)].index)

    # Fill NaNs of magnitude with 0
    df_wildfire = fix_nans(df_wildfire, 'CAUSE')
    df_wildfire = df_wildfire.replace(r'^\s+$', np.nan, regex=True)
    df_wildfire['DECADE'].fillna("2010-2019", inplace=True)

    return df_wildfire


def general_data_preprocessing():
    df_graldata = pd.read_csv('general_data.csv', sep=",")

    # Drop columns I dont interest
    df_graldata.drop(
        df_graldata.columns.difference(['EVENT TYPE', 'PLACE', 'EVENT', 'COMMENTS', 'FATALITIES', 'INJURED / INFECTED',
                                        'EVACUATED', 'ESTIMATED TOTAL COST', 'EVENT END DATE',
                                        'UTILITY - PEOPLE AFFECTED', 'MAGNITUDE']), 1, inplace=True)

    df_graldata['EVENT END DATE'].fillna(df_graldata['EVENT'], inplace=True)
    df_graldata.fillna("0", inplace=True)  # see

    return df_graldata


# This is the method in which all preprocessing for tornadoes dataset was made.
# However, for efficiency reasons, the decision was made to execute this method, export a csv and then read directly from that csv so as not to waste time in pre-processing.
def tornadoes_preprocessing():
    df_tornado = pd.read_csv('tornadoes.csv', sep=",")
    df_graldata = general_data_preprocessing()

    # Drop columns Im not interested in
    df_tornado = df_tornado.drop('YYYYMMDDHHMM_UTC', 1)
    df_tornado = df_tornado.drop('HHMM_LOCAL', 1)
    df_tornado = df_tornado.drop('MOTION_DEG', 1)
    df_tornado = df_tornado.drop('FORECAST_REGION', 1)

    df_tornado = df_tornado.drop(df_tornado.columns[15], 1)
    df_tornado = df_tornado.drop(df_tornado.columns[15], 1)
    df_tornado = df_tornado.drop(df_tornado.columns[15], 1)

    # Fill nans
    df_tornado = fix_nans(df_tornado, 'DD_LOCAL')
    df_tornado = fix_nans(df_tornado, 'MM_LOCAL')
    df_tornado['MM_LOCAL'] = df_tornado['MM_LOCAL'].round()
    df_tornado['DD_LOCAL'] = df_tornado['DD_LOCAL'].round()

    df_tornado['HUMAN_FATAL'].fillna("0", inplace=True)
    df_tornado['HUMAN_INJ'].fillna("0", inplace=True)
    df_tornado['DMG_THOUS'].fillna("0", inplace=True)

    # end latitude and end longitude if they are empty, they will get the value of start lat and start long
    df_tornado['END_LAT_N'].fillna(df_tornado['START_LAT_N'], inplace=True)
    df_tornado['END_LON_W'].fillna(df_tornado['START_LON_W'], inplace=True)

    # I insert in df_tornado the latest data of tornadoes from general data
    recent_tornadoes = df_graldata[(df_graldata['EVENT TYPE'] == 'Tornado') & (df_graldata['EVENT'] > '2010-01-01')]

    gn = geocoders.GeoNames(username='micaelamelo')
    i = len(df_tornado)
    j = 0
    print(df_tornado)
    for m in range(len(recent_tornadoes) - 1):
        date = recent_tornadoes['EVENT'].values[j]
        dt = datetime.strptime(date, '%Y-%m-%d')
        location = gn.geocode(recent_tornadoes['PLACE'].values[j])

        aux = [dt.year, dt.month, dt.day, recent_tornadoes['PLACE'].values[j], recent_tornadoes['PLACE'].values[j],
               recent_tornadoes['MAGNITUDE'], location.longitude, location.latitude, location.longitude,
               location.latitude, 0, 0,
               recent_tornadoes['FATALITIES'].values[j], recent_tornadoes['INJURED / INFECTED'].values[j],
               recent_tornadoes['ESTIMATED TOTAL COST'].values[j]]
        df_tornado.loc[len(df_tornado)] = aux

        i = i + 1
        j = j + 1

    df_tornado.to_csv(r'C:\Users\miksm\Desktop\result_tornadoes.csv')


# I read directly from the csv exported in tornadoes_preprocessing()
def tornadoes_data():
    df_tornado = pd.read_csv('result_tornadoes.csv', sep=",")
    return df_tornado


# To find longitude and latitude of a place given the name as input
def findGeocode(city):
    # try and catch is used to overcome
    # the exception thrown by geolocator
    # using geocodertimedout
    try:
        try:
            # Specify the user_agent as your
            # app name it should not be none
            geolocator = Nominatim(user_agent="hazard")

            return geolocator.geocode(city, timeout=None)

        except GeocoderQueryError:

            return geolocator.geocode("Null Island", timeout=None)

    except GeocoderTimedOut:

        return findGeocode(city)


def lat_long(i, l):
    gn = geocoders.GeoNames(username='micaelamelo')
    location = findGeocode(i)

    if location is not None:
        if l == 1:
            return location.longitude
        else:
            return location.latitude
    else:
        return np.nan


# This is the method in which all preprocessing for floods dataset was made.
# However, for efficiency reasons, the decision was made to execute this method, export a csv and then read directly from that csv so as not to waste time in pre-processing.
def floods_preprocessing():
    df_graldata = general_data_preprocessing()
    df_floods = df_graldata[(df_graldata['EVENT TYPE'] == 'Flood')]
    df_floods = df_floods.reset_index(drop=True)
    # print(df_floods.head().to_string())

    df_floods['YEAR'] = pd.to_datetime(df_floods['EVENT']).dt.year
    df_floods['LONGITUDE'] = df_floods['PLACE'].apply(lambda x: lat_long(x, 1))
    df_floods['LATITUDE'] = df_floods['PLACE'].apply(lambda x: lat_long(x, 2))
    df_floods.to_csv(r'C:\Users\miksm\Desktop\result_floods.csv')


# Read directly from the result of pre processing
def floods_data():
    df_floods = pd.read_csv('result_floods.csv', sep=",", encoding='windows-1252')
    df_floods = df_floods.dropna()
    # print(df_floods.head().to_string())
    return df_floods


# This is the method in which all preprocessing for hurricanes dataset was made.
# However, for efficiency reasons, the decision was made to execute this method, export a csv and then read directly from that csv so as not to waste time in pre-processing.
def hurricanes_preprocessing():
    df_graldata = general_data_preprocessing()
    df_hurricanes = df_graldata[(df_graldata['EVENT TYPE'] == 'Hurricane / Typhoon / Tropical Storm')]
    df_hurricanes = df_hurricanes.reset_index(drop=True)

    df_hurricanes['YEAR'] = pd.to_datetime(df_hurricanes['EVENT']).dt.year

    gn = geocoders.GeoNames(username='micaelamelo')
    df_hurricanes['LONGITUDE'] = df_hurricanes['PLACE'].apply(lambda x: lat_long(x, 1))
    df_hurricanes['LATITUDE'] = df_hurricanes['PLACE'].apply(lambda x: lat_long(x, 2))
    df_hurricanes.dropna()
    df_hurricanes.to_csv(r'C:\Users\miksm\Desktop\result_hurricanes.csv')


# Read directly from the result of preprocessing
def hurricanes_data():
    df_hurricanes = pd.read_csv('result_hurricanes.csv', sep=",")
    df_hurricanes = df_hurricanes.dropna()
    # print(df_hurricanes.head().to_string())
    return df_hurricanes


if __name__ == "__main__":
    # earthquakes_data()
    # wildfires_data()
    # tornadoes_data()
    # general_data_preprocessing()
    # hurricanes_data()
    floods_data()
    hurricanes_data()

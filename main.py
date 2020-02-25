import pandas as pd
import folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter


def open_csv(path):
    '''(str) -> DataFrame
    Opens .csv file and Return Data Frame with data from this file.
    '''
    data = pd.read_csv(path, error_bad_lines=False, warn_bad_lines=False)
    df = pd.DataFrame(data)
    return df


def get_address_from_coordinates(coordinate):
    '''str -> str
    Accept coordinates in format: lat, long,
    and return full address.

    >>> get_address_from_coordinates('49.8179844, 24.0065319')
    '4, Mykoly Arkasa Street, Помірки, Kulparkiv, Lviv, Frankivskyi District, Lviv City Council, Lviv Oblast, 79053, Ukraine'
    >>> get_address_from_coordinates('40.7410861, -73.9896297241625')
    'Flatiron Building, 175, 5th Avenue, Flatiron District, Manhattan Community Board 5, Manhattan, New York County, New York, 10010, United States of America'
    '''
    geolocator = Nominatim(user_agent="specify_your_app_name_here")
    reverse = RateLimiter(geolocator.reverse, min_delay_seconds=1, max_retries=100)
    location = geolocator.reverse(coordinate, language='en-UK')
    return str(location)


def get_list_of_movies(df, year, address):
    '''(DataFrame, int, str) -> list
    Return list of movies that were prodused in chosen year at chosen country.
    '''
    lst = []
    df = df[df['year'] == year].reset_index()
    df['common_words_in_address'] = None
    set_address = set(address.replace(',', '').split(' '))
    for ind in df.index:
        df.loc[ind, 'common_words_in_address'] = int(len(set(str(df.loc[ind, 'location']).split(' ')) & set_address))
    df = df.sort_values(['common_words_in_address'])
    new_df = df.iloc[-11: -1]
    for i in range(10):
        # adds location and name of film to lst
        lst.append(tuple((new_df.iloc[i, 0], new_df.iloc[i, 3])))
    return lst


def get_coordinates(lst):
    '''list -> list
    Return list of tuples with name and coordinate (latitude, longitude) of films
    '''
    coordinates = []
    geolocator = Nominatim(user_agent="specify_your_app_name_here")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1, max_retries=10)
    for tpl in lst:
        location = geolocator.geocode(tpl[1])
        # if geocode return None
        try:
            coordinates.append(tuple((tpl[0], (location.latitude, location.longitude))))
        except AttributeError:
            continue
    return coordinates


if __name__ == '__main__':
    year = input('Enter a year of movies, please: ')
    locatione = input('Please enter your location (format: lat, long): ')
    print('loading...')
    addres = get_address_from_coordinates(locatione)
    data_csv = open_csv('locations.csv')
    lst_of_movies = get_list_of_movies(data_csv, year, addres)
    print('And a little bit more...')
    lst_of_coordinates = get_coordinates(lst_of_movies)

    m = folium.Map(location=[float(locatione.split(',')[0]), float(locatione.split(',')[1])], zoom_start=12)
    tooltip = 'click to know a name of film'
    for tpl in lst_of_coordinates:
        folium.Marker([tpl[1][0], tpl[1][1]], popup='{}'.format(tpl[0]), tooltip=tooltip).add_to(m)
    m.save('map.html')
    print('To watch the map, open "map.html"')

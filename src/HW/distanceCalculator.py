from geopy import distance
from geopy.geocoders import Nominatim
#avadia whit lolo
# Calculates distance between two cities and returns distance in kilometer
def distance_between_cities(c1,c2):
    geolocator = Nominatim(user_agent="geoapi Exercises")
    # These variables have the exact Location of the cities.
    l1 = geolocator.geocode(c1)
    l2 = geolocator.geocode(c2)
    loc1 = ((l1.latitude, l1.longitude))
    loc2 = ((l2.latitude, l2.longitude))
    return (distance.distance(loc1, loc2).kilometers)

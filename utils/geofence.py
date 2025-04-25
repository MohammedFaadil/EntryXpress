from geopy.distance import geodesic

# Phoenix Mall, Chennai - Coordinates
CENTER_COORDS = (13.087800, 80.278500)  # Latitude, Longitude of Phoenix Mall, Chennai
RADIUS_METERS = 500  # Radius in meters (300 meters radius for the mall)

def is_inside_mall(lat, lon):
    # Calculate the distance between the provided lat/lon and the mall center coordinates
    distance = geodesic((lat, lon), CENTER_COORDS).meters
    # If the distance is within the radius, user is inside the mall
    return distance <= RADIUS_METERS


#12.90511211781927, 80.15062437991924 amuthu supermarket
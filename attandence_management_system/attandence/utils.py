import math

def is_within_office_range(user_lat, user_long, office_lat, office_long, allowed_range_km=1.0):
    radius = 6371  # Earth radius in kilometers

    dlat = math.radians(office_lat - user_lat)
    dlon = math.radians(office_long - user_long)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(user_lat)) \
        * math.cos(math.radians(office_lat)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = radius * c

    return distance <= allowed_range_km

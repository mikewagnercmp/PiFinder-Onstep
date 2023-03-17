import datetime
import json
import math

from .solver import Skyfield_utils

def solve_debug(debug_dir, prefix):
    with open(f"{debug_dir}/{prefix}_location.json", "r") as f:
        location_dict = json.load(f)

    with open(f"{debug_dir}/{prefix}_datetime.json", "r") as f:
        dt = datetime.datetime.fromisoformat(f.readline().replace('"',''))

    with open(f"{debug_dir}/{prefix}_newsolve.json", "r") as f:
        solve_dict = json.load(f)

    roll = calc_roll(
            solve_dict["Alt"],
            solve_dict["Az"],
            location_dict["lat"],
            location_dict["lon"],
            location_dict["altitude"],
            dt,
            )
    roll2 = calc_roll(
            solve_dict["Alt"],
            solve_dict["Az"],
            location_dict["lat"],
            location_dict["lon"],
            location_dict["altitude"],
            dt,
            reverse=True
            )
    print(f"DT: {dt}")
    print(f"Ra: {solve_dict['RA']} / Dec: {solve_dict['Dec']}")
    print(f"Alt: {solve_dict['Alt']} / Az: {solve_dict['Az']}")
    print(f"T3 Roll: {solve_dict['Roll']} / Solve: {roll} / {roll2}")

def calc_roll(alt, az, lat, long, loc_alt, dt, reverse=False):
    sfu = Skyfield_utils()
    sfu.set_location( lat, long, loc_alt)
    np_alt, np_az = sfu.radec_to_altaz(0.01,89.99, dt, False)
    if az > 180:
        az = az - 360

    if reverse:
        roll = calc_bearing(alt,az,np_alt, np_az)
    else:
        roll = calc_bearing(np_alt, np_az, alt, az)
    return roll


def calc_bearing(lat1, long1, lat2, long2):
    # Convert latitude and longitude to radians
    lat1 = math.radians(lat1)
    long1 = math.radians(long1)
    lat2 = math.radians(lat2)
    long2 = math.radians(long2)
    # Calculate the bearing
    bearing = math.atan2(
        math.sin(long2 - long1) * math.cos(lat2),
        math.cos(lat1) * math.sin(lat2)
        - math.sin(lat1) * math.cos(lat2) * math.cos(long2 - long1),
    )
    # Convert the bearing to degrees
    bearing = math.degrees(bearing)
    # Make sure the bearing is positive
    bearing = (bearing + 360) % 360
    return bearing

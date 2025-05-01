# calculations.py
import swisseph as swe
from datetime import datetime, timedelta
import math
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Constants
PLANETS = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mercury': swe.MERCURY, 'Venus': swe.VENUS,
    'Mars': swe.MARS, 'Jupiter': swe.JUPITER, 'Saturn': swe.SATURN, 'Uranus': swe.URANUS,
    'Neptune': swe.NEPTUNE, 'Pluto': swe.PLUTO, 'North Node': swe.MEAN_NODE
}
ASPECTS = {
    'Conjunction': {'angle': 0, 'orb': 8}, 'Sextile': {'angle': 60, 'orb': 6},
    'Square': {'angle': 90, 'orb': 8}, 'Trine': {'angle': 120, 'orb': 8},
    'Opposition': {'angle': 180, 'orb': 8}
}
SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio',
         'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

def get_julian_day(date_str, time_str, tz_offset):
    """Convert birth date, time, and timezone offset to Julian Day."""
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    dt_utc = dt - timedelta(hours=tz_offset)
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                      dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600)

def format_degrees(deg):
    """Convert decimal degrees to degrees, minutes, and seconds."""
    degrees = int(deg)
    minutes = int((deg - degrees) * 60)
    seconds = int(((deg - degrees) * 60 - minutes) * 60)
    return f"{degrees}° {minutes}' {seconds}\""

def calculate_sidereal_position(jd, planet_id):
    """Calculate sidereal position for a planet using Lahiri ayanamsa."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    result = swe.calc_ut(jd, planet_id, swe.FLG_SIDEREAL)
    logging.debug(f"Result from swe.calc_ut for planet {planet_id}: {result}")
    
    # Robust tuple handling
    try:
        # swe.calc_ut typically returns (lon_data, ..., speed, ...)
        # lon_data is a tuple (lon, lat, dist, ...) when FLG_SIDEREAL is used
        lon = float(result[0][0])  # Extract longitude from first tuple element
        # Speed is typically at index 3 for retrograde check
        retrograde = result[3] < 0 if len(result) > 3 and planet_id != swe.MEAN_NODE else False
    except (IndexError, TypeError) as e:
        logging.error(f"Error parsing swe.calc_ut result {result}: {str(e)}")
        raise ValueError(f"Failed to extract longitude from {result} for planet {planet_id}")
    
    return lon, retrograde

def calculate_midpoint(lon1, lon2):
    """Calculate the midpoint longitude using the shortest arc."""
    lon1, lon2 = lon1 % 360, lon2 % 360
    diff = abs(lon1 - lon2)
    if diff > 180:
        diff = 360 - diff
        if lon1 > lon2:
            lon1, lon2 = lon2, lon1
        mid = (lon1 + diff / 2 + 180) % 360
    else:
        mid = (lon1 + lon2) / 2
    return mid

def calculate_planetary_positions(jd):
    """Calculate sidereal planetary positions."""
    positions = {}
    for planet_name, planet_id in PLANETS.items():
        lon, retrograde = calculate_sidereal_position(jd, planet_id)
        sign_idx = int(lon // 30)
        sign = SIGNS[sign_idx]
        degree_in_sign = lon % 30
        positions[planet_name] = {
            'longitude': lon,
            'sign': sign,
            'degree': format_degrees(degree_in_sign),
            'retrograde': retrograde
        }
    # South Node as 180° opposite North Node
    nn_lon = positions['North Node']['longitude']
    sn_lon = (nn_lon + 180) % 360
    sign_idx = int(sn_lon // 30)
    sign = SIGNS[sign_idx]
    degree_in_sign = sn_lon % 30
    positions['South Node'] = {
        'longitude': sn_lon,
        'sign': sign,
        'degree': format_degrees(degree_in_sign),
        'retrograde': True
    }
    return positions

def calculate_ascendant_and_houses(jd, lat, lon):
    """Calculate Ascendant, MC, and ascendant sign index."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    house_cusps, ascmc = swe.houses_ex(jd, lat, lon, b'W', flags=swe.FLG_SIDEREAL)
    asc = ascmc[0] % 360
    mc = ascmc[1] % 360
    asc_sign_idx = int(asc // 30)
    return asc, mc, asc_sign_idx

def assign_planets_to_houses(positions, asc_sign_idx):
    """Assign planets to Whole Sign houses."""
    houses = {}
    for planet, data in positions.items():
        longitude = data['longitude']
        planet_sign_idx = int(longitude // 30)
        house = (planet_sign_idx - asc_sign_idx) % 12 + 1
        houses[planet] = house
    return houses

def calculate_composite_positions(pos_a, pos_b):
    """Calculate composite planetary positions from two natal charts."""
    positions = {}
    for planet in pos_a:
        lon_a = pos_a[planet]['longitude']
        lon_b = pos_b[planet]['longitude']
        lon_mid = calculate_midpoint(lon_a, lon_b)
        sign_idx = int(lon_mid // 30)
        sign = SIGNS[sign_idx]
        degree_in_sign = lon_mid % 30
        retrograde = pos_a[planet]['retrograde'] or pos_b[planet]['retrograde']
        positions[planet] = {
            'longitude': lon_mid,
            'sign': sign,
            'degree': format_degrees(degree_in_sign),
            'retrograde': retrograde
        }
    return positions

def calculate_composite_angles(jd_a, jd_b, lat_a, lon_a, lat_b, lon_b):
    """Calculate composite Ascendant and MC using midpoint method."""
    jd_mid = (jd_a + jd_b) / 2
    ref_lat = (lat_a + lat_b) / 2
    ref_lon = (lon_a + lon_b) / 2
    _, ascmc_mid = swe.houses_ex(jd_mid, ref_lat, ref_lon, b'W', flags=swe.FLG_SIDEREAL)
    asc_composite = ascmc_mid[0] % 360
    mc_composite = ascmc_mid[1] % 360
    asc_sign_idx_composite = int(asc_composite // 30)
    return asc_composite, mc_composite, asc_sign_idx_composite

def calculate_aspects(positions):
    """Calculate aspects between composite planets and points."""
    aspects = []
    points = list(positions.keys())
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            p1, p2 = points[i], points[j]
            lon1, lon2 = positions[p1]['longitude'], positions[p2]['longitude']
            diff = min(abs(lon1 - lon2), 360 - abs(lon1 - lon2))
            for aspect_name, data in ASPECTS.items():
                if abs(diff - data['angle']) <= data['orb']:
                    aspects.append({
                        'point_a': p1,
                        'point_b': p2,
                        'aspect': aspect_name,
                        'angle': diff,
                        'orb': abs(diff - data['angle'])
                    })
    return aspects

def validate_person_data(person_data, person_label):
    """Validate required fields for birth data."""
    required = ['date', 'time', 'lat', 'lon', 'tz_offset']
    missing = [field for field in required if field not in person_data]
    if missing:
        return False, f"Missing fields for {person_label}: {', '.join(missing)}"
    return True, None

def calculate_composite_chart(data):
    """
    Calculate the composite chart for two individuals based on birth data.
    
    Parameters:
    - data: Dictionary containing person_a and person_b data with date, time, lat, lon, tz_offset, and optional name.
    
    Returns:
    - Dictionary containing the composite chart data or raises an exception on error.
    """
    # Extract data for Person A
    person_a = data['person_a']
    name_a = person_a.get('name', 'Person A')
    jd_a = get_julian_day(person_a['date'], person_a['time'], float(person_a['tz_offset']))
    lat_a = float(person_a['lat'])
    lon_a = float(person_a['lon'])
    pos_a = calculate_planetary_positions(jd_a)
    asc_a, mc_a, asc_sign_idx_a = calculate_ascendant_and_houses(jd_a, lat_a, lon_a)
    houses_a = assign_planets_to_houses(pos_a, asc_sign_idx_a)

    # Extract data for Person B
    person_b = data['person_b']
    name_b = person_b.get('name', 'Person B')
    jd_b = get_julian_day(person_b['date'], person_b['time'], float(person_b['tz_offset']))
    lat_b = float(person_b['lat'])
    lon_b = float(person_b['lon'])
    pos_b = calculate_planetary_positions(jd_b)
    asc_b, mc_b, asc_sign_idx_b = calculate_ascendant_and_houses(jd_b, lat_b, lon_b)
    houses_b = assign_planets_to_houses(pos_b, asc_sign_idx_b)

    # Composite calculations
    positions = calculate_composite_positions(pos_a, pos_b)
    asc_composite, mc_composite, asc_sign_idx_composite = calculate_composite_angles(
        jd_a, jd_b, lat_a, lon_a, lat_b, lon_b
    )
    houses_composite = assign_planets_to_houses(positions, asc_sign_idx_composite)

    # Calculate aspects including Ascendant and Midheaven
    positions_with_angles = {
        **positions,
        'Ascendant': {'longitude': asc_composite, 'sign': SIGNS[asc_sign_idx_composite], 'degree': format_degrees(asc_composite % 30), 'retrograde': False},
        'Midheaven': {'longitude': mc_composite, 'sign': SIGNS[int(mc_composite // 30)], 'degree': format_degrees(mc_composite % 30), 'retrograde': False}
    }
    aspects = calculate_aspects(positions_with_angles)

    # Prepare natal data for Person A
    natal_a = {
        'planets': {planet: {**pos_a[planet], 'house': houses_a[planet]} for planet in pos_a},
        'ascendant': {'longitude': asc_a, 'sign': SIGNS[asc_sign_idx_a], 'degree': format_degrees(asc_a % 30)},
        'midheaven': {'longitude': mc_a, 'sign': SIGNS[int(mc_a // 30)], 'degree': format_degrees(mc_a % 30)},
        'houses': {i+1: SIGNS[(asc_sign_idx_a + i) % 12] for i in range(12)}
    }

    # Prepare natal data for Person B
    natal_b = {
        'planets': {planet: {**pos_b[planet], 'house': houses_b[planet]} for planet in pos_b},
        'ascendant': {'longitude': asc_b, 'sign': SIGNS[asc_sign_idx_b], 'degree': format_degrees(asc_b % 30)},
        'midheaven': {'longitude': mc_b, 'sign': SIGNS[int(mc_b // 30)], 'degree': format_degrees(mc_b % 30)},
        'houses': {i+1: SIGNS[(asc_sign_idx_b + i) % 12] for i in range(12)}
    }

    # Prepare composite data
    composite = {
        'planets': {planet: {**positions[planet], 'house': houses_composite[planet]} for planet in positions},
        'ascendant': {'longitude': asc_composite, 'sign': SIGNS[asc_sign_idx_composite], 'degree': format_degrees(asc_composite % 30)},
        'midheaven': {'longitude': mc_composite, 'sign': SIGNS[int(mc_composite // 30)], 'degree': format_degrees(mc_composite % 30)},
        'aspects': aspects,
        'houses': {i+1: SIGNS[(asc_sign_idx_composite + i) % 12] for i in range(12)}
    }

    # Construct response
    response = {
        'person_a': {
            'name': name_a,
            'natal': natal_a
        },
        'person_b': {
            'name': name_b,
            'natal': natal_b
        },
        'composite': composite
    }
    return response
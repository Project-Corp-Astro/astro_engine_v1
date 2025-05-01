# calculations.py
import swisseph as swe
from datetime import datetime, timedelta
import math
import logging

# Set up logging
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
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                    dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600)
    logging.debug(f"Calculated Julian Day: {jd}")
    return jd

def format_degrees(deg):
    """Convert decimal degrees to degrees, minutes, and seconds."""
    if not isinstance(deg, (float, int)):
        raise ValueError(f"Degree value must be a number, got {type(deg)}: {deg}")
    degrees = int(deg)
    minutes = int((deg - degrees) * 60)
    seconds = int(((deg - degrees) * 60 - minutes) * 60)
    return f"{degrees}° {minutes}' {seconds}\""

def calculate_planetary_positions(jd):
    """Calculate sidereal planetary positions using Lahiri ayanamsa."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    positions = {}
    for planet_name, planet_id in PLANETS.items():
        result = swe.calc_ut(jd, planet_id, swe.FLG_SIDEREAL)
        logging.debug(f"swe.calc_ut result for {planet_name}: {result}")
        
        # Ensure result is a tuple and has at least 1 element (longitude)
        if not isinstance(result, tuple):
            raise ValueError(f"swe.calc_ut for {planet_name} did not return a tuple: {result}")
        if len(result) < 1:
            raise ValueError(f"swe.calc_ut for {planet_name} returned empty or insufficient tuple: {result}")
        
        # Handle nested tuples if returned (some versions of swisseph may do this)
        lon = result[0]
        if isinstance(lon, tuple):
            if len(lon) < 1:
                raise ValueError(f"Nested tuple for {planet_name} longitude is empty: {lon}")
            lon = lon[0]
        
        # Ensure longitude is a number
        lon = float(lon)  # Convert to float to handle potential string or int types
        if not isinstance(lon, (float, int)):
            raise ValueError(f"Longitude for {planet_name} is not a number: {lon}")
        
        sign_idx = int(lon // 30)
        if not (0 <= sign_idx < 12):
            raise ValueError(f"Invalid sign index for {planet_name}: {sign_idx}")
        
        sign = SIGNS[sign_idx]
        degree_in_sign = lon % 30
        # Check for retrograde using speed (index 3) if available, default to False if not
        retrograde = result[3] < 0 if len(result) > 3 else False
        if planet_id == swe.MEAN_NODE:
            retrograde = True  # North Node is always retrograde
        
        positions[planet_name] = {
            'longitude': lon,
            'sign': sign,
            'degree': format_degrees(degree_in_sign),
            'retrograde': retrograde
        }
    
    # South Node calculation
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
    """Calculate Ascendant and Whole Sign house cusps."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    result = swe.houses_ex(jd, lat, lon, b'W', flags=swe.FLG_SIDEREAL)
    logging.debug(f"swe.houses_ex result: {result}")
    
    # Ensure result is a tuple with at least two elements (house_cusps, ascmc)
    if not isinstance(result, tuple) or len(result) < 2:
        raise ValueError(f"Unexpected return from swe.houses_ex: {result}")
    
    house_cusps, ascmc = result
    
    # Validate ascmc
    if not isinstance(ascmc, (list, tuple)) or len(ascmc) < 1:
        raise ValueError(f"Unexpected ascmc format from swe.houses_ex: {ascmc}")
    
    ascendant = float(ascmc[0]) % 360  # Ensure ascendant is a float
    if not isinstance(ascendant, (float, int)):
        raise ValueError(f"Ascendant is not a number: {ascendant}")
    
    asc_sign_idx = int(ascendant // 30)
    return ascendant, asc_sign_idx

def assign_planets_to_houses(positions, asc_sign_idx):
    """Assign planets to houses using Whole Sign system."""
    houses = {}
    for planet, data in positions.items():
        longitude = data['longitude']
        planet_sign_idx = int(longitude // 30)
        house = (planet_sign_idx - asc_sign_idx) % 12 + 1
        houses[planet] = house
    return houses

def calculate_aspects(pos_a, pos_b):
    """Calculate aspects between two sets of planetary positions."""
    aspects = []
    for planet_a, data_a in pos_a.items():
        for planet_b, data_b in pos_b.items():
            diff = abs(data_a['longitude'] - data_b['longitude'])
            diff = min(diff, 360 - diff)
            for aspect_name, aspect_data in ASPECTS.items():
                if abs(diff - aspect_data['angle']) <= aspect_data['orb']:
                    aspects.append({
                        'planet_a': planet_a,
                        'planet_b': planet_b,
                        'aspect': aspect_name,
                        'angle': diff,
                        'orb': abs(diff - aspect_data['angle'])
                    })
    return aspects

def analyze_house_overlays(pos_planets, asc_sign_idx):
    """Map one person's planets to the other's houses."""
    overlays = {}
    for planet, data in pos_planets.items():
        planet_sign_idx = int(data['longitude'] // 30)
        house = (planet_sign_idx - asc_sign_idx) % 12 + 1
        overlays[planet] = house
    return overlays

def evaluate_nodal_connections(pos_planets, pos_nodes):
    """Evaluate connections with North and South Nodes."""
    connections = []
    node_lons = {
        'North Node': pos_nodes['North Node']['longitude'],
        'South Node': pos_nodes['South Node']['longitude']
    }
    for planet, data in pos_planets.items():
        for node, node_lon in node_lons.items():
            diff = abs(data['longitude'] - node_lon)
            angle = min(diff, 360 - diff)
            if angle <= 5:  # 5° orb for nodal conjunctions
                connections.append({'planet': planet, 'node': node, 'angle': angle})
    return connections

def interpret_synastry(aspects, overlays_a_in_b, overlays_b_in_a, nodal_a, nodal_b):
    """Provide detailed interpretations of synastry factors."""
    interpretation = {
        'aspects': [],
        'house_overlays': {'a_in_b': [], 'b_in_a': []},
        'nodal_connections': {'person_a': [], 'person_b': []}
    }
    # Aspect Interpretations
    for aspect in aspects:
        planet_a, planet_b = aspect['planet_a'], aspect['planet_b']
        aspect_type = aspect['aspect']
        if aspect_type == 'Conjunction':
            interp = f"Person A's {planet_a} conjunct Person B's {planet_b}: A powerful blend of energies."
        elif aspect_type == 'Trine':
            interp = f"Person A's {planet_a} trine Person B's {planet_b}: Harmonious flow."
        elif aspect_type == 'Sextile':
            interp = f"Person A's {planet_a} sextile Person B's {planet_b}: Opportunities for growth."
        elif aspect_type == 'Square':
            interp = f"Person A's {planet_a} square Person B's {planet_b}: Tension and challenges."
        elif aspect_type == 'Opposition':
            interp = f"Person A's {planet_a} opposite Person B's {planet_b}: Polarizing dynamics."
        interpretation['aspects'].append(interp)
    # House Overlay Interpretations
    house_meanings = {
        1: "identity", 2: "resources", 3: "communication", 4: "home", 5: "creativity",
        6: "service", 7: "relationships", 8: "transformation", 9: "exploration",
        10: "career", 11: "friendships", 12: "subconscious"
    }
    for planet, house in overlays_a_in_b.items():
        interp = f"Person A's {planet} in Person B's {house} house: Influences {house_meanings[house]}."
        interpretation['house_overlays']['a_in_b'].append(interp)
    for planet, house in overlays_b_in_a.items():
        interp = f"Person B's {planet} in Person A's {house} house: Influences {house_meanings[house]}."
        interpretation['house_overlays']['b_in_a'].append(interp)
    # Nodal Connection Interpretations
    for conn in nodal_a:
        interp = f"Person A's {conn['planet']} conjunct Person B's {conn['node']}: Karmic tie."
        interpretation['nodal_connections']['person_a'].append(interp)
    for conn in nodal_b:
        interp = f"Person B's {conn['planet']} conjunct Person A's {conn['node']}: Karmic bond."
        interpretation['nodal_connections']['person_b'].append(interp)
    return interpretation

def validate_person_data(person_data, person_label):
    """Validate required fields for a person's birth data."""
    required_fields = ['date', 'time', 'lat', 'lon', 'tz_offset']
    missing_fields = [field for field in required_fields if field not in person_data]
    if missing_fields:
        return False, f"Missing fields for {person_label}: {', '.join(missing_fields)}"
    return True, None

def calculate_synastry(data):
    """
    Calculate synastry data for two individuals based on birth data.
    
    Args:
        data (dict): Contains 'person_a' and 'person_b' data with date, time, lat, lon, tz_offset, and optional name.
    
    Returns:
        dict: Contains synastry calculations and interpretations.
    """
    # Person A calculations
    person_a = data['person_a']
    name_a = person_a.get('name', 'Person A')
    jd_a = get_julian_day(person_a['date'], person_a['time'], person_a['tz_offset'])
    pos_a = calculate_planetary_positions(jd_a)
    asc_a, asc_sign_idx_a = calculate_ascendant_and_houses(jd_a, person_a['lat'], person_a['lon'])
    houses_a = assign_planets_to_houses(pos_a, asc_sign_idx_a)

    # Person B calculations
    person_b = data['person_b']
    name_b = person_b.get('name', 'Person B')
    jd_b = get_julian_day(person_b['date'], person_b['time'], person_b['tz_offset'])
    pos_b = calculate_planetary_positions(jd_b)
    asc_b, asc_sign_idx_b = calculate_ascendant_and_houses(jd_b, person_b['lat'], person_b['lon'])
    houses_b = assign_planets_to_houses(pos_b, asc_sign_idx_b)

    # Include Ascendant for aspects
    pos_a_with_asc = {**pos_a, 'Ascendant': {'longitude': asc_a, 'sign': SIGNS[asc_sign_idx_a], 'degree': format_degrees(asc_a % 30), 'retrograde': False}}
    pos_b_with_asc = {**pos_b, 'Ascendant': {'longitude': asc_b, 'sign': SIGNS[asc_sign_idx_b], 'degree': format_degrees(asc_b % 30), 'retrograde': False}}

    # Synastry analysis
    aspects = calculate_aspects(pos_a_with_asc, pos_b_with_asc)
    overlays_a_in_b = analyze_house_overlays(pos_a, asc_sign_idx_b)
    overlays_b_in_a = analyze_house_overlays(pos_b, asc_sign_idx_a)
    nodal_a = evaluate_nodal_connections(pos_a, pos_b)
    nodal_b = evaluate_nodal_connections(pos_b, pos_a)
    interpretation = interpret_synastry(aspects, overlays_a_in_b, overlays_b_in_a, nodal_a, nodal_b)

    # Response
    response = {
        'person_a': {
            'name': name_a,
            'birth_details': person_a,
            'ascendant': {'sign': SIGNS[asc_sign_idx_a], 'degree': format_degrees(asc_a % 30)},
            'planets': {k: {**v, 'house': houses_a[k]} for k, v in pos_a.items()}
        },
        'person_b': {
            'name': name_b,
            'birth_details': person_b,
            'ascendant': {'sign': SIGNS[asc_sign_idx_b], 'degree': format_degrees(asc_b % 30)},
            'planets': {k: {**v, 'house': houses_b[k]} for k, v in pos_b.items()}
        },
        'synastry': {
            'aspects': aspects,
            'house_overlays': {'a_in_b': overlays_a_in_b, 'b_in_a': overlays_b_in_a},
            'nodal_connections': {'person_a': nodal_a, 'person_b': nodal_b},
            'interpretation': interpretation
        }
    }
    return response
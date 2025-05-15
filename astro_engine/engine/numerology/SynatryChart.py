

import swisseph as swe
from datetime import datetime, timedelta
import math
import logging

# Set Swiss Ephemeris path (update to your ephemeris files' location)
swe.set_ephe_path('astro_api/ephe')

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

# Nakshatra list with start and end degrees
NAKSHATRAS = [
    ('Ashwini', 0, 13.3333), ('Bharani', 13.3333, 26.6667), ('Krittika', 26.6667, 40),
    ('Rohini', 40, 53.3333), ('Mrigashira', 53.3333, 66.6667), ('Ardra', 66.6667, 80),
    ('Punarvasu', 80, 93.3333), ('Pushya', 93.3333, 106.6667), ('Ashlesha', 106.6667, 120),
    ('Magha', 120, 133.3333), ('Purva Phalguni', 133.3333, 146.6667), ('Uttara Phalguni', 146.6667, 160),
    ('Hasta', 160, 173.3333), ('Chitra', 173.3333, 186.6667), ('Swati', 186.6667, 200),
    ('Vishakha', 200, 213.3333), ('Anuradha', 213.3333, 226.6667), ('Jyeshtha', 226.6667, 240),
    ('Mula', 240, 253.3333), ('Purva Ashadha', 253.3333, 266.6667), ('Uttara Ashadha', 266.6667, 280),
    ('Shravana', 280, 293.3333), ('Dhanishta', 293.3333, 306.6667), ('Shatabhisha', 306.6667, 320),
    ('Purva Bhadrapada', 320, 333.3333), ('Uttara Bhadrapada', 333.3333, 346.6667), ('Revati', 346.6667, 360)
]

# Set up logging
logging.basicConfig(level=logging.DEBUG)

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

def get_nakshatra_and_pada(longitude):
    """Determine the nakshatra and pada for a given longitude."""
    longitude = longitude % 360
    for nakshatra, start, end in NAKSHATRAS:
        if start <= longitude < end:
            position_in_nakshatra = longitude - start
            pada = math.ceil(position_in_nakshatra / 3.3333)
            return nakshatra, pada
    return 'Revati', 4  # Fallback for edge cases

def calculate_planetary_positions(jd):
    """Calculate sidereal planetary positions, nakshatra, and pada using Lahiri ayanamsa."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    positions = {}
    for planet_name, planet_id in PLANETS.items():
        result = swe.calc_ut(jd, planet_id, swe.FLG_SIDEREAL)
        logging.debug(f"swe.calc_ut result for {planet_name}: {result}")
        
        if not isinstance(result, tuple) or len(result) < 1:
            raise ValueError(f"swe.calc_ut for {planet_name} returned invalid data: {result}")
        
        lon = float(result[0] if not isinstance(result[0], tuple) else result[0][0])
        sign_idx = int(lon // 30)
        if not (0 <= sign_idx < 12):
            raise ValueError(f"Invalid sign index for {planet_name}: {sign_idx}")
        
        sign = SIGNS[sign_idx]
        degree_in_sign = lon % 30
        retrograde = result[3] < 0 if len(result) > 3 else False
        if planet_id == swe.MEAN_NODE:
            retrograde = True
        
        nakshatra, pada = get_nakshatra_and_pada(lon)
        
        positions[planet_name] = {
            'longitude': lon,
            'sign': sign,
            'degree': format_degrees(degree_in_sign),
            'retrograde': retrograde,
            'nakshatra': nakshatra,
            'pada': pada
        }
    
    nn_lon = positions['North Node']['longitude']
    sn_lon = (nn_lon + 180) % 360
    sign_idx = int(sn_lon // 30)
    sign = SIGNS[sign_idx]
    degree_in_sign = sn_lon % 30
    nakshatra, pada = get_nakshatra_and_pada(sn_lon)
    positions['South Node'] = {
        'longitude': sn_lon,
        'sign': sign,
        'degree': format_degrees(degree_in_sign),
        'retrograde': True,
        'nakshatra': nakshatra,
        'pada': pada
    }
    return positions

def calculate_ascendant_and_houses(jd, lat, lon):
    """Calculate Ascendant and Whole Sign house cusps."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    result = swe.houses_ex(jd, lat, lon, b'W', flags=swe.FLG_SIDEREAL)
    logging.debug(f"swe.houses_ex result: {result}")
    
    if not isinstance(result, tuple) or len(result) < 2:
        raise ValueError(f"Unexpected return from swe.houses_ex: {result}")
    
    house_cusps, ascmc = result
    ascendant = float(ascmc[0]) % 360
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
            if angle <= 5:
                connections.append({'planet': planet, 'node': node, 'angle': angle})
    return connections

def interpret_synastry(aspects, overlays_a_in_b, overlays_b_in_a, nodal_a, nodal_b):
    """Provide detailed interpretations of synastry factors."""
    interpretation = {
        'aspects': [],
        'house_overlays': {'a_in_b': [], 'b_in_a': []},
        'nodal_connections': {'person_a': [], 'person_b': []}
    }
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

def lahairi_synastry(person_data):
    """Calculate chart data for one person using Lahiri ayanamsa, including nakshatra and pada."""
    name = person_data.get('name', 'Person')
    jd = get_julian_day(person_data['date'], person_data['time'], person_data['tz_offset'])
    positions = calculate_planetary_positions(jd)
    ascendant, asc_sign_idx = calculate_ascendant_and_houses(jd, person_data['lat'], person_data['lon'])
    houses = assign_planets_to_houses(positions, asc_sign_idx)
    
    asc_nakshatra, asc_pada = get_nakshatra_and_pada(ascendant)
    ascendant_details = {
        'longitude': ascendant,
        'sign': SIGNS[asc_sign_idx],
        'degree': format_degrees(ascendant % 30),
        'retrograde': False,
        'nakshatra': asc_nakshatra,
        'pada': asc_pada
    }
    return {
        'name': name,
        'positions': positions,
        'ascendant': ascendant_details,
        'houses': houses,
        'asc_sign_idx': asc_sign_idx
    }
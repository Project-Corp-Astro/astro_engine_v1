import swisseph as swe
from datetime import datetime, timedelta
import math

# Zodiac signs (0-based index)
SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

# Nakshatra details: (name, start degree, end degree)
NAKSHATRAS = [
    ("Ashwini", 0, 13.333),
    ("Bharani", 13.333, 26.666),
    ("Krittika", 26.666, 40),
    ("Rohini", 40, 53.333),
    ("Mrigashira", 53.333, 66.666),
    ("Ardra", 66.666, 80),
    ("Punarvasu", 80, 93.333),
    ("Pushya", 93.333, 106.666),
    ("Ashlesha", 106.666, 120),
    ("Magha", 120, 133.333),
    ("Purva Phalguni", 133.333, 146.666),
    ("Uttara Phalguni", 146.666, 160),
    ("Hasta", 160, 173.333),
    ("Chitra", 173.333, 186.666),
    ("Swati", 186.666, 200),
    ("Vishakha", 200, 213.333),
    ("Anuradha", 213.333, 226.666),
    ("Jyeshta", 226.666, 240),
    ("Mula", 240, 253.333),
    ("Purva Ashadha", 253.333, 266.666),
    ("Uttara Ashadha", 266.666, 280),
    ("Shravana", 280, 293.333),
    ("Dhanishta", 293.333, 306.666),
    ("Shatabhisha", 306.666, 320),
    ("Purva Bhadrapada", 320, 333.333),
    ("Uttara Bhadrapada", 333.333, 346.666),
    ("Revati", 346.666, 360)
]

# Planet codes for Swiss Ephemeris
PLANETS = {
    'Sun': swe.SUN,
    'Moon': swe.MOON,
    'Mercury': swe.MERCURY,
    'Venus': swe.VENUS,
    'Mars': swe.MARS,
    'Jupiter': swe.JUPITER,
    'Saturn': swe.SATURN,
    'Rahu': swe.MEAN_NODE,
    'Ketu': swe.MEAN_NODE  # Ketu is opposite to Rahu
}

# Navamsa starting signs for each element
ELEMENT_NAVAMSA_START = {
    'Fire': 'Aries',
    'Earth': 'Capricorn',
    'Air': 'Libra',
    'Water': 'Cancer'
}

# Sign elements
SIGN_ELEMENTS = {
    'Aries': 'Fire', 'Taurus': 'Earth', 'Gemini': 'Air', 'Cancer': 'Water',
    'Leo': 'Fire', 'Virgo': 'Earth', 'Libra': 'Air', 'Scorpio': 'Water',
    'Sagittarius': 'Fire', 'Capricorn': 'Earth', 'Aquarius': 'Air', 'Pisces': 'Water'
}

def get_julian_day(date_str, time_str, tz_offset):
    """Convert local birth date and time to Julian Day in UT."""
    local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    ut_dt = local_dt - timedelta(hours=tz_offset)
    hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
    return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal, swe.GREG_CAL)

def calculate_sidereal_positions(jd):
    """Calculate sidereal longitudes and retrograde status of planets using Lahiri Ayanamsa."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)  # Lahiri Ayanamsa
    positions = {}
    for planet, code in PLANETS.items():
        if planet == 'Ketu':
            # Ketu is opposite to Rahu
            rahu_lon = positions['Rahu']['longitude']
            ketu_lon = (rahu_lon + 180) % 360
            positions['Ketu'] = {'longitude': ketu_lon, 'retrograde': True}  # Ketu is always retrograde
        else:
            # Calculate position and speed
            pos = swe.calc_ut(jd, code, swe.FLG_SIDEREAL | swe.FLG_SPEED)
            lon = pos[0][0] % 360
            speed = pos[0][3]  # Speed in longitude
            retrograde = speed < 0 if planet not in ['Sun', 'Moon'] else False  # Sun and Moon are never retrograde
            positions[planet] = {'longitude': lon, 'retrograde': retrograde}
    return positions

def get_sign_and_degree(longitude):
    """Determine natal sign and degrees within the sign from longitude."""
    sign_index = int(longitude // 30)  # Each sign is 30 degrees
    degrees_in_sign = longitude % 30
    return SIGNS[sign_index], degrees_in_sign

def get_nakshatra_and_pada(longitude):
    """Determine nakshatra and pada from longitude."""
    longitude = longitude % 360
    for nakshatra, start, end in NAKSHATRAS:
        if start <= longitude < end:
            nakshatra_name = nakshatra
            nakshatra_span = end - start
            pada = math.ceil((longitude - start) / (nakshatra_span / 4))
            return nakshatra_name, pada
    return "Unknown", 0  # Fallback in case of error

def get_navamsa_sign(natal_sign, degrees_in_sign):
    """Calculate the Navamsa sign for a planet."""
    element = SIGN_ELEMENTS[natal_sign]
    start_sign = ELEMENT_NAVAMSA_START[element]
    start_index = SIGNS.index(start_sign)
    navamsa_segment = math.floor(degrees_in_sign / (30 / 9))  # 3°20’ per segment
    navamsa_sign_index = (start_index + navamsa_segment) % 12
    return SIGNS[navamsa_sign_index]

def find_atmakaraka(positions):
    """Identify the Atmakaraka planet (highest degree in D1)."""
    max_degree = -1
    atmakaraka = None
    for planet, data in positions.items():
        if planet not in ['Rahu', 'Ketu']:  # Exclude Rahu and Ketu
            degree = data['longitude'] % 30  # Degrees within the sign
            if degree > max_degree:
                max_degree = degree
                atmakaraka = planet
    return atmakaraka

def calculate_karkamsha(positions, atmakaraka):
    """Calculate the Karkamsha sign (Navamsa sign of Atmakaraka)."""
    atmakaraka_lon = positions[atmakaraka]['longitude']
    natal_sign, degrees_in_sign = get_sign_and_degree(atmakaraka_lon)
    navamsa_sign = get_navamsa_sign(natal_sign, degrees_in_sign)
    return navamsa_sign

def calculate_navamsa_positions(positions):
    """Calculate Navamsa positions, nakshatra, pada, and retrograde status for all planets."""
    navamsa_positions = {}
    for planet, data in positions.items():
        lon = data['longitude']
        retrograde = data['retrograde']
        natal_sign, degrees_in_sign = get_sign_and_degree(lon)
        navamsa_sign = get_navamsa_sign(natal_sign, degrees_in_sign)
        nakshatra, pada = get_nakshatra_and_pada(lon)
        navamsa_positions[planet] = {
            'navamsa_sign': navamsa_sign,
            'retrograde': retrograde,
            'nakshatra': nakshatra,
            'pada': pada
        }
    return navamsa_positions

def assign_houses(navamsa_positions, karkamsha_sign):
    """Assign houses in the Karkamsha chart using whole sign house system."""
    karkamsha_index = SIGNS.index(karkamsha_sign)  # Index of Karkamsha Ascendant
    for planet, data in navamsa_positions.items():
        sign_index = SIGNS.index(data['navamsa_sign'])
        house = (sign_index - karkamsha_index) % 12 + 1  # House number (1-12)
        data['house'] = house

def lahiri_karkamsha_D9(birth_date, birth_time, latitude, longitude, tz_offset):
    """Calculate the Karkamsha chart based on birth details using Lahiri Ayanamsa."""
    # Calculate Julian Day in UT
    jd = get_julian_day(birth_date, birth_time, tz_offset)

    # Calculate sidereal positions
    positions = calculate_sidereal_positions(jd)

    # Identify Atmakaraka
    atmakaraka = find_atmakaraka(positions)

    # Calculate Navamsa positions
    navamsa_positions = calculate_navamsa_positions(positions)

    # Determine Karkamsha sign
    karkamsha_sign = calculate_karkamsha(positions, atmakaraka)

    # Assign houses
    assign_houses(navamsa_positions, karkamsha_sign)

    # Return computed data
    return {
        'atmakaraka': atmakaraka,
        'karkamsha_sign': karkamsha_sign,
        'karkamsha_chart': navamsa_positions
    }
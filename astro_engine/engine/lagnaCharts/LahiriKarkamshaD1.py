import swisseph as swe
from datetime import datetime, timedelta
import math

# Constants
SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

NAKSHATRAS = [
    ("Ashwini", 0, 13.333), ("Bharani", 13.333, 26.666), ("Krittika", 26.666, 40),
    ("Rohini", 40, 53.333), ("Mrigashira", 53.333, 66.666), ("Ardra", 66.666, 80),
    ("Punarvasu", 80, 93.333), ("Pushya", 93.333, 106.666), ("Ashlesha", 106.666, 120),
    ("Magha", 120, 133.333), ("Purva Phalguni", 133.333, 146.666), ("Uttara Phalguni", 146.666, 160),
    ("Hasta", 160, 173.333), ("Chitra", 173.333, 186.666), ("Swati", 186.666, 200),
    ("Vishakha", 200, 213.333), ("Anuradha", 213.333, 226.666), ("Jyeshta", 226.666, 240),
    ("Mula", 240, 253.333), ("Purva Ashadha", 253.333, 266.666), ("Uttara Ashadha", 266.666, 280),
    ("Shravana", 280, 293.333), ("Dhanishta", 293.333, 306.666), ("Shatabhisha", 306.666, 320),
    ("Purva Bhadrapada", 320, 333.333), ("Uttara Bhadrapada", 333.333, 346.666), ("Revati", 346.666, 360)
]

PLANETS = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mercury': swe.MERCURY, 'Venus': swe.VENUS,
    'Mars': swe.MARS, 'Jupiter': swe.JUPITER, 'Saturn': swe.SATURN,
    'Rahu': swe.MEAN_NODE, 'Ketu': swe.MEAN_NODE  # Ketu is opposite Rahu
}

ELEMENT_NAVAMSA_START = {'Fire': 'Aries', 'Earth': 'Capricorn', 'Air': 'Libra', 'Water': 'Cancer'}
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

def calculate_ascendant(jd, latitude, longitude):
    """Calculate the D1 Ascendant using Swiss Ephemeris."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)  # Lahiri Ayanamsa for sidereal
    cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b'W', flags=swe.FLG_SIDEREAL)
    asc_lon = ascmc[0] % 360
    sign, degrees = get_sign_and_degree(asc_lon)
    nakshatra, pada = get_nakshatra_and_pada(asc_lon)
    return {
        'longitude': asc_lon,
        'sign': sign,
        'degrees': degrees,
        'nakshatra': nakshatra,
        'pada': pada,
        'retrograde': False  # Ascendant doesn't have retrograde status
    }

def calculate_planetary_positions(jd):
    """Calculate sidereal longitudes, signs, degrees, retrograde status, nakshatras, and padas for planets."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)  # Lahiri Ayanamsa
    positions = {}
    for planet, code in PLANETS.items():
        if planet == 'Ketu':
            rahu_lon = positions['Rahu']['longitude']
            ketu_lon = (rahu_lon + 180) % 360
            sign, degrees = get_sign_and_degree(ketu_lon)
            nakshatra, pada = get_nakshatra_and_pada(ketu_lon)
            positions['Ketu'] = {
                'longitude': ketu_lon, 'sign': sign, 'degrees': degrees,
                'retrograde': True, 'nakshatra': nakshatra, 'pada': pada
            }
        else:
            pos = swe.calc_ut(jd, code, swe.FLG_SIDEREAL | swe.FLG_SPEED)
            lon = pos[0][0] % 360
            sign, degrees = get_sign_and_degree(lon)
            retrograde = pos[0][3] < 0 if planet not in ['Sun', 'Moon'] else False
            nakshatra, pada = get_nakshatra_and_pada(lon)
            positions[planet] = {
                'longitude': lon, 'sign': sign, 'degrees': degrees,
                'retrograde': retrograde, 'nakshatra': nakshatra, 'pada': pada
            }
    return positions

def get_sign_and_degree(longitude):
    """Determine sign and degrees within the sign from longitude."""
    sign_index = int(longitude // 30)
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
    return "Revati", 4 if longitude == 360 else ("Unknown", 0)

def get_navamsa_sign(natal_sign, degrees_in_sign):
    """Calculate the Navamsa sign for a planet or point."""
    element = SIGN_ELEMENTS[natal_sign]
    start_sign = ELEMENT_NAVAMSA_START[element]
    start_index = SIGNS.index(start_sign)
    navamsa_segment = math.floor(degrees_in_sign / (30 / 9))  # 3°20' per segment
    navamsa_sign_index = (start_index + navamsa_segment) % 12
    return SIGNS[navamsa_sign_index]

def find_atmakaraka(positions):
    """Identify the Atmakaraka planet (highest degree in D1)."""
    max_degree = -1
    atmakaraka = None
    planet_list = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']
    for planet in planet_list:
        data = positions[planet]
        degree = data['degrees']
        if degree > max_degree:
            max_degree = degree
            atmakaraka = planet
    return atmakaraka

def calculate_d1_karkamsha_ascendant(positions, atmakaraka):
    """Calculate the D1 Karkamsha Ascendant (Navamsa sign of Atmakaraka)."""
    natal_sign = positions[atmakaraka]['sign']
    degrees_in_sign = positions[atmakaraka]['degrees']
    navamsa_sign = get_navamsa_sign(natal_sign, degrees_in_sign)
    return navamsa_sign

def assign_houses_d1_karkamsha(positions, karkamsha_ascendant):
    """Assign houses in D1 Karkamsha chart using whole sign house system."""
    karkamsha_index = SIGNS.index(karkamsha_ascendant)
    for planet, data in positions.items():
        sign_index = SIGNS.index(data['sign'])
        house = (sign_index - karkamsha_index) % 12 + 1
        data['house'] = house

def lahiri_karkamsha_d1(birth_date, birth_time, latitude, longitude, tz_offset):
    """Calculate the D1 Karkamsha chart based on birth details."""
    # Step 1: Convert to Julian Day
    jd = get_julian_day(birth_date, birth_time, tz_offset)

    # Step 2: Calculate D1 Ascendant
    ascendant = calculate_ascendant(jd, latitude, longitude)

    # Step 3: Calculate D1 planetary positions
    positions = calculate_planetary_positions(jd)

    # Step 4: Include Ascendant in positions dictionary
    positions['Ascendant'] = ascendant

    # Step 5: Identify Atmakaraka
    atmakaraka = find_atmakaraka(positions)
    if not atmakaraka:
        raise ValueError("Unable to determine Atmakaraka")

    # Step 6: Calculate D1 Karkamsha Ascendant (Navamsa sign of Atmakaraka)
    karkamsha_ascendant = calculate_d1_karkamsha_ascendant(positions, atmakaraka)

    # Step 7: Assign houses in D1 Karkamsha chart
    assign_houses_d1_karkamsha(positions, karkamsha_ascendant)

    # Return computed data
    return {
        'd1_ascendant': {
            'sign': ascendant['sign'],
            'degrees': ascendant['degrees'],
            'nakshatra': ascendant['nakshatra'],
            'pada': ascendant['pada']
        },
        'atmakaraka': atmakaraka,
        'karkamsha_ascendant': karkamsha_ascendant,
        'd1_karkamsha_chart': positions
    }
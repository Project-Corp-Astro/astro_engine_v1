import swisseph as swe
from datetime import datetime, timedelta
import math

# Constants
SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

ODD_SIGN_D30_RANGES = [
    (0, 5, 'Aries'),
    (5, 10, 'Aquarius'),
    (10, 18, 'Sagittarius'),
    (18, 25, 'Gemini'),
    (25, 30, 'Libra')
]

EVEN_SIGN_D30_RANGES = [
    (0, 5, 'Taurus'),
    (5, 12, 'Virgo'),
    (12, 20, 'Pisces'),
    (20, 25, 'Capricorn'),
    (25, 30, 'Scorpio')
]

NAKSHATRAS = [
    ("Ashwini", 0),
    ("Bharani", 13.333),
    ("Krittika", 26.666),
    ("Rohini", 40),
    ("Mrigashira", 53.333),
    ("Ardra", 66.666),
    ("Punarvasu", 80),
    ("Pushya", 93.333),
    ("Ashlesha", 106.666),
    ("Magha", 120),
    ("Purva Phalguni", 133.333),
    ("Uttara Phalguni", 146.666),
    ("Hasta", 160),
    ("Chitra", 173.333),
    ("Swati", 186.666),
    ("Vishakha", 200),
    ("Anuradha", 213.333),
    ("Jyeshta", 226.666),
    ("Mula", 240),
    ("Purva Ashadha", 253.333),
    ("Uttara Ashadha", 266.666),
    ("Shravana", 280),
    ("Dhanishta", 293.333),
    ("Shatabhisha", 306.666),
    ("Purva Bhadrapada", 320),
    ("Uttara Bhadrapada", 333.333),
    ("Revati", 346.666)
]

PLANETS = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mercury': swe.MERCURY, 'Venus': swe.VENUS,
    'Mars': swe.MARS, 'Jupiter': swe.JUPITER, 'Saturn': swe.SATURN,
    'Rahu': swe.MEAN_NODE, 'Ketu': None
}

def get_julian_day(date_str, time_str, tz_offset):
    """Convert local birth date and time to Julian Day in UT."""
    local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    ut_dt = local_dt - timedelta(hours=tz_offset)
    hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
    return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal, swe.GREG_CAL)

def calculate_sidereal_longitudes(jd, latitude, longitude):
    """Calculate sidereal longitudes using Lahiri Ayanamsa."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    positions = {}
    for planet, code in PLANETS.items():
        if planet == 'Ketu':
            rahu_lon = positions['Rahu']['longitude']
            positions['Ketu'] = {'longitude': (rahu_lon + 180) % 360}
        else:
            pos = swe.calc_ut(jd, code, swe.FLG_SIDEREAL)
            positions[planet] = {'longitude': pos[0][0] % 360}
    cusps, ascmc = swe.houses_ex(jd, float(latitude), float(longitude), b'W', flags=swe.FLG_SIDEREAL)
    positions['Ascendant'] = {'longitude': ascmc[0] % 360}
    return positions

def get_d30_sign_and_degree(longitude):
    """Map sidereal longitude to D30 sign and degree."""
    sign_index = int(longitude // 30)
    degree_in_sign = longitude % 30
    natal_sign = SIGNS[sign_index]
    is_odd = sign_index % 2 == 0
    ranges = ODD_SIGN_D30_RANGES if is_odd else EVEN_SIGN_D30_RANGES
    for start, end, sign in ranges:
        if start <= degree_in_sign < end:
            range_length = end - start
            position_in_range = (degree_in_sign - start) / range_length
            d30_degree = position_in_range * 30
            return sign, d30_degree, natal_sign, degree_in_sign
    start, end, sign = ranges[-1]
    d30_degree = ((degree_in_sign - start) / (end - start)) * 30
    return sign, d30_degree, natal_sign, degree_in_sign

def assign_houses(d30_positions, ascendant_sign):
    """Assign houses using Whole Sign system."""
    ascendant_index = SIGNS.index(ascendant_sign)
    for planet, data in d30_positions.items():
        sign_index = SIGNS.index(data['sign'])
        house = (sign_index - ascendant_index) % 12 + 1
        data['house'] = house

def format_degree(deg):
    """Format degrees as degrees, minutes, seconds."""
    d = int(deg)
    m = int((deg - d) * 60)
    s = (deg - d - m / 60) * 3600
    return f"{d}° {m}' {s:.2f}\""

def get_sign_and_degree(longitude):
    """Determine sign and degrees within the sign from longitude."""
    sign_index = int(longitude // 30)
    degree_in_sign = longitude % 30
    sign = SIGNS[sign_index]
    return sign, degree_in_sign

def get_nakshatra_and_pada(longitude):
    """Determine nakshatra and pada from longitude."""
    longitude = longitude % 360
    for i, (name, start) in enumerate(NAKSHATRAS):
        end = start + 13.333 if i < 26 else 360
        if start <= longitude < end:
            offset = longitude - start
            pada = math.ceil(offset / (13.333 / 4))
            return name, pada
    return "Unknown", 0

def calculate_natal_positions(jd, latitude, longitude):
    """Calculate natal positions with additional details."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    positions = {}
    for planet, code in PLANETS.items():
        if planet == 'Ketu':
            rahu_lon = positions['Rahu']['longitude']
            ketu_lon = (rahu_lon + 180) % 360
            retrograde = True
            sign, degree = get_sign_and_degree(ketu_lon)
            nakshatra, pada = get_nakshatra_and_pada(ketu_lon)
            positions['Ketu'] = {
                'longitude': ketu_lon,
                'retrograde': retrograde,
                'sign': sign,
                'degree': degree,
                'nakshatra': nakshatra,
                'pada': pada
            }
        else:
            pos = swe.calc_ut(jd, code, swe.FLG_SIDEREAL | swe.FLG_SPEED)
            lon = pos[0][0] % 360
            speed = pos[0][3]
            retrograde = speed < 0 if planet not in ['Sun', 'Moon'] else False
            sign, degree = get_sign_and_degree(lon)
            nakshatra, pada = get_nakshatra_and_pada(lon)
            positions[planet] = {
                'longitude': lon,
                'retrograde': retrograde,
                'sign': sign,
                'degree': degree,
                'nakshatra': nakshatra,
                'pada': pada
            }
    cusps, ascmc = swe.houses_ex(jd, float(latitude), float(longitude), b'W', flags=swe.FLG_SIDEREAL)
    asc_lon = ascmc[0] % 360
    sign, degree = get_sign_and_degree(asc_lon)
    nakshatra, pada = get_nakshatra_and_pada(asc_lon)
    positions['Ascendant'] = {
        'longitude': asc_lon,
        'sign': sign,
        'degree': degree,
        'nakshatra': nakshatra,
        'pada': pada
    }
    return positions

def lahiri_trimshamsha_D30(birth_date, birth_time, latitude, longitude, tz_offset):
    """Calculate D30 chart with natal details including pada, stars, and retrograde."""
    jd = get_julian_day(birth_date, birth_time, tz_offset)
    natal_positions = calculate_natal_positions(jd, latitude, longitude)
    d30_positions = {}
    for planet, data in natal_positions.items():
        longitude = data['longitude']
        sign, degree, natal_sign, natal_deg = get_d30_sign_and_degree(longitude)
        d30_positions[planet] = {
            'sign': sign,
            'degree': format_degree(degree),
            # 'natal_sign': natal_sign,
            # 'natal_degree': format_degree(natal_deg),
            # 'natal_longitude': round(longitude, 4),
            'retrograde': data.get('retrograde', None),
            'nakshatra': data['nakshatra'],
            'pada': data['pada']
        }
    ascendant_sign = d30_positions['Ascendant']['sign']
    assign_houses(d30_positions, ascendant_sign)
    return natal_positions, d30_positions
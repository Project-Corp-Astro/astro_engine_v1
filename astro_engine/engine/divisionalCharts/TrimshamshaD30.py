import swisseph as swe
from datetime import datetime, timedelta

# Zodiac signs
SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

# D30 mapping ranges for odd signs
ODD_SIGN_D30_RANGES = [
    (0, 5, 'Aries'),
    (5, 10, 'Aquarius'),
    (10, 18, 'Sagittarius'),
    (18, 25, 'Gemini'),
    (25, 30, 'Libra')
]

# D30 mapping ranges for even signs
EVEN_SIGN_D30_RANGES = [
    (0, 5, 'Taurus'),
    (5, 12, 'Virgo'),
    (12, 20, 'Pisces'),
    (20, 25, 'Capricorn'),
    (25, 30, 'Scorpio')
]

# Nakshatras with start degrees (each spans 13°20')
NAKSHATRAS = [
    ("Ashwini", 0.0),
    ("Bharani", 13.333333333333334),
    ("Krittika", 26.666666666666668),
    ("Rohini", 40.0),
    ("Mrigashira", 53.333333333333336),
    ("Ardra", 66.66666666666667),
    ("Punarvasu", 80.0),
    ("Pushya", 93.33333333333333),
    ("Ashlesha", 106.66666666666667),
    ("Magha", 120.0),
    ("Purva Phalguni", 133.33333333333334),
    ("Uttara Phalguni", 146.66666666666666),
    ("Hasta", 160.0),
    ("Chitra", 173.33333333333334),
    ("Swati", 186.66666666666666),
    ("Vishakha", 200.0),
    ("Anuradha", 213.33333333333334),
    ("Jyeshta", 226.66666666666666),
    ("Mula", 240.0),
    ("Purva Ashadha", 253.33333333333334),
    ("Uttara Ashadha", 266.6666666666667),
    ("Shravana", 280.0),
    ("Dhanishta", 293.3333333333333),
    ("Shatabhisha", 306.6666666666667),
    ("Purva Bhadrapada", 320.0),
    ("Uttara Bhadrapada", 333.3333333333333),
    ("Revati", 346.6666666666667)
]

def get_julian_day_d30(date_str, time_str, tz_offset):
    """Convert local birth date and time to Julian Day in UT."""
    local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    ut_dt = local_dt - timedelta(hours=tz_offset)
    hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
    return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal, swe.GREG_CAL)

def calculate_sidereal_longitudes_d30(jd, latitude, longitude):
    """Calculate sidereal longitudes using Lahiri Ayanamsa."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    planets = {
        'Sun': swe.SUN, 'Moon': swe.MOON, 'Mercury': swe.MERCURY, 'Venus': swe.VENUS,
        'Mars': swe.MARS, 'Jupiter': swe.JUPITER, 'Saturn': swe.SATURN,
        'Rahu': swe.MEAN_NODE, 'Ketu': None
    }
    positions = {}
    for planet, code in planets.items():
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

def assign_houses_d30(d30_positions, ascendant_sign):
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

def get_nakshatra_and_pada(longitude):
    """Determine nakshatra and pada for a given longitude."""
    for nakshatra, start in NAKSHATRAS:
        if start <= longitude < start + 13.333333333333334:
            offset = longitude - start
            pada = int(offset / 3.3333333333333335) + 1  # Each pada is 3°20'
            return nakshatra, pada
    # Handle edge case near 360°
    offset = (longitude - 346.6666666666667) % 360
    pada = int(offset / 3.3333333333333335) + 1
    return "Revati", pada

def lahiri_trimshamsha_d30(natal_positions):
    """Calculate the Lahiri Trimshamsha (D30) chart with retrograde, stars, and pada."""
    d30_positions = {}
    for planet, data in natal_positions.items():
        longitude = data['longitude']
        sign, degree, natal_sign, natal_deg = get_d30_sign_and_degree(longitude)
        nakshatra, pada = get_nakshatra_and_pada(longitude)
        # Retrograde status (assuming speed isn't available in original data, default to False)
        retrograde = data.get('speed', 0) < 0 if 'speed' in data else False
        d30_positions[planet] = {
            'sign': sign,
            'degree': format_degree(degree),
            'natal_sign': natal_sign,
            'natal_degree': format_degree(natal_deg),
            'natal_longitude': round(longitude, 4),
            'retrograde': retrograde,
            'nakshatra': nakshatra,
            'pada': pada
        }
    return d30_positions
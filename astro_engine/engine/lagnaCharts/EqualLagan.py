# import swisseph as swe
# from datetime import datetime, timedelta

# # Zodiac signs for reference
# SIGNS = [
#     "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
#     "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
# ]

# def bava_get_julian_day(date_str, time_str, tz_offset):
#     """Convert birth date and time to Julian Day (UT)."""
#     try:
#         date_obj = datetime.strptime(date_str, '%Y-%m-%d')
#         time_obj = datetime.strptime(time_str, '%H:%M:%S')
#         local_dt = datetime.combine(date_obj, time_obj.time())
#         ut_dt = local_dt - timedelta(hours=tz_offset)
#         hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
#         return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal)
#     except ValueError as e:
#         raise ValueError(f"Invalid date or time format: {str(e)}")

# def bava_calculate_ascendant(jd, latitude, longitude):
#     """Calculate the sidereal ascendant longitude using Lahiri Ayanamsa."""
#     try:
#         swe.set_sid_mode(swe.SIDM_LAHIRI)  # Set Lahiri Ayanamsa
#         cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b'P', flags=swe.FLG_SIDEREAL)
#         ascendant = ascmc[0] % 360.0  # Ascendant longitude in degrees
#         return ascendant
#     except Exception as e:
#         raise Exception(f"Ascendant calculation failed: {str(e)}")

# def bava_get_planet_positions(jd):
#     """Calculate sidereal positions and retrograde status of planets."""
#     try:
#         planets = {
#             'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS, 'Mercury': swe.MERCURY,
#             'Jupiter': swe.JUPITER, 'Venus': swe.VENUS, 'Saturn': swe.SATURN,
#             'Rahu': swe.MEAN_NODE, 'Ketu': None  # Ketu will be calculated as 180° opposite Rahu
#         }
#         positions = {}
#         for planet, pid in planets.items():
#             if planet == 'Ketu':
#                 continue
#             pos, ret = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL)
#             if ret < 0:
#                 raise ValueError(f"Error calculating position for {planet}")
#             longitude = pos[0] % 360.0
#             # Determine retrograde status
#             # Sun and Moon are never retrograde
#             # Rahu and Ketu are always retrograde in Vedic astrology
#             # For others, check speed (negative speed = retrograde)
#             if planet in ['Sun', 'Moon']:
#                 retrograde = False
#             elif planet == 'Rahu':
#                 retrograde = True
#             else:
#                 retrograde = pos[3] < 0  # Speed component (index 3) negative means retrograde
#             positions[planet] = (longitude, retrograde)
#         # Calculate Ketu (180° opposite Rahu)
#         rahu_lon = positions['Rahu'][0]
#         ketu_lon = (rahu_lon + 180.0) % 360.0
#         positions['Ketu'] = (ketu_lon, True)  # Ketu is always retrograde
#         return positions
#     except Exception as e:
#         raise Exception(f"Planetary calculation failed: {str(e)}")

# def bava_calculate_equal_bhava_cusps(ascendant):
#     """Calculate the midpoints (cusps) of all 12 houses, each spanning 30 degrees."""
#     cusps = [(ascendant + (n - 1) * 30) % 360 for n in range(1, 13)]
#     return cusps

# def bava_assign_planets_to_houses(planetary_positions, ascendant_sign_index):
#     """Assign planets to houses using Whole Sign system based on Equal Bhava Lagna."""
#     house_assignments = {}
#     for planet, (longitude, _) in planetary_positions.items():
#         planet_sign_index = int(longitude // 30)
#         house = (planet_sign_index - ascendant_sign_index) % 12 + 1
#         house_assignments[planet] = house
#     return house_assignments

# def bava_format_dms(degrees):
#     """Format degrees into degrees, minutes, and seconds."""
#     degrees = degrees % 360.0
#     d = int(degrees)
#     m = int((degrees - d) * 60)
#     s = int(((degrees - d) * 60 - m) * 60)
#     return f"{d}° {m}' {s}\""





import swisseph as swe
from datetime import datetime, timedelta
import math

# Zodiac signs for reference
SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

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

def get_julian_day(date_str, time_str, tz_offset):
    """Convert birth date and time to Julian Day (UT)."""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        time_obj = datetime.strptime(time_str, '%H:%M:%S')
        local_dt = datetime.combine(date_obj, time_obj.time())
        ut_dt = local_dt - timedelta(hours=tz_offset)
        hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
        return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal)
    except ValueError as e:
        raise ValueError(f"Invalid date or time format: {str(e)}")

def calculate_ascendant(jd, latitude, longitude):
    """Calculate the sidereal ascendant longitude using Lahiri Ayanamsa."""
    try:
        swe.set_sid_mode(swe.SIDM_LAHIRI)  # Set Lahiri Ayanamsa
        cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b'P', flags=swe.FLG_SIDEREAL)
        ascendant = ascmc[0] % 360.0  # Ascendant longitude in degrees
        return ascendant
    except Exception as e:
        raise Exception(f"Ascendant calculation failed: {str(e)}")

def get_planet_positions(jd):
    """Calculate sidereal positions and retrograde status of planets."""
    try:
        planets = {
            'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS, 'Mercury': swe.MERCURY,
            'Jupiter': swe.JUPITER, 'Venus': swe.VENUS, 'Saturn': swe.SATURN,
            'Rahu': swe.MEAN_NODE, 'Ketu': None  # Ketu will be calculated as 180° opposite Rahu
        }
        positions = {}
        for planet, pid in planets.items():
            if planet == 'Ketu':
                continue
            pos, ret = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL)
            if ret < 0:
                raise ValueError(f"Error calculating position for {planet}")
            longitude = pos[0] % 360.0
            # Determine retrograde status
            # Sun and Moon are never retrograde
            # Rahu and Ketu are always retrograde in Vedic astrology
            # For others, check speed (negative speed = retrograde)
            if planet in ['Sun', 'Moon']:
                retrograde = False
            elif planet == 'Rahu':
                retrograde = True
            else:
                retrograde = pos[3] < 0  # Speed component (index 3) negative means retrograde
            positions[planet] = (longitude, retrograde)
        # Calculate Ketu (180° opposite Rahu)
        rahu_lon = positions['Rahu'][0]
        ketu_lon = (rahu_lon + 180.0) % 360.0
        positions['Ketu'] = (ketu_lon, True)  # Ketu is always retrograde
        return positions
    except Exception as e:
        raise Exception(f"Planetary calculation failed: {str(e)}")

def calculate_equal_bhava_cusps(ascendant):
    """Calculate the midpoints (cusps) of all 12 houses, each spanning 30 degrees."""
    cusps = [(ascendant + (n - 1) * 30) % 360 for n in range(1, 13)]
    return cusps

def assign_planets_to_houses(planetary_positions, ascendant_sign_index):
    """Assign planets to houses using Whole Sign system based on Equal Bhava Lagna."""
    house_assignments = {}
    for planet, (longitude, _) in planetary_positions.items():
        planet_sign_index = int(longitude // 30)
        house = (planet_sign_index - ascendant_sign_index) % 12 + 1
        house_assignments[planet] = house
    return house_assignments

def format_dms(degrees):
    """Format degrees into degrees, minutes, and seconds."""
    degrees = degrees % 360.0
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = int(((degrees - d) * 60 - m) * 60)
    return f"{d}° {m}' {s}\""

def get_nakshatra_and_pada(longitude):
    """Calculate nakshatra and pada based on longitude."""
    longitude = longitude % 360
    for nakshatra, start, end in NAKSHATRAS:
        if start <= longitude < end:
            position_in_nakshatra = longitude - start
            pada = math.ceil(position_in_nakshatra / 3.3333)
            return nakshatra, pada
    # Fallback for edge case at 360 degrees
    return 'Revati', 4

def lahairi_equal_bava(birth_date, birth_time, latitude, longitude, tz_offset):
    """Calculate Equal Bhava Lagna, house cusps, and planetary positions with retrograde, nakshatras, and padas."""
    # Calculate Julian Day (UT)
    jd = get_julian_day(birth_date, birth_time, tz_offset)

    # Calculate sidereal ascendant
    ascendant = calculate_ascendant(jd, latitude, longitude)
    ascendant_sign_index = int(ascendant // 30)

    # Calculate planetary positions with retrograde status
    planetary_positions = get_planet_positions(jd)

    # Calculate equal bhava house cusps
    cusps_degrees = calculate_equal_bhava_cusps(ascendant)
    cusps_formatted = [format_dms(cusp) for cusp in cusps_degrees]

    # Assign planets to houses
    house_assignments = assign_planets_to_houses(planetary_positions, ascendant_sign_index)

    # Prepare house data with nakshatras and padas
    house_data = [
        {
            "house": i + 1,
            "cusp": cusps_formatted[i],
            "sign": SIGNS[int(cusps_degrees[i] // 30)],
            "nakshatra": get_nakshatra_and_pada(cusps_degrees[i])[0],
            "pada": get_nakshatra_and_pada(cusps_degrees[i])[1]
        }
        for i in range(12)
    ]

    # Prepare planetary positions data with nakshatras and padas
    planetary_data = [
        {
            "planet": planet,
            "longitude": format_dms(longitude),
            "sign": SIGNS[int(longitude // 30)],
            "retrograde": retrograde,
            "house": house_assignments[planet],
            "nakshatra": get_nakshatra_and_pada(longitude)[0],
            "pada": get_nakshatra_and_pada(longitude)[1]
        }
        for planet, (longitude, retrograde) in planetary_positions.items()
    ]

    # Prepare JSON response
    response = {
        "ascendant": {
            "longitude": format_dms(ascendant),
            "sign": SIGNS[ascendant_sign_index]
        },
        "planetary_positions": planetary_data,
        "house_cusps": house_data,
        "metadata": {
            "ayanamsa": "Lahiri",
            "house_system": "Equal Bhava (Whole Sign based)",
            "calculation_time": datetime.utcnow().isoformat(),
            "input": {
                "birth_date": birth_date,
                "birth_time": birth_time,
                "latitude": latitude,
                "longitude": longitude,
                "timezone_offset": tz_offset
            }
        }
    }
    return response
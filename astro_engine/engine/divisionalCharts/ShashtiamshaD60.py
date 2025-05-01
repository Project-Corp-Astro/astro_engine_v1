import swisseph as swe
from datetime import datetime, timedelta
import math

# Zodiac signs (0-based index: Aries=0, Taurus=1, ..., Pisces=11)
SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

# Shashtiamsha deities list (1 to 60, as per Brihat Parashara Hora Shastra)
SHASHTIAMSHA_DEITIES = [
    "Ghora", "Rakshasa", "Deva", "Kubera", "Yaksha", "Kinnara", "Bhrashta", "Kulagna",
    "Garala", "Vahni", "Maya", "Purishaka", "Apampathi", "Marut", "Kala", "Sarpa",
    "Amrita", "Indu", "Mridu", "Komal", "Heramba", "Brahma", "Vishnu", "Maheshwara",
    "Deva", "Ardra", "Kala", "Kshiti", "Kamalakara", "Gulika", "Mrityu", "Kaala",
    "Davagni", "Ghora", "Yama", "Kantaka", "Sudha", "Amrita", "Purnachandra", "Vishadagdha",
    "Kulanashta", "Vamsakshaya", "Utpata", "Kala", "Saumya", "Komala", "Sheetala", "Karaladamshtra",
    "Chandramukhi", "Praveena", "Kalapavaka", "Dandayudha", "Nirmala", "Saumya", "Kroora", "Atisheetala",
    "Amrita", "Payodhi", "Brahmana", "Indu Rekha"
]

def get_julian_day(date_str, time_str, tz_offset):
    """
    Convert birth date, time, and timezone offset to Julian Day (UT).
    
    Args:
        date_str (str): Birth date in 'YYYY-MM-DD' format.
        time_str (str): Birth time in 'HH:MM:SS' format.
        tz_offset (float): Timezone offset in hours (e.g., 5.5 for IST).
    
    Returns:
        float: Julian Day in Universal Time.
    """
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    time_obj = datetime.strptime(time_str, '%H:%M:%S')
    local_dt = datetime.combine(date_obj, time_obj.time())
    ut_dt = local_dt - timedelta(hours=tz_offset)
    hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
    return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal)

def get_sidereal_longitude(jd_ut, planet_id, ascendant=False):
    """
    Calculate sidereal longitude for a planet or ascendant using Lahiri Ayanamsa.
    
    Args:
        jd_ut (float): Julian Day in UT.
        planet_id (int): Swiss Ephemeris planet ID (e.g., swe.SUN) or None for ascendant.
        ascendant (bool): True if calculating for ascendant, False for planets.
    
    Returns:
        tuple: (longitude, retrograde flag) where longitude is 0-360° and retrograde is 'R' or ''.
    """
    swe.set_sid_mode(swe.SIDM_LAHIRI)  # Set Lahiri Ayanamsa
    flag = swe.FLG_SIDEREAL | swe.FLG_SPEED
    
    if ascendant:
        # Placeholder for ascendant longitude (will be calculated separately)
        return None, ''
    else:
        pos, _ = swe.calc_ut(jd_ut, planet_id, flag)
        longitude = pos[0] % 360
        retrograde = 'R' if pos[3] < 0 else ''
        return longitude, retrograde

def get_d60_position(sidereal_lon):
    """
    Calculate D60 sign and Shashtiamsha number from sidereal longitude.
    
    Args:
        sidereal_lon (float): Sidereal longitude in degrees (0-360°).
    
    Returns:
        dict: D60 sign, sign index, Shashtiamsha number, and deity.
    """
    # Step 1: Extract natal sign and degrees within it
    natal_sign_index = int(sidereal_lon // 30)  # 0-11 (Aries to Pisces)
    natal_degrees = sidereal_lon % 30  # Degrees within the sign (0° to 29.999°)

    # Step 2: Calculate D60 sign
    y = natal_degrees * 2
    remainder = y % 12
    count = math.floor(remainder) + 1  # Count starts from 1
    d60_sign_index = (natal_sign_index + count - 1) % 12  # Adjust for 0-based index

    # Step 3: Calculate Shashtiamsha number
    shashtiamsha_number = math.floor(natal_degrees / 0.5) + 1  # Each segment is 0.5°
    if shashtiamsha_number > 60:
        shashtiamsha_number = 60  # Cap at 60
    
    # Step 4: Map to deity
    deity = SHASHTIAMSHA_DEITIES[shashtiamsha_number - 1]  # -1 for 0-based list index

    return {
        "sign": SIGNS[d60_sign_index],
        "sign_index": d60_sign_index,
        "shashtiamsha": shashtiamsha_number,
        "deity": deity,
        "longitude": sidereal_lon  # Retain for house calculation
    }

def get_d60_house(d60_sign_index, d60_asc_sign_index):
    """
    Assign house number using Whole Sign system.
    
    Args:
        d60_sign_index (int): D60 sign index of the planet (0-11).
        d60_asc_sign_index (int): D60 ascendant sign index (0-11).
    
    Returns:
        int: House number (1-12).
    """
    return (d60_sign_index - d60_asc_sign_index) % 12 + 1

def format_dms(degrees):
    """
    Format longitude in degrees, minutes, seconds (e.g., 17°41'36").
    
    Args:
        degrees (float): Longitude in decimal degrees.
    
    Returns:
        str: Formatted string in D°M'S" format.
    """
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = (degrees - d - m / 60) * 3600
    return f"{d}°{m}'{s:.1f}\""

def calculate_d60_chart(jd_ut, latitude, longitude):
    """
    Calculate the D60 (Shashtiamsha) chart based on birth details.
    
    Args:
        jd_ut (float): Julian Day in UT.
        latitude (float): Latitude of birth place.
        longitude (float): Longitude of birth place.
    
    Returns:
        dict: D60 chart data including ascendant, planetary positions, and house signs.
    """
    # Calculate sidereal longitudes for planets
    planets = [
        (swe.SUN, 'Sun'), (swe.MOON, 'Moon'), (swe.MARS, 'Mars'),
        (swe.MERCURY, 'Mercury'), (swe.JUPITER, 'Jupiter'), (swe.VENUS, 'Venus'),
        (swe.SATURN, 'Saturn'), (swe.TRUE_NODE, 'Rahu')
    ]
    d1_positions = {}
    for planet_id, name in planets:
        lon, retro = get_sidereal_longitude(jd_ut, planet_id)
        d1_positions[name] = (lon, retro)

    # Calculate Ketu
    rahu_lon = d1_positions['Rahu'][0]
    ketu_lon = (rahu_lon + 180) % 360
    d1_positions['Ketu'] = (ketu_lon, '')

    # Calculate ascendant sidereal longitude
    cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b'W', flags=swe.FLG_SIDEREAL)
    d1_asc_lon = ascmc[0] % 360

    # Calculate D60 ascendant
    d60_asc = get_d60_position(d1_asc_lon)
    d60_asc_sign_index = d60_asc['sign_index']

    # Calculate D60 positions for all planets
    d60_positions = {}
    for planet, (d1_lon, retro) in d1_positions.items():
        d60_pos = get_d60_position(d1_lon)
        house = get_d60_house(d60_pos['sign_index'], d60_asc_sign_index)
        d60_positions[planet] = {
            "sign": d60_pos['sign'],
            "shashtiamsha": d60_pos['shashtiamsha'],
            "deity": d60_pos['deity'],
            "house": house,
            "retrograde": retro,
            "longitude": format_dms(d1_lon)  # Formatted for readability
        }

    # Assign house signs using Whole Sign system
    house_signs = [
        {"house": i + 1, "sign": SIGNS[(d60_asc_sign_index + i) % 12]} 
        for i in range(12)
    ]

    return {
        "d60_ascendant": {
            "sign": d60_asc['sign'],
            "shashtiamsha": d60_asc['shashtiamsha'],
            "deity": d60_asc['deity'],
            "longitude": format_dms(d1_asc_lon)
        },
        "planetary_positions": d60_positions,
        "house_signs": house_signs
    }
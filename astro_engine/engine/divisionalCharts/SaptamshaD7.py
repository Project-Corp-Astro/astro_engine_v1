# calculations.py
import swisseph as swe
from datetime import datetime, timedelta
import math
import logging

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Constants
PLANET_NAMES = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

def get_julian_day(date_str, time_str, tz_offset):
    """Convert local birth date and time to Julian Day (UTC)."""
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    dt_utc = dt - timedelta(hours=tz_offset)
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600)
    logger.debug(f"Julian Day: {jd:.6f}")
    return jd

def calculate_sidereal_position(jd, planet_id, ayanamsa):
    """Calculate sidereal longitude of a planet."""
    pos, _ = swe.calc_ut(jd, planet_id, swe.FLG_SWIEPH | swe.FLG_SPEED)
    sidereal_lon = (pos[0] - ayanamsa) % 360
    return sidereal_lon

def calculate_ascendant(jd, lat, lon):
    """Calculate sidereal Ascendant longitude using Whole Sign system."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    houses, ascmc = swe.houses_ex(jd, lat, lon, b'W', flags=swe.FLG_SIDEREAL)
    asc_lon = ascmc[0] % 360
    logger.debug(f"Sidereal Ascendant Longitude: {asc_lon:.6f}")
    return asc_lon

def get_sign_and_degrees(longitude):
    """Extract sign and degrees within the sign from longitude."""
    sign_index = int(longitude // 30)
    degrees = longitude % 30
    sign = SIGNS[sign_index]
    return sign, degrees

def calculate_d7_sign(longitude, natal_sign):
    """Calculate D7 (Saptamsa) sign based on natal longitude and sign."""
    # Determine if the natal sign is odd or even
    is_odd = SIGNS.index(natal_sign) % 2 == 0
    if is_odd:
        start_sign = natal_sign
    else:
        start_sign = SIGNS[(SIGNS.index(natal_sign) + 6) % 12]  # 7th sign from natal sign
    
    # Calculate Saptamsa number (each segment is 30° / 7 ≈ 4.2857142857°)
    degrees = longitude % 30
    saptamsa_number = math.ceil(degrees / (30 / 7))
    
    # Calculate D7 sign by counting from the starting sign
    d7_sign_index = (SIGNS.index(start_sign) + saptamsa_number - 1) % 12
    d7_sign = SIGNS[d7_sign_index]
    return d7_sign

def calculate_d7_house(d7_sign, d7_asc_sign):
    """Calculate house number using Whole Sign system with D7 Ascendant."""
    d7_sign_index = SIGNS.index(d7_sign)
    d7_asc_index = SIGNS.index(d7_asc_sign)
    house = (d7_sign_index - d7_asc_index + 12) % 12 + 1
    return house

def calculate_d7_chart(jd, lat, lon):
    """Calculate D7 chart data with precise planetary positions."""
    # Set sidereal mode to Lahiri Ayanamsa
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa = swe.get_ayanamsa_ut(jd)
    logger.debug(f"Lahiri Ayanamsa: {ayanamsa:.6f}")

    # Calculate natal Ascendant and its D7 position
    asc_lon = calculate_ascendant(jd, lat, lon)
    natal_asc_sign, asc_degrees = get_sign_and_degrees(asc_lon)
    d7_asc_sign = calculate_d7_sign(asc_lon, natal_asc_sign)

    # Calculate planetary positions in D7 chart
    planets = {}
    for planet_name in PLANET_NAMES:
        if planet_name == 'Rahu':
            planet_id = swe.MEAN_NODE
        elif planet_name == 'Ketu':
            planet_id = swe.MEAN_NODE
        else:
            planet_id = getattr(swe, planet_name.upper())
        
        # Calculate sidereal longitude
        lon = calculate_sidereal_position(jd, planet_id, ayanamsa)
        if planet_name == 'Ketu':
            lon = (lon + 180) % 360  # Ketu is 180° opposite Rahu
        
        # Determine natal and D7 positions
        natal_sign, degrees = get_sign_and_degrees(lon)
        d7_sign = calculate_d7_sign(lon, natal_sign)
        house = calculate_d7_house(d7_sign, d7_asc_sign)
        
        planets[planet_name] = {
            "natal_sign": natal_sign,
            "degrees": round(degrees, 6),
            "d7_sign": d7_sign,
            "house": house
        }

    # Add Ascendant to the chart
    planets['Ascendant'] = {
        "natal_sign": natal_asc_sign,
        "degrees": round(asc_degrees, 6),
        "d7_sign": d7_asc_sign,
        "house": 1
    }

    return planets
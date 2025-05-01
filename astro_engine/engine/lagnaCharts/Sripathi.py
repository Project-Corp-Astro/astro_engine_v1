# calculations.py
import swisseph as swe
from datetime import datetime, timedelta
import math
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
PLANET_IDS = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS, 'Mercury': swe.MERCURY,
    'Jupiter': swe.JUPITER, 'Venus': swe.VENUS, 'Saturn': swe.SATURN,
    'Rahu': swe.MEAN_NODE, 'Ketu': None  # Ketu calculated separately
}

def get_julian_day(date_str, time_str, tz_offset):
    """Convert local birth date and time to Julian Day in UT."""
    dt = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M:%S')
    ut_dt = dt - timedelta(hours=tz_offset)
    jd = swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, ut_dt.hour + ut_dt.minute / 60.0 + ut_dt.second / 3600.0)
    logger.debug(f"Julian Day: {jd} for UT: {ut_dt}")
    return jd

def calculate_ascendant(jd, lat, lon):
    """Calculate the ascendant longitude and house cusps using Sripathi Bhava system."""
    cusps, ascmc = swe.houses_ex(jd, lat, lon, b'S', flags=swe.FLG_SIDEREAL)  # 'S' for Sripati
    asc_lon = ascmc[0] % 360  # Ascendant longitude
    asc_sign_index = math.floor(asc_lon / 30)
    logger.debug(f"Ascendant Longitude: {asc_lon}, Sign Index: {asc_sign_index}, Cusps: {cusps}")
    return asc_lon, asc_sign_index, cusps

def calculate_house(planet_lon, cusps):
    """Determine house number using Sripathi Bhava cusps."""
    planet_lon = planet_lon % 360
    for i in range(12):
        cusp_start = cusps[i] % 360
        cusp_end = cusps[(i + 1) % 12] % 360
        if cusp_start < cusp_end:
            if cusp_start <= planet_lon < cusp_end:
                return i + 1
        else:  # Handle wrap-around at 360°
            if planet_lon >= cusp_start or planet_lon < cusp_end:
                return i + 1
    return 12  # Default to House 12 if not found

def get_planet_data(jd, asc_lon, cusps):
    """Calculate planetary positions, signs, degrees, retrograde status, and houses."""
    natal_positions = {}
    for planet, pid in PLANET_IDS.items():
        if planet == 'Ketu':
            continue
        pos_data, _ = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL | swe.FLG_SPEED)
        lon = pos_data[0] % 360
        retrograde = 'R' if pos_data[3] < 0 else ''
        sign_index = math.floor(lon / 30)
        sign = SIGNS[sign_index]
        degrees = lon % 30
        house = calculate_house(lon, cusps)
        natal_positions[planet] = {
            "sign": sign,
            "degrees": round(degrees, 4),
            "house": house,
            "retrograde": retrograde
        }
        logger.debug(f"{planet}: Lon={lon}, Sign={sign}, Degrees={degrees}, House={house}, Retro={retrograde}")
    
    # Calculate Ketu (180° opposite Rahu)
    rahu_lon = natal_positions['Rahu']['degrees'] + (SIGNS.index(natal_positions['Rahu']['sign']) * 30)
    ketu_lon = (rahu_lon + 180) % 360
    ketu_sign_index = math.floor(ketu_lon / 30)
    ketu_sign = SIGNS[ketu_sign_index]
    ketu_degrees = ketu_lon % 30
    ketu_house = calculate_house(ketu_lon, cusps)
    natal_positions['Ketu'] = {
        "sign": ketu_sign,
        "degrees": round(ketu_degrees, 4),
        "house": ketu_house,
        "retrograde": 'R'
    }
    logger.debug(f"Ketu: Lon={ketu_lon}, Sign={ketu_sign}, Degrees={ketu_degrees}, House={ketu_house}, Retro=R")
    return natal_positions
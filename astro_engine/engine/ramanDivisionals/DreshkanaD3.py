import swisseph as swe
from datetime import datetime, timedelta
import logging

# Set Swiss Ephemeris path
swe.set_ephe_path('astro_api/ephe')

# Get logger
logger = logging.getLogger(__name__)

# Constants
PLANET_NAMES = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
NAKSHATRA_NAMES = ['Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
                   'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
                   'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
                   'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta',
                   'Shatabhisha', 'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati']

def get_julian_day(date_str, time_str, tz_offset):
    """Convert local birth time to Julian Day using UTC."""
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    dt_utc = dt - timedelta(hours=tz_offset)
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600)
    logger.debug(f"Julian Day for {dt_utc}: {jd:.6f}")
    return jd

def calculate_sidereal_position(jd, planet_id, ayanamsa):
    """Calculate sidereal longitude and retrograde status for a planet."""
    pos, ret = swe.calc_ut(jd, planet_id, swe.FLG_SWIEPH | swe.FLG_SPEED)
    if ret < 0:
        logger.error(f"Error calculating position for planet ID {planet_id}")
        return 0.0, ''
    tropical_lon = pos[0]
    sidereal_lon = (tropical_lon - ayanamsa) % 360
    speed = pos[3]  # Speed in longitude
    retrograde = 'R' if speed < 0 else ''
    logger.debug(f"Planet ID {planet_id}: Tropical Lon {tropical_lon:.6f}, Sidereal Lon {sidereal_lon:.6f}, Speed {speed:.6f}, Retrograde: {retrograde}")
    return sidereal_lon, retrograde

def calculate_ascendant(jd, lat, lon):
    """Calculate sidereal ascendant longitude."""
    swe.set_sid_mode(swe.SIDM_RAMAN)
    houses, ascmc = swe.houses_ex(jd, lat, lon, b'W', flags=swe.FLG_SIDEREAL)
    asc_lon = ascmc[0] % 360
    logger.debug(f"Sidereal Ascendant Longitude: {asc_lon:.6f}")
    return asc_lon

def get_sign_and_degrees(longitude):
    """Get sign and degrees from longitude."""
    sign_index = int(longitude // 30)
    degrees = longitude % 30
    sign = SIGNS[sign_index]
    logger.debug(f"Longitude {longitude:.6f}: Sign {sign}, Degrees {degrees:.6f}")
    return sign, degrees

def calculate_d3_sign(longitude):
    """Calculate D3 sign based on degrees in natal sign."""
    natal_sign, degrees = get_sign_and_degrees(longitude)
    natal_index = SIGNS.index(natal_sign)
    if degrees < 10:
        d3_sign = natal_sign
    elif 10 <= degrees < 20:
        d3_sign = SIGNS[(natal_index + 4) % 12]  # 5th sign
    else:
        d3_sign = SIGNS[(natal_index + 8) % 12]  # 9th sign
    logger.debug(f"Longitude {longitude:.6f}: D3 Sign {d3_sign}")
    return d3_sign

def calculate_d3_house(d3_sign, d3_asc_sign):
    """Calculate D3 house number."""
    d3_sign_index = SIGNS.index(d3_sign)
    d3_asc_index = SIGNS.index(d3_asc_sign)
    house = (d3_sign_index - d3_asc_index + 12) % 12 + 1
    return house

def get_nakshatra_pada(longitude):
    """Calculate nakshatra and pada from sidereal longitude."""
    nakshatra_span = 360 / 27  # Each nakshatra is 13°20' or ~13.3333 degrees
    longitude = longitude % 360
    nakshatra_index = int(longitude / nakshatra_span)
    nakshatra_name = NAKSHATRA_NAMES[nakshatra_index]
    position_in_nakshatra = longitude % nakshatra_span
    pada = int(position_in_nakshatra / (nakshatra_span / 4)) + 1  # Each pada is ~3.3333 degrees
    return nakshatra_name, pada

def raman_drekshakana(jd, lat, lon):
    """Calculate D3 chart data with retrograde status, nakshatras, and padas."""
    swe.set_sid_mode(swe.SIDM_RAMAN)
    ayanamsa = swe.get_ayanamsa_ut(jd)
    logger.debug(f"Raman Ayanamsa: {ayanamsa:.6f}")

    asc_lon = calculate_ascendant(jd, lat, lon)
    natal_asc_sign, asc_degrees = get_sign_and_degrees(asc_lon)
    d3_asc_sign = calculate_d3_sign(asc_lon)
    asc_nakshatra, asc_pada = get_nakshatra_pada(asc_lon)

    planets = {}
    for planet_name in PLANET_NAMES:
        if planet_name == 'Rahu':
            planet_id = swe.MEAN_NODE
            lon, _ = calculate_sidereal_position(jd, planet_id, ayanamsa)
            retrograde = 'R'  # Rahu is always retrograde
        elif planet_name == 'Ketu':
            planet_id = swe.MEAN_NODE
            lon, _ = calculate_sidereal_position(jd, planet_id, ayanamsa)
            lon = (lon + 180) % 360  # Ketu is opposite Rahu
            retrograde = 'R'  # Ketu is always retrograde
        else:
            planet_id = getattr(swe, planet_name.upper())
            lon, retrograde = calculate_sidereal_position(jd, planet_id, ayanamsa)
        
        natal_sign, degrees = get_sign_and_degrees(lon)
        d3_sign = calculate_d3_sign(lon)
        house = calculate_d3_house(d3_sign, d3_asc_sign)
        nakshatra, pada = get_nakshatra_pada(lon)
        
        planets[planet_name] = {
            "natal_sign": natal_sign,
            "degrees": round(degrees, 6),
            "retrograde": retrograde,
            "d3_sign": d3_sign,
            "house": house,
            "nakshatra": nakshatra,
            "pada": pada
        }

    planets['Ascendant'] = {
        "natal_sign": natal_asc_sign,
        "degrees": round(asc_degrees, 6),
        "retrograde": "",
        "d3_sign": d3_asc_sign,
        "house": 1,
        "nakshatra": asc_nakshatra,
        "pada": asc_pada
    }

    return planets
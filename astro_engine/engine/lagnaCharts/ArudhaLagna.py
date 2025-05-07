import swisseph as swe
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
ZODIAC_SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
LORDS = {
    'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury', 'Cancer': 'Moon', 'Leo': 'Sun', 'Virgo': 'Mercury',
    'Libra': 'Venus', 'Scorpio': 'Mars', 'Sagittarius': 'Jupiter', 'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
}
PLANETS = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Rahu', 'Ketu']
SWE_PLANETS = [swe.SUN, swe.MOON, swe.MERCURY, swe.VENUS, swe.MARS, swe.JUPITER, swe.SATURN, swe.MEAN_NODE, swe.MEAN_NODE]

def get_julian_day(birth_date, birth_time, tz_offset):
    """Convert birth date and time to Julian Day with timezone adjustment."""
    logging.debug(f"Calculating Julian Day for {birth_date} {birth_time} with TZ offset {tz_offset}")
    local_dt = datetime.strptime(birth_date + " " + birth_time, "%Y-%m-%d %H:%M:%S")
    ut_dt = local_dt - timedelta(hours=tz_offset)
    jd = swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, ut_dt.hour + ut_dt.minute / 60.0 + ut_dt.second / 3600.0)
    logging.debug(f"Julian Day: {jd}")
    return jd

def calculate_ascendant(jd, latitude, longitude):
    """Calculate sidereal Ascendant longitude using Lahiri Ayanamsa."""
    logging.debug(f"Calculating Ascendant for JD: {jd}, Lat: {latitude}, Lon: {longitude}")
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    houses = swe.houses_ex(jd, latitude, longitude, flags=swe.FLG_SIDEREAL)
    asc_lon = houses[0][0]  # Ascendant longitude
    logging.debug(f"Ascendant Longitude: {asc_lon}")
    return asc_lon

def calculate_planet_data(jd, planet_code):
    """Calculate sidereal longitude and retrograde status of a planet."""
    logging.debug(f"Calculating planet data for JD: {jd}, Planet Code: {planet_code}")
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    pos, ret = swe.calc_ut(jd, planet_code, swe.FLG_SIDEREAL | swe.FLG_SPEED)
    if ret < 0:
        logging.error(f"Error calculating position for planet code {planet_code}")
        raise ValueError(f"Error calculating position for planet code {planet_code}")
    longitude = pos[0]
    speed = pos[3]  # Speed in longitude
    is_retrograde = speed < 0
    logging.debug(f"Longitude: {longitude}, Retrograde: {is_retrograde}")
    return longitude, is_retrograde

def get_sign(longitude):
    """Determine zodiac sign from sidereal longitude."""
    if not isinstance(longitude, (int, float)):
        logging.error(f"Invalid longitude type: {type(longitude)}, value: {longitude}")
        raise TypeError(f"Longitude must be a number, got {type(longitude)}")
    sign_index = int(longitude // 30) % 12
    sign = ZODIAC_SIGNS[sign_index]
    logging.debug(f"Longitude {longitude} corresponds to sign: {sign}")
    return sign

def get_arudha_lagna(asc_sign, lord_sign):
    """Calculate Arudha Lagna based on Ascendant and Lagna lord's sign."""
    logging.debug(f"Calculating Arudha Lagna for Ascendant: {asc_sign}, Lord Sign: {lord_sign}")
    asc_index = ZODIAC_SIGNS.index(asc_sign)
    lord_index = ZODIAC_SIGNS.index(lord_sign)
    if asc_sign == lord_sign:
        al_index = (asc_index + 9) % 12  # 10th house from Ascendant
    elif (lord_index - asc_index) % 12 == 6:
        al_index = (asc_index + 3) % 12  # 4th house from Ascendant
    else:
        count = (lord_index - asc_index) % 12 + 1
        al_index = (lord_index + count - 1) % 12
    al_sign = ZODIAC_SIGNS[al_index]
    logging.debug(f"Arudha Lagna: {al_sign}")
    return al_sign
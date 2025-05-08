import swisseph as swe
from datetime import datetime, timedelta

# Constants
ZODIAC_SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
LORDS = {
    'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury', 'Cancer': 'Moon', 'Leo': 'Sun', 'Virgo': 'Mercury',
    'Libra': 'Venus', 'Scorpio': 'Mars', 'Sagittarius': 'Jupiter', 'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
}
PLANETS = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Rahu', 'Ketu']
SWE_PLANETS = [swe.SUN, swe.MOON, swe.MERCURY, swe.VENUS, swe.MARS, swe.JUPITER, swe.SATURN, swe.MEAN_NODE, swe.MEAN_NODE]

def astro_utils_get_julian_day(birth_date, birth_time, tz_offset):
    """Convert birth date and time to Julian Day with timezone adjustment."""
    local_dt = datetime.strptime(birth_date + " " + birth_time, "%Y-%m-%d %H:%M:%S")
    ut_dt = local_dt - timedelta(hours=tz_offset)
    return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, ut_dt.hour + ut_dt.minute / 60.0 + ut_dt.second / 3600.0)

def astro_utils_calculate_ascendant(jd, latitude, longitude):
    """Calculate sidereal Ascendant longitude using Lahiri Ayanamsa."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    houses = swe.houses_ex(jd, latitude, longitude, flags=swe.FLG_SIDEREAL)
    return houses[0][0]  # Ascendant longitude

def astro_utils_calculate_planet_data(jd, planet_code):
    """Calculate sidereal longitude and retrograde status of a planet."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    pos, ret = swe.calc_ut(jd, planet_code, swe.FLG_SIDEREAL | swe.FLG_SPEED)
    if ret < 0:
        raise ValueError(f"Error calculating position for planet code {planet_code}")
    longitude = pos[0]
    speed = pos[3]  # Speed in longitude
    is_retrograde = speed < 0
    return longitude, is_retrograde

def astro_utils_get_sign(longitude):
    """Determine zodiac sign from sidereal longitude."""
    sign_index = int(longitude // 30) % 12
    return ZODIAC_SIGNS[sign_index]

def astro_utils_get_arudha_lagna(asc_sign, lord_sign):
    """Calculate Arudha Lagna based on Ascendant and Lagna lord's sign."""
    asc_index = ZODIAC_SIGNS.index(asc_sign)
    lord_index = ZODIAC_SIGNS.index(lord_sign)
    if asc_sign == lord_sign:
        al_index = (asc_index + 9) % 12  # 10th house from Ascendant
    elif (lord_index - asc_index) % 12 == 6:
        al_index = (asc_index + 3) % 12  # 4th house from Ascendant
    else:
        count = (lord_index - asc_index) % 12 + 1
        al_index = (lord_index + count - 1) % 12
    return ZODIAC_SIGNS[al_index]
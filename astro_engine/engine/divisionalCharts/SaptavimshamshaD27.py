import swisseph as swe
from datetime import datetime, timedelta
from decimal import Decimal, getcontext
import math

# Set precision for Decimal
getcontext().prec = 10

# Constants
PLANETS = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS, 'Mercury': swe.MERCURY,
    'Jupiter': swe.JUPITER, 'Venus': swe.VENUS, 'Saturn': swe.SATURN,
    'Rahu': swe.MEAN_NODE, 'Ketu': swe.MEAN_NODE
}
ZODIAC_SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
NAKSHATRAS = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra', 
    'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni', 
    'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha', 
    'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta', 
    'Shatabhisha', 'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
]

# Helper Functions
def get_julian_day(date_str, time_str, tz_offset):
    """Convert birth date and time to Julian Day with timezone adjustment."""
    local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    ut_dt = local_dt - timedelta(hours=tz_offset)
    return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, ut_dt.hour + ut_dt.minute / 60.0 + ut_dt.second / 3600.0)

def calculate_lahiri_ayanamsa(jd):
    """Calculate Lahiri Ayanamsa for the given Julian Day."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    return swe.get_ayanamsa(jd)

def calculate_sidereal_longitude(jd, planet_code, ayanamsa):
    """Calculate sidereal longitude of a planet or point."""
    if planet_code == 'Ketu':
        rahu_lon = calculate_sidereal_longitude(jd, swe.MEAN_NODE, ayanamsa)
        return (rahu_lon + 180) % 360
    else:
        tropical_lon = swe.calc_ut(jd, planet_code)[0][0]
        return (tropical_lon - ayanamsa) % 360

def calculate_ascendant(jd, latitude, longitude, ayanamsa):
    """Calculate sidereal Ascendant."""
    houses = swe.houses_ex(jd, latitude, longitude, hsys=b'W')
    tropical_asc = houses[0][0]
    return (tropical_asc - ayanamsa) % 360

def map_to_d27(longitude):
    """Map sidereal longitude to D27 sign and degrees using Decimal for precision."""
    longitude = Decimal(str(longitude))
    thirty = Decimal('30')
    twenty_seven = Decimal('27')
    sign_index = int(longitude // thirty)
    degrees_in_sign = longitude % thirty
    segment_size = thirty / twenty_seven
    segment = int(degrees_in_sign // segment_size)
    total_segments = sign_index * 27 + segment
    d27_sign_index = total_segments % 12
    segment_start = Decimal(segment) * segment_size
    offset = degrees_in_sign - segment_start
    d27_degrees = (offset / segment_size) * thirty
    return ZODIAC_SIGNS[d27_sign_index], float(d27_degrees)

def assign_to_house(d27_sign, d27_asc_sign):
    """Assign planet to house based on D27 Ascendant sign."""
    sign_to_index = {sign: idx for idx, sign in enumerate(ZODIAC_SIGNS)}
    asc_index = sign_to_index[d27_asc_sign]
    planet_index = sign_to_index[d27_sign]
    house = (planet_index - asc_index) % 12 + 1
    return house

def format_dms(degrees):
    """Convert decimal degrees to DMS format with high precision."""
    d = int(degrees)
    minutes_total = (degrees - d) * 60
    m = int(minutes_total)
    s = (minutes_total - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def get_nakshatra_and_pada(longitude):
    """Calculate nakshatra and pada from sidereal longitude."""
    longitude = longitude % 360
    nakshatra_index = int(longitude / (360 / 27))
    position_in_nakshatra = longitude % (360 / 27)
    pada = int(position_in_nakshatra / (360 / 108)) + 1
    nakshatra = NAKSHATRAS[nakshatra_index]
    return {"nakshatra": nakshatra, "pada": pada}

def get_retrograde_status(jd, planet_code):
    """Determine if a planet is retrograde."""
    if planet_code in ['Rahu', 'Ketu']:
        return False  # Nodes don't have retrograde motion
    pos = swe.calc_ut(jd, PLANETS[planet_code])[0]
    speed = pos[3]  # Speed is in degrees per day
    return speed < 0

def lahairi_Saptavimshamsha(birth_date, birth_time, latitude, longitude, tz_offset, user_name='Unknown'):
    """Calculate the Lahiri Saptavimshamsha (D27) chart with retrograde, nakshatras, and padas."""
    # Calculate Julian Day
    jd = get_julian_day(birth_date, birth_time, tz_offset)

    # Calculate Ayanamsa
    ayanamsa = calculate_lahiri_ayanamsa(jd)

    # Calculate Ascendant
    sidereal_asc = calculate_ascendant(jd, latitude, longitude, ayanamsa)
    d27_asc_sign, d27_asc_degrees = map_to_d27(sidereal_asc)
    asc_nakshatra_pada = get_nakshatra_and_pada(sidereal_asc)

    # Calculate planetary positions
    sidereal_positions = {}
    for planet, code in PLANETS.items():
        sidereal_lon = calculate_sidereal_longitude(jd, code, ayanamsa)
        d27_sign, d27_degrees = map_to_d27(sidereal_lon)
        house = assign_to_house(d27_sign, d27_asc_sign)
        planet_nakshatra_pada = get_nakshatra_and_pada(sidereal_lon)
        retrograde = get_retrograde_status(jd, planet)
        sidereal_positions[planet] = {
            "sidereal_longitude": format_dms(sidereal_lon),
            "sidereal_longitude_decimal": float(sidereal_lon),
            "d27_sign": d27_sign,
            "d27_degrees": format_dms(d27_degrees),
            "d27_degrees_decimal": float(d27_degrees),
            "house": house,
            "retrograde": retrograde,
            "nakshatra": planet_nakshatra_pada["nakshatra"],
            "pada": planet_nakshatra_pada["pada"]
        }

    # Construct response
    response = {
        "user_name": user_name,
        "d27_ascendant": {
            "sign": d27_asc_sign,
            "degrees": format_dms(d27_asc_degrees),
            "decimal_degrees": float(d27_asc_degrees),
            "nakshatra": asc_nakshatra_pada["nakshatra"],
            "pada": asc_nakshatra_pada["pada"]
        },
        "planets": sidereal_positions,
        "metadata": {
            "ayanamsa": "Lahiri",
            "house_system": "Whole Sign",
            "calculation_time": datetime.utcnow().isoformat(),
            "input": {
                "birth_date": birth_date,
                "birth_time": birth_time,
                "latitude": latitude,
                "longitude": longitude,
                "tz_offset": tz_offset
            }
        }
    }
    return response
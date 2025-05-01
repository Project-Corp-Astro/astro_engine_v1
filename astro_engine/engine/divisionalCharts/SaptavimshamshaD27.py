import swisseph as swe
from datetime import datetime, timedelta
from math import floor, ceil
import logging

# Zodiac sign names (1-based index: 1=Aries, 12=Pisces)
SIGN_NAMES = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

# Elemental sign groups
FIERY_SIGNS = [1, 5, 9]    # Aries, Leo, Sagittarius
EARTHY_SIGNS = [2, 6, 10]  # Taurus, Virgo, Capricorn
AIRY_SIGNS = [3, 7, 11]    # Gemini, Libra, Aquarius
WATERY_SIGNS = [4, 8, 12]  # Cancer, Scorpio, Pisces

def get_julian_day(date_str, time_str, tz_offset):
    """Convert local birth date and time to Julian Day in UT."""
    try:
        local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
        ut_dt = local_dt - timedelta(hours=tz_offset)
        hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
        jd = swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal, swe.GREG_CAL)
        if jd < 0 or jd > 5373484:  # Swiss Ephemeris valid range
            raise ValueError(f"Julian Day {jd} out of range")
        logging.debug(f"Julian Day: {jd} for UT {ut_dt}")
        return jd
    except ValueError as e:
        logging.error(f"Invalid date/time: {str(e)}")
        raise

def calculate_d1_positions(jd, latitude, longitude):
    """Calculate sidereal D1 positions using Lahiri ayanamsa."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    positions = {}
    planet_ids = {
        'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS,
        'Mercury': swe.MERCURY, 'Jupiter': swe.JUPITER,
        'Venus': swe.VENUS, 'Saturn': swe.SATURN,
        'Rahu': swe.MEAN_NODE  # Mean node for Rahu
    }
    
    for planet, pid in planet_ids.items():
        try:
            result = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL)
            if result[1] != 0:
                raise Exception(f"Error calculating {planet}: code {result[1]}")
            longitude = result[0][0] % 360
            sign = floor(longitude / 30) + 1
            degrees_in_sign = longitude % 30
            positions[planet] = {'sign': sign, 'degrees': degrees_in_sign}
            logging.debug(f"{planet} D1: Sign {sign}, Degrees {degrees_in_sign}")
        except Exception as e:
            logging.error(f"Failed to calculate {planet}: {str(e)}")
            raise
    
    ketu_longitude = (positions['Rahu']['degrees'] + 180) % 360
    ketu_sign = floor(ketu_longitude / 30) + 1
    ketu_degrees = ketu_longitude % 30
    positions['Ketu'] = {'sign': ketu_sign, 'degrees': ketu_degrees}
    
    try:
        house_pos = swe.houses_ex(jd, latitude, longitude, b'W', flags=swe.FLG_SIDEREAL)
        asc_long = house_pos[0][0] % 360
        asc_sign = floor(asc_long / 30) + 1
        asc_degrees = asc_long % 30
        positions['Ascendant'] = {'sign': asc_sign, 'degrees': asc_degrees}
        logging.debug(f"Ascendant D1: Sign {asc_sign}, Degrees {asc_degrees}")
    except Exception as e:
        logging.error(f"Failed to calculate Ascendant: {str(e)}")
        raise
    
    return positions

def get_d27_sign(sign, degrees):
    """Determine D27 sign based on D1 sign and degrees."""
    bhamsa_number = ceil(degrees / (30 / 27))
    if bhamsa_number > 27:
        bhamsa_number = 27
    
    if sign in FIERY_SIGNS:
        start_sign = 1  # Aries
    elif sign in EARTHY_SIGNS:
        start_sign = 4  # Cancer
    elif sign in AIRY_SIGNS:
        start_sign = 7  # Libra
    elif sign in WATERY_SIGNS:
        start_sign = 10  # Capricorn
    else:
        raise ValueError(f"Invalid sign: {sign}")
    
    d27_sign = (start_sign + bhamsa_number - 2) % 12 + 1
    logging.debug(f"Bhamsa {bhamsa_number} for sign {sign}: D27 sign {d27_sign}")
    return d27_sign

def calculate_d27_positions(d1_positions):
    """Calculate D27 positions for all planets and Ascendant."""
    d27_positions = {}
    for planet, pos in d1_positions.items():
        d27_sign = get_d27_sign(pos['sign'], pos['degrees'])
        d27_positions[planet] = d27_sign
    return d27_positions

def calculate_d27_houses(d27_asc_sign, d27_positions):
    """Calculate D27 houses using whole-sign house system."""
    houses = {}
    for planet, d27_sign in d27_positions.items():
        house = (d27_sign - d27_asc_sign) % 12 + 1
        houses[planet] = house
    return houses
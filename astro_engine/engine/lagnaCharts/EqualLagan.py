import swisseph as swe
from datetime import datetime, timedelta

# Zodiac signs for reference
SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

def bava_get_julian_day(date_str, time_str, tz_offset):
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

def bava_calculate_ascendant(jd, latitude, longitude):
    """Calculate the sidereal ascendant longitude using Lahiri Ayanamsa."""
    try:
        swe.set_sid_mode(swe.SIDM_LAHIRI)  # Set Lahiri Ayanamsa
        cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b'P', flags=swe.FLG_SIDEREAL)
        ascendant = ascmc[0] % 360.0  # Ascendant longitude in degrees
        return ascendant
    except Exception as e:
        raise Exception(f"Ascendant calculation failed: {str(e)}")

def bava_get_planet_positions(jd):
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

def bava_calculate_equal_bhava_cusps(ascendant):
    """Calculate the midpoints (cusps) of all 12 houses, each spanning 30 degrees."""
    cusps = [(ascendant + (n - 1) * 30) % 360 for n in range(1, 13)]
    return cusps

def bava_assign_planets_to_houses(planetary_positions, ascendant_sign_index):
    """Assign planets to houses using Whole Sign system based on Equal Bhava Lagna."""
    house_assignments = {}
    for planet, (longitude, _) in planetary_positions.items():
        planet_sign_index = int(longitude // 30)
        house = (planet_sign_index - ascendant_sign_index) % 12 + 1
        house_assignments[planet] = house
    return house_assignments

def bava_format_dms(degrees):
    """Format degrees into degrees, minutes, and seconds."""
    degrees = degrees % 360.0
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = int(((degrees - d) * 60 - m) * 60)
    return f"{d}° {m}' {s}\""
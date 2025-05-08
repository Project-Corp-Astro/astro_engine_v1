




import swisseph as swe
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
ZODIAC_SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
PLANETS = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
SWE_PLANETS = [swe.SUN, swe.MOON, swe.MARS, swe.MERCURY, swe.JUPITER, swe.VENUS, swe.SATURN]

# Bindu allocation rules (1-based house numbers)
BINDU_RULES = {
    "Sun": {
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
        "Jupiter": [5, 6, 9, 11],
        "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
        "Sun": [1, 2, 4, 7, 8, 9, 10, 11],
        "Venus": [6, 7, 12],
        "Mercury": [3, 5, 6, 9, 10, 11, 12],
        "Moon": [3, 6, 10, 11],
        "Ascendant": [3, 4, 6, 10, 11, 12]
    },
    "Moon": {
        "Saturn": [3, 5, 6, 11],
        "Jupiter": [1, 4, 7, 8, 10, 11, 12],
        "Mars": [2, 3, 5, 6, 9, 10, 11],
        "Sun": [3, 6, 7, 8, 10, 11],
        "Venus": [3, 4, 5, 7, 9, 10, 11],
        "Mercury": [1, 3, 4, 5, 7, 8, 10, 11],
        "Moon": [1, 3, 6, 7, 10, 11],
        "Ascendant": [3, 6, 10, 11]
    },
    "Mars": {
        "Saturn": [1, 4, 7, 8, 9, 10, 11],
        "Jupiter": [6, 10, 11, 12],
        "Mars": [1, 2, 4, 7, 8, 10, 11],
        "Sun": [3, 5, 6, 10, 11],
        "Venus": [6, 8, 11, 12],
        "Mercury": [3, 5, 6, 11],
        "Moon": [3, 6, 11],
        "Ascendant": [1, 3, 6, 10, 11]
    },
    "Mercury": {
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
        "Jupiter": [6, 8, 11, 12],
        "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
        "Sun": [5, 6, 9, 11, 12],
        "Venus": [1, 2, 3, 4, 5, 8, 9, 11],
        "Mercury": [1, 3, 5, 6, 9, 10, 11, 12],
        "Moon": [2, 4, 6, 8, 10, 11],
        "Ascendant": [1, 2, 4, 6, 8, 10, 11]
    },
    "Venus": {
        "Saturn": [3, 4, 5, 8, 9, 10, 11],
        "Jupiter": [5, 8, 9, 10, 11],
        "Mars": [3, 5, 6, 9, 11, 12],
        "Sun": [8, 11, 12],
        "Venus": [1, 2, 3, 4, 5, 8, 9, 10, 11],
        "Mercury": [3, 5, 6, 9, 11],
        "Moon": [1, 2, 3, 4, 5, 8, 9, 11, 12],
        "Ascendant": [1, 2, 3, 4, 5, 8, 9, 11]
    },
    "Jupiter": {
        "Saturn": [3, 5, 6, 12],
        "Jupiter": [1, 2, 3, 4, 7, 8, 10, 11],
        "Mars": [1, 2, 4, 7, 8, 10, 11],
        "Sun": [1, 2, 3, 4, 7, 8, 9, 10, 11],
        "Venus": [2, 5, 6, 9, 10, 11],
        "Mercury": [1, 2, 4, 5, 6, 9, 10, 11],
        "Moon": [2, 5, 7, 9, 11],
        "Ascendant": [1, 2, 4, 5, 6, 7, 9, 10, 11]
    },
    "Saturn": {
        "Saturn": [3, 5, 6, 11],
        "Jupiter": [5, 6, 11, 12],
        "Mars": [3, 5, 6, 10, 11, 12],
        "Sun": [1, 2, 4, 7, 8, 10, 11],
        "Venus": [6, 11, 12],
        "Mercury": [6, 8, 9, 10, 11, 12],
        "Moon": [3, 6, 11],
        "Ascendant": [1, 3, 4, 6, 10, 11]
    },
    "Ascendant": {
        "Saturn": [1, 3, 4, 6, 10, 11],
        "Jupiter": [1, 2, 4, 5, 6, 7, 9, 10, 11],
        "Mars": [1, 3, 6, 10, 11],
        "Sun": [3, 4, 6, 10, 11, 12],
        "Venus": [1, 2, 3, 4, 5, 8, 9],
        "Mercury": [1, 2, 4, 6, 8, 10, 11],
        "Moon": [3, 6, 10, 11, 12],
        "Ascendant": [3, 6, 10, 11]
    }
}



# Expected bindu totals for validation
EXPECTED_TOTALS = {
    "Sun": 48, "Moon": 49, "Mars": 39, "Mercury": 54,
    "Venus": 52, "Jupiter": 56, "Saturn": 39, "Ascendant": 49
}

def astro_binna_get_julian_day(birth_date, birth_time, tz_offset):
    """Convert birth date and time to Julian Day with timezone adjustment."""
    logging.debug(f"Calculating Julian Day for {birth_date} {birth_time} with TZ offset {tz_offset}")
    local_dt = datetime.strptime(birth_date + " " + birth_time, "%Y-%m-%d %H:%M:%S")
    ut_dt = local_dt - timedelta(hours=tz_offset)
    jd = swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, ut_dt.hour + ut_dt.minute / 60.0 + ut_dt.second / 3600.0)
    logging.debug(f"Julian Day: {jd}")
    return jd

def astro_binna_calculate_ascendant(jd, latitude, longitude):
    """Calculate sidereal Ascendant longitude using Lahiri Ayanamsa."""
    logging.debug(f"Calculating Ascendant for JD: {jd}, Lat: {latitude}, Lon: {longitude}")
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    houses = swe.houses_ex(jd, latitude, longitude, flags=swe.FLG_SIDEREAL)
    asc_lon = houses[0][0]  # Ascendant longitude
    logging.debug(f"Ascendant Longitude: {asc_lon}")
    return asc_lon

def astro_utils_calculate_sidereal_longitude(jd, planet_code):
    """Calculate sidereal longitude of a planet using Lahiri Ayanamsa."""
    logging.debug(f"Calculating sidereal longitude for planet code: {planet_code}")
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    pos, _ = swe.calc_ut(jd, planet_code, swe.FLG_SIDEREAL)
    longitude = pos[0] % 360
    logging.debug(f"Sidereal Longitude: {longitude}")
    return longitude

def astro_binna_get_sign_index(longitude):
    """Determine zodiac sign index (0-based) from longitude."""
    sign_index = int(longitude // 30) % 12
    logging.debug(f"Longitude {longitude} corresponds to sign index: {sign_index}")
    return sign_index

def astro_utils_calculate_planet_positions(jd):
    """Calculate sidereal positions of planets using Lahiri Ayanamsa."""
    logging.debug(f"Calculating planet positions for JD: {jd}")
    positions = {}
    for planet, code in zip(PLANETS, SWE_PLANETS):
        lon = astro_utils_calculate_sidereal_longitude(jd, code)
        positions[planet] = {"longitude": lon, "sign_index": astro_utils_get_sign_index(lon)}
    return positions

def astro_utils_calculate_bhinnashtakavarga(positions):
    """Calculate Bhinnashtakavarga matrix with precise bindu assignment."""
    contributors = PLANETS + ['Ascendant']
    targets = PLANETS + ['Ascendant']
    bhinnashtakavarga = {target: [0] * 12 for target in targets}

    for target in targets:
        for contributor in contributors:
            if contributor not in positions:
                continue
            contributor_sign = positions[contributor]["sign_index"]
            for sign_idx in range(12):  # 0-based: Aries=0, ..., Pisces=11
                relative_house = (sign_idx - contributor_sign) % 12 + 1  # 1-based house
                if relative_house in BINDU_RULES[target][contributor]:
                    bhinnashtakavarga[target][sign_idx] += 1

    return bhinnashtakavarga

def astro_utils_validate_totals(bhinnashtakavarga):
    """Validate Bhinnashtakvarga totals against expected values."""
    errors = []
    for target, expected in EXPECTED_TOTALS.items():
        total = sum(bhinnashtakavarga[target])
        if total != expected:
            errors.append(f"{target}: {total} (expected {expected})")
    if errors:
        raise ValueError("Validation failed: " + "; ".join(errors))

def astro_utils_format_dms(degrees):
    """Convert decimal degrees to degrees, minutes, seconds format."""
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = (degrees - d - m / 60.0) * 3600.0
    return f"{d}° {abs(m)}' {abs(s):.2f}\""
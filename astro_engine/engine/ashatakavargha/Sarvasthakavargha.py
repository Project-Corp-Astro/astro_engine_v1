import swisseph as swe
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
PLANETS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN
}
BINDU_RULES = {
    "Sun": {
        "Sun": [1, 2, 4, 7, 8, 9, 10, 11], "Moon": [3, 6, 10, 11], "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [3, 5, 6, 9, 10, 11, 12], "Jupiter": [5, 6, 9, 11], "Venus": [6, 7, 12],
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11], "Ascendant": [3, 4, 6, 10, 11, 12]
    },
    "Moon": {
        "Sun": [3, 6, 7, 10, 11], "Moon": [1, 3, 6, 7, 10, 11], "Mars": [2, 3, 6, 10, 11],
        "Mercury": [1, 3, 5, 6, 7, 9, 10, 11], "Jupiter": [1, 2, 3, 4, 5, 7, 10, 11],
        "Venus": [1, 2, 3, 4, 5, 8, 10, 11, 12], "Saturn": [3, 6, 11], "Ascendant": [3, 6, 10, 11]
    },
    "Mars": {
        "Sun": [1, 2, 4, 7, 8, 10, 11], "Moon": [3, 6, 11], "Mars": [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [3, 5, 6, 9, 11], "Jupiter": [6, 11, 12], "Venus": [6, 7, 12],
        "Saturn": [1, 2, 4, 7, 8, 10, 11], "Ascendant": [3, 4, 6, 10, 11, 12]
    },
    "Mercury": {
        "Sun": [1, 3, 5, 6, 9, 10, 11], "Moon": [1, 2, 4, 5, 7, 8, 10, 11], "Mars": [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [1, 2, 3, 4, 5, 7, 9, 10, 11], "Jupiter": [1, 2, 4, 5, 7, 8, 10, 11],
        "Venus": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], "Saturn": [3, 5, 6, 9, 11],
        "Ascendant": [1, 2, 4, 5, 7, 8, 10, 11]
    },
    "Jupiter": {
        "Sun": [1, 2, 3, 4, 7, 8, 10, 11], "Moon": [1, 2, 3, 4, 5, 7, 10, 11], "Mars": [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [1, 2, 3, 4, 5, 7, 8, 10, 11], "Jupiter": [1, 2, 3, 4, 5, 7, 8, 9, 10, 11],
        "Venus": [2, 5, 6, 9, 11, 12], "Saturn": [3, 5, 6, 11], "Ascendant": [1, 2, 3, 4, 7, 8, 10, 11]
    },
    "Venus": {
        "Sun": [6, 7, 12], "Moon": [1, 2, 3, 4, 5, 8, 9, 10, 11], "Mars": [6, 7, 12],
        "Mercury": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], "Jupiter": [2, 5, 6, 9, 11, 12],
        "Venus": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], "Saturn": [1, 2, 3, 4, 5, 8, 9, 10, 11],
        "Ascendant": [1, 2, 3, 4, 5, 8, 9, 10, 11]
    },
    "Saturn": {
        "Sun": [1, 2, 4, 7, 8, 10, 11], "Moon": [3, 6, 11], "Mars": [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [3, 5, 6, 9, 11], "Jupiter": [6, 11, 12], "Venus": [6, 7, 12],
        "Saturn": [1, 2, 4, 7, 8, 10, 11], "Ascendant": [3, 4, 6, 10, 11, 12]
    },
    "Ascendant": {
        "Sun": [3, 6, 10, 11], "Moon": [3, 6, 10, 11], "Mars": [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [1, 2, 4, 5, 7, 8, 10, 11], "Jupiter": [1, 2, 3, 4, 7, 8, 10, 11],
        "Venus": [1, 2, 3, 4, 5, 8, 9, 10, 11], "Saturn": [3, 6, 11], "Ascendant": [1, 2, 3, 4, 5, 7, 8, 9, 10, 11]
    }
}
EXPECTED_TOTALS = {
    "Sun": 48, "Moon": 49, "Mars": 39, "Mercury": 54,
    "Jupiter": 56, "Venus": 52, "Saturn": 39, "Ascendant": 49
}

def get_julian_day(date_str, time_str, tz_offset):
    """Convert birth date, time, and timezone offset to Julian Day."""
    local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    ut_dt = local_dt - timedelta(hours=tz_offset)
    hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
    jd = swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal, swe.GREG_CAL)
    logging.debug(f"Julian Day: {jd}")
    return jd

def calculate_ayanamsa(jd):
    """Calculate Lahiri Ayanamsa for the given Julian Day."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa = swe.get_ayanamsa_ut(jd)
    logging.debug(f"Ayanamsa: {ayanamsa}")
    return ayanamsa

def calculate_sidereal_longitude(jd, planet_code):
    """Calculate sidereal longitude of a planet using Lahiri Ayanamsa."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    lon = swe.calc_ut(jd, planet_code, swe.FLG_SIDEREAL | swe.FLG_SPEED)[0][0]
    lon = lon % 360
    logging.debug(f"Planet {planet_code} longitude: {lon}")
    return lon

def calculate_ascendant(jd, latitude, longitude):
    """Calculate sidereal Ascendant longitude."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    house_cusps, ascmc = swe.houses_ex(jd, latitude, longitude, flags=swe.FLG_SIDEREAL)
    asc_lon = ascmc[0] % 360
    logging.debug(f"Ascendant longitude: {asc_lon}")
    return asc_lon

def get_sign_index(longitude):
    """Convert longitude to 0-based sign index (0=Aries, 11=Pisces)."""
    if not isinstance(longitude, (int, float)):
        raise TypeError(f"Longitude must be a number, got {type(longitude)}")
    sign_index = int(longitude // 30) % 12
    logging.debug(f"Longitude {longitude} -> Sign index: {sign_index}")
    return sign_index

def calculate_relative_house(from_sign, to_sign):
    """Calculate the relative house from one sign to another (1-based)."""
    if not isinstance(from_sign, int) or not isinstance(to_sign, int):
        raise TypeError(f"Sign indices must be integers: from_sign={from_sign}, to_sign={to_sign}")
    relative_house = (to_sign - from_sign) % 12 + 1
    logging.debug(f"From sign {from_sign} to {to_sign} -> Relative house: {relative_house}")
    return relative_house

def calculate_bhinnashtakavarga(positions):
    """Calculate Bhinnashtakavarga matrix with precise Bindu assignment."""
    if not isinstance(positions, dict):
        logging.error(f"Positions must be a dictionary, got: {type(positions)}")
        raise TypeError("Positions must be a dictionary")

    contributors = list(PLANETS.keys()) + ["Ascendant"]
    targets = list(PLANETS.keys()) + ["Ascendant"]
    bhinnashtakavarga = {target: [0] * 12 for target in targets}

    for target in targets:
        if target not in BINDU_RULES:
            logging.warning(f"No Bindu rules for target: {target}")
            continue
        rules = BINDU_RULES[target]
        for contributor in contributors:
            if contributor not in positions or "sign_index" not in positions[contributor]:
                logging.error(f"Missing or invalid position data for {contributor}: {positions.get(contributor)}")
                raise KeyError(f"Missing position data for {contributor}")
            contributor_sign = positions[contributor]["sign_index"]
            if not isinstance(contributor_sign, int):
                logging.error(f"Sign index for {contributor} must be an integer, got: {type(contributor_sign)}")
                raise TypeError(f"Sign index for {contributor} must be an integer")
            for sign_idx in range(12):
                relative_house = calculate_relative_house(contributor_sign, sign_idx)
                if contributor in rules and relative_house in rules[contributor]:
                    logging.debug(f"Accessing bhinnashtakavarga[{target}][{sign_idx}], type(sign_idx): {type(sign_idx)}")
                    bhinnashtakavarga[target][sign_idx] += 1
                    logging.debug(f"Assigned Bindu: {target}[{sign_idx}] += 1 from {contributor}")

    return bhinnashtakavarga

def validate_bhinnashtakavarga(bhinnashtakavarga):
    """Validate Bhinnashtakavarga totals against expected values."""
    if not isinstance(bhinnashtakavarga, dict):
        logging.error(f"Bhinnashtakavarga must be a dictionary, got: {type(bhinnashtakavarga)}")
        raise TypeError("Bhinnashtakavarga must be a dictionary")

    errors = []
    for target, expected in EXPECTED_TOTALS.items():
        if target not in bhinnashtakavarga:
            errors.append(f"Missing Bhinnashtakavarga for {target}")
            continue
        bindus = bhinnashtakavarga[target]
        if not isinstance(bindus, list) or len(bindus) != 12:
            errors.append(f"Bhinnashtakavarga for {target} must be a list of 12 integers, got: {bindus}")
            continue
        total = sum(bindus)
        if total != expected:
            errors.append(f"{target}: Total Bindus {total} (expected {expected})")
    if errors:
        error_msg = "; ".join(errors)
        logging.error(f"Validation failed: {error_msg}")
        raise ValueError(f"Bhinnashtakavarga validation failed: {error_msg}")

def calculate_sarvashtakavarga(bhinnashtakavarga):
    """Calculate Sarvashtakavarga by summing Bhinnashtakavarga Bindus."""
    if not isinstance(bhinnashtakavarga, dict):
        logging.error(f"Bhinnashtakavarga must be a dictionary, got: {type(bhinnashtakavarga)}")
        raise TypeError("Bhinnashtakavarga must be a dictionary")

    sarvashtakavarga = [0] * 12
    for target in bhinnashtakavarga:
        bindus = bhinnashtakavarga[target]
        if not isinstance(bindus, list) or len(bindus) != 12:
            logging.error(f"Bhinnashtakavarga[{target}] must be a list of 12 integers, got: {bindus}")
            raise TypeError(f"Bhinnashtakavarga[{target}] must be a list of 12 integers")
        for sign_idx in range(12):
            logging.debug(f"Accessing sarvashtakavarga[{sign_idx}], type(sign_idx): {type(sign_idx)}")
            sarvashtakavarga[sign_idx] += bindus[sign_idx]

    total_bindus = sum(sarvashtakavarga)
    if total_bindus != 337:
        logging.error(f"Sarvashtakavarga total is {total_bindus}, expected 337")
        raise ValueError(f"Sarvashtakavarga total is {total_bindus}, expected 337")
    return sarvashtakavarga

def map_to_houses(sarvashtakavarga, asc_sign_index):
    """Map Sarvashtakavarga Bindus to the 12 houses based on Ascendant."""
    if not isinstance(sarvashtakavarga, list) or len(sarvashtakavarga) != 12:
        logging.error(f"Sarvashtakavarga must be a list of 12 integers, got: {sarvashtakavarga}")
        raise TypeError("Sarvashtakavarga must be a list of 12 integers")
    if not isinstance(asc_sign_index, int):
        logging.error(f"Ascendant sign index must be an integer, got: {type(asc_sign_index)}")
        raise TypeError("Ascendant sign index must be an integer")

    house_bindus = {}
    for house in range(1, 13):
        sign_idx = (asc_sign_index + house - 1) % 12
        logging.debug(f"Accessing sarvashtakavarga[{sign_idx}], type(sign_idx): {type(sign_idx)}")
        house_bindus[f"House {house}"] = sarvashtakavarga[sign_idx]
    return house_bindus

def format_dms(degrees):
    """Format degrees into DMS (degrees, minutes, seconds)."""
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = (degrees - d - m / 60) * 3600
    return f"{d}° {m}' {s:.2f}\""

def get_planetary_positions(jd):
    """Calculate planetary positions for the given Julian Day."""
    positions = {}
    for planet in PLANETS:
        lon = calculate_sidereal_longitude(jd, PLANETS[planet])
        sign_idx = get_sign_index(lon)
        sign_deg = lon % 30
        positions[planet] = {
            "sign": SIGNS[sign_idx],
            "sign_index": sign_idx,
            "degrees": format_dms(sign_deg)
        }
    asc_lon = calculate_ascendant(jd, 0, 0)  # Assuming latitude/longitude 0 for simplicity
    asc_sign_idx = get_sign_index(asc_lon)
    positions["Ascendant"] = {
        "sign": SIGNS[asc_sign_idx],
        "sign_index": asc_sign_idx,
        "degrees": format_dms(asc_lon % 30)
    }
    return positions

# Example usage (for debugging)
if __name__ == "__main__":
    jd = get_julian_day("2023-01-01", "12:00:00", 5.5)
    positions = get_planetary_positions(jd)
    bhav = calculate_bhinnashtakavarga(positions)
    validate_bhinnashtakavarga(bhav)
    sav = calculate_sarvashtakavarga(bhav)
    houses = map_to_houses(sav, positions["Ascendant"]["sign_index"])
    print(houses)
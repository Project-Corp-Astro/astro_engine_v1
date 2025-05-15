# import swisseph as swe
# from datetime import datetime, timedelta

# # Zodiac signs (0-based index: 0=Aries, 11=Pisces)
# SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
#          "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

# # Planet codes for Swiss Ephemeris
# PLANETS = {
#     "Sun": swe.SUN,
#     "Moon": swe.MOON,
#     "Mars": swe.MARS,
#     "Mercury": swe.MERCURY,
#     "Jupiter": swe.JUPITER,
#     "Venus": swe.VENUS,
#     "Saturn": swe.SATURN,
# }

# # Corrected Bindu allocation rules (1-based house numbers)
# BINDU_RULES = {
#     "Sun": {
#         "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
#         "Jupiter": [5, 6, 9, 11],
#         "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
#         "Sun": [1, 2, 4, 7, 8, 9, 10, 11],
#         "Venus": [6, 7, 12],
#         "Mercury": [3, 5, 6, 9, 10, 11, 12],
#         "Moon": [3, 6, 10, 11],
#         "Ascendant": [3, 4, 6, 10, 11, 12]    # 6 
#     },
#     "Moon": {
#         "Saturn": [3, 5, 6, 11],
#         "Jupiter": [1, 4, 7, 8, 10, 11, 12],
#         "Mars": [2, 3, 5, 6, 9, 10, 11],
#         "Sun": [3, 6, 7, 8, 10, 11],
#         "Venus": [3, 4, 5, 7, 9, 10, 11],
#         "Mercury": [1, 3, 4, 5, 7, 8, 10, 11],
#         "Moon": [1, 3, 6, 7, 10, 11],
#         "Ascendant": [3, 6, 10, 11]    # 4
#     },
#     "Mars": {
#         "Saturn": [1, 4, 7, 8, 9, 10, 11],
#         "Jupiter": [6, 10, 11, 12],
#         "Mars": [1, 2, 4, 7, 8, 10, 11],
#         "Sun": [3, 5, 6, 10, 11],
#         "Venus": [6, 8, 11, 12],
#         "Mercury": [3, 5, 6, 11],
#         "Moon": [3, 6, 11],  # Adjusted: Added house 5 to reach 39 bindus
#         "Ascendant": [1, 3, 6, 10, 11]      # 5 
#     },
#     "Mercury": {
#         "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
#         "Jupiter": [6, 8, 11, 12],
#         "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
#         "Sun": [5, 6, 9, 11, 12],
#         "Venus": [1, 2, 3, 4, 5, 8, 9, 11],
#         "Mercury": [1, 3, 5, 6, 9, 10, 11, 12],
#         "Moon": [2, 4, 6, 8, 10, 11],
#         "Ascendant": [1, 2, 4, 6, 8, 10, 11]    # 7 
#     },
#     "Venus": {
#         "Saturn": [3, 4, 5, 8, 9, 10, 11],
#         "Jupiter": [5, 8, 9, 10, 11],
#         "Mars": [3, 5, 6, 9, 11, 12],
#         "Sun": [8, 11, 12],
#         "Venus": [1, 2, 3, 4, 5, 8, 9, 10, 11],  # Adjusted: Removed 10 and 11 to reach 50 bindus
#         "Mercury": [3, 5, 6, 9, 11],
#         "Moon": [1, 2, 3, 4, 5, 8, 9, 11, 12],
#         "Ascendant": [1, 2, 3, 4, 5, 8, 9, 11]      # 8 
#     },
#     "Jupiter": {
#         "Saturn": [3, 5, 6, 12],
#         "Jupiter": [1, 2, 3, 4, 7, 8, 10, 11],  # Adjusted: Removed 7, 8, 10, 11 to reach 52 bindus
#         "Mars": [1, 2, 4, 7, 8, 10, 11],
#         "Sun": [1, 2, 3, 4, 7, 8, 9, 10, 11],
#         "Venus": [2, 5, 6, 9, 10, 11],
#         "Mercury": [1, 2, 4, 5, 6, 9, 10, 11],
#         "Moon": [2, 5, 7, 9, 11],
#         "Ascendant": [1, 2, 4, 5, 6, 7, 9, 10, 11]    # 9 
#     },
#     "Saturn": {
#         "Saturn": [3, 5, 6, 11],
#         "Jupiter": [5, 6, 11, 12],
#         "Mars": [3, 5, 6, 10, 11, 12],
#         "Sun": [1, 2, 4, 7, 8, 10, 11],
#         "Venus": [6, 11, 12],
#         "Mercury": [6, 8, 9, 10, 11, 12],
#         "Moon": [3, 6, 11],
#         "Ascendant": [1, 3, 4, 6, 10, 11]      # 6
#     },
#     "Ascendant": {
#         "Saturn": [1, 3, 4, 6, 10, 11],
#         "Jupiter": [1, 2, 4, 5, 6, 7, 9, 10, 11],
#         "Mars": [1, 3, 6, 10, 11],  
#         "Sun": [3, 4, 6, 10, 11, 12],   
#         "Venus": [1, 2, 3, 4, 5, 8, 9],
#         "Mercury": [1, 2, 4, 6, 8, 10, 11],
#         "Moon": [3, 6, 10, 11, 12],
#         "Ascendant": [3, 6, 10, 11]      
#     }
# }

# # Expected bindu totals for validation
# EXPECTED_TOTALS = {
#     "Sun": 48, "Moon": 49, "Mars": 39, "Mercury": 54,
#     "Venus": 52, "Jupiter": 56, "Saturn": 39, "Ascendant": 49
# }

# # Helper Functions
# def bv_get_julian_day(date_str, time_str, tz_offset):
#     """Convert birth date, time, and timezone offset to Julian Day."""
#     local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
#     ut_dt = local_dt - timedelta(hours=tz_offset)
#     hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
#     jd = swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal, swe.GREG_CAL)
#     return jd

# def bv_calculate_ayanamsa(jd):
#     """Calculate Lahiri Ayanamsa for the given Julian Day."""
#     swe.set_sid_mode(swe.SIDM_RAMAN)
#     ayanamsa = swe.get_ayanamsa_ut(jd)
#     return ayanamsa

# def bv_calculate_sidereal_longitude(jd, planet_code):
#     """Calculate sidereal longitude of a planet using Lahiri Ayanamsa."""
#     swe.set_sid_mode(swe.SIDM_RAMAN)
#     try:
#         lon = swe.calc_ut(jd, planet_code, swe.FLG_SIDEREAL | swe.FLG_SPEED)[0][0]
#         return lon % 360
#     except Exception as e:
#         raise Exception(f"Failed to calculate longitude: {str(e)}")

# def bv_calculate_ascendant(jd, latitude, longitude):
#     """Calculate sidereal Ascendant longitude."""
#     swe.set_sid_mode(swe.SIDM_RAMAN)
#     try:
#         house_cusps, ascmc = swe.houses_ex(jd, latitude, longitude, flags=swe.FLG_SIDEREAL)
#         return ascmc[0] % 360
#     except Exception as e:
#         raise Exception(f"Failed to calculate ascendant: {str(e)}")

# def bv_get_sign_index(longitude):
#     """Convert longitude to 0-based sign index (0=Aries, 11=Pisces)."""
#     return int(longitude // 30) % 12

# def bv_calculate_relative_house(from_sign, to_sign):
#     """Calculate the relative house from one sign to another (1-based)."""
#     relative_house = (to_sign - from_sign) % 12 + 1
#     return relative_house

# def bv_calculate_bhinnashtakavarga_matrix(positions):
#     """Calculate Bhinnashtakavarga matrix with precise bindu assignment."""
#     contributors = list(PLANETS.keys()) + ["Ascendant"]
#     targets = list(PLANETS.keys()) + ["Ascendant"]
#     bhinnashtakavarga = {target: [0] * 12 for target in targets}

#     for target in targets:
#         for contributor in contributors:
#             if contributor not in positions:
#                 continue
#             contributor_sign = positions[contributor]["sign_index"]
#             for sign_idx in range(12):  # 0-based: Aries=0, ..., Pisces=11
#                 relative_house = bv_calculate_relative_house(contributor_sign, sign_idx)
#                 if relative_house in BINDU_RULES[target][contributor]:
#                     bhinnashtakavarga[target][sign_idx] += 1

#     return bhinnashtakavarga

# def bv_validate_totals(bhinnashtakavarga):
#     """Validate Bhinnashtakvarga totals against expected values."""
#     errors = []
#     for target, expected in EXPECTED_TOTALS.items():
#         total = sum(bhinnashtakavarga[target])
#         if total != expected:
#             errors.append(f"{target}: {total} (expected {expected})")
#     if errors:
#         raise ValueError("Validation failed: " + "; ".join(errors))

# def bv_format_dms(degrees):
#     """Format degrees into DMS (degrees, minutes, seconds)."""
#     d = int(degrees)
#     m = int((degrees - d) * 60)
#     s = (degrees - d - m / 60) * 3600
#     return f"{d}° {m}' {s:.2f}\""

# def raman_binnastakavargha(user_name, birth_date, birth_time, latitude, longitude, tz_offset):
#     """Calculate Bhinnashtakavarga and related astrological data."""
#     # Calculate Julian Day and Ayanamsa
#     jd = bv_get_julian_day(birth_date, birth_time, tz_offset)
#     ayanamsa = bv_calculate_ayanamsa(jd)

#     # Calculate planetary positions and Ascendant
#     positions = {}
#     planet_positions = {}
#     for planet in PLANETS:
#         lon = bv_calculate_sidereal_longitude(jd, PLANETS[planet])
#         sign_idx = bv_get_sign_index(lon)
#         positions[planet] = {
#             "longitude": lon,
#             "sign_index": sign_idx
#         }
#         sign_deg = lon % 30
#         planet_positions[planet] = {
#             "sign": SIGNS[sign_idx],
#             "degrees": bv_format_dms(sign_deg)
#         }

#     asc_lon = bv_calculate_ascendant(jd, latitude, longitude)
#     asc_sign = bv_get_sign_index(asc_lon)
#     positions["Ascendant"] = {
#         "longitude": asc_lon,
#         "sign_index": asc_sign
#     }
#     asc_deg = asc_lon % 30

#     # Calculate Bhinnashtakavarga
#     bhinnashtakavarga = bv_calculate_bhinnashtakavarga_matrix(positions)
#     bv_validate_totals(bhinnashtakavarga)

#     # Format output
#     bhinnashtakavarga_output = {
#         target: {
#             "signs": {SIGNS[i]: bindus[i] for i in range(12)},
#             "total_bindus": sum(bindus)
#         } for target, bindus in bhinnashtakavarga.items()
#     }

#     # Response
#     response = {
#         "user_name": user_name,
#         "birth_details": {
#             "birth_date": birth_date,
#             "birth_time": birth_time,
#             "latitude": latitude,
#             "longitude": longitude,
#             "timezone_offset": tz_offset
#         },
#         "planetary_positions": planet_positions,
#         "ascendant": {"sign": SIGNS[asc_sign], "degrees": bv_format_dms(asc_deg)},
#         "bhinnashtakavarga": bhinnashtakavarga_output,
#         "notes": {
#             "ayanamsa": "Lahiri",
#             "ayanamsa_value": f"{ayanamsa:.6f}",
#             "chart_type": "Rasi",
#             "house_system": "Whole Sign"
#         }
#     }
#     return response



import swisseph as swe
from datetime import datetime, timedelta
import math

# Constants
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
}

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

EXPECTED_TOTALS = {
    "Sun": 48, "Moon": 49, "Mars": 39, "Mercury": 54,
    "Venus": 52, "Jupiter": 56, "Saturn": 39, "Ascendant": 49
}

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# Helper Functions
def bv_get_julian_day(date_str, time_str, tz_offset):
    """Convert birth date, time, and timezone offset to Julian Day."""
    local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    ut_dt = local_dt - timedelta(hours=tz_offset)
    hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
    jd = swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal, swe.GREG_CAL)
    return jd

def bv_calculate_ayanamsa(jd):
    """Calculate Lahiri Ayanamsa for the given Julian Day."""
    swe.set_sid_mode(swe.SIDM_RAMAN)
    ayanamsa = swe.get_ayanamsa_ut(jd)
    return ayanamsa

def bv_calculate_sidereal_longitude(jd, planet_code):
    """Calculate sidereal longitude of a planet using Lahiri Ayanamsa."""
    swe.set_sid_mode(swe.SIDM_RAMAN)
    try:
        lon = swe.calc_ut(jd, planet_code, swe.FLG_SIDEREAL | swe.FLG_SPEED)[0][0]
        return lon % 360
    except Exception as e:
        raise Exception(f"Failed to calculate longitude: {str(e)}")

def bv_calculate_ascendant(jd, latitude, longitude):
    """Calculate sidereal Ascendant longitude."""
    swe.set_sid_mode(swe.SIDM_RAMAN)
    try:
        house_cusps, ascmc = swe.houses_ex(jd, latitude, longitude, flags=swe.FLG_SIDEREAL)
        return ascmc[0] % 360
    except Exception as e:
        raise Exception(f"Failed to calculate ascendant: {str(e)}")

def bv_get_sign_index(longitude):
    """Convert longitude to 0-based sign index (0=Aries, 11=Pisces)."""
    return int(longitude // 30) % 12

def bv_calculate_relative_house(from_sign, to_sign):
    """Calculate the relative house from one sign to another (1-based)."""
    relative_house = (to_sign - from_sign) % 12 + 1
    return relative_house

def bv_calculate_bhinnashtakavarga_matrix(positions):
    """Calculate Bhinnashtakavarga matrix with precise bindu assignment."""
    contributors = list(PLANETS.keys()) + ["Ascendant"]
    targets = list(PLANETS.keys()) + ["Ascendant"]
    bhinnashtakavarga = {target: [0] * 12 for target in targets}

    for target in targets:
        for contributor in contributors:
            if contributor not in positions:
                continue
            contributor_sign = positions[contributor]["sign_index"]
            for sign_idx in range(12):  # 0-based: Aries=0, ..., Pisces=11
                relative_house = bv_calculate_relative_house(contributor_sign, sign_idx)
                if relative_house in BINDU_RULES[target][contributor]:
                    bhinnashtakavarga[target][sign_idx] += 1

    return bhinnashtakavarga

def bv_validate_totals(bhinnashtakavarga):
    """Validate Bhinnashtakvarga totals against expected values."""
    errors = []
    for target, expected in EXPECTED_TOTALS.items():
        total = sum(bhinnashtakavarga[target])
        if total != expected:
            errors.append(f"{target}: {total} (expected {expected})")
    if errors:
        raise ValueError("Validation failed: " + "; ".join(errors))

def bv_format_dms(degrees):
    """Format degrees into DMS (degrees, minutes, seconds)."""
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = (degrees - d - m / 60) * 3600
    return f"{d}° {m}' {s:.2f}\""

def get_nakshatra(longitude):
    """Determine the nakshatra based on sidereal longitude."""
    nakshatra_index = int((longitude % 360) / (360 / 27))
    return NAKSHATRAS[nakshatra_index]

def raman_binnastakavargha(birth_date, birth_time, latitude, longitude, tz_offset):
    """Calculate Bhinnashtakavarga and related astrological data."""
    # Calculate Julian Day
    jd = bv_get_julian_day(birth_date, birth_time, tz_offset)
    
    # Calculate Ayanamsa
    ayanamsa = bv_calculate_ayanamsa(jd)
    
    # Calculate planetary positions
    positions = {}
    planet_positions = {}
    for planet in PLANETS:
        lon = bv_calculate_sidereal_longitude(jd, PLANETS[planet])
        sign_idx = bv_get_sign_index(lon)
        positions[planet] = {
            "longitude": lon,
            "sign_index": sign_idx
        }
        sign_deg = lon % 30
        planet_positions[planet] = {
            "sign": SIGNS[sign_idx],
            "degrees": bv_format_dms(sign_deg),
            "nakshatra": get_nakshatra(lon)
        }
    
    # Calculate Ascendant
    asc_lon = bv_calculate_ascendant(jd, latitude, longitude)
    asc_sign = bv_get_sign_index(asc_lon)
    positions["Ascendant"] = {
        "longitude": asc_lon,
        "sign_index": asc_sign
    }
    asc_deg = asc_lon % 30
    ascendant = {
        "sign": SIGNS[asc_sign],
        "degrees": bv_format_dms(asc_deg),
        "nakshatra": get_nakshatra(asc_lon)
    }
    
    # Calculate Bhinnashtakavarga
    bhinnashtakavarga = bv_calculate_bhinnashtakavarga_matrix(positions)
    bv_validate_totals(bhinnashtakavarga)
    
    # Format Bhinnashtakavarga output
    bhinnashtakavarga_output = {
        target: {
            "signs": {SIGNS[i]: bindus[i] for i in range(12)},
            "total_bindus": sum(bindus)
        } for target, bindus in bhinnashtakavarga.items()
    }
    
    # Return the calculated data
    return {
        "planetary_positions": planet_positions,
        "ascendant": ascendant,
        "bhinnashtakavarga": bhinnashtakavarga_output,
        "notes": {
            "ayanamsa": "Lahiri",
            "ayanamsa_value": f"{ayanamsa:.6f}",
            "chart_type": "Rasi",
            "house_system": "Whole Sign"
        }
    }
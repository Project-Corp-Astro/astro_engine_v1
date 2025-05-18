




# # import swisseph as swe
# # from datetime import datetime, timedelta
# # import logging

# # # Set up logging
# # logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# # # Constants
# # ZODIAC_SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
# # PLANETS = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
# # SWE_PLANETS = [swe.SUN, swe.MOON, swe.MARS, swe.MERCURY, swe.JUPITER, swe.VENUS, swe.SATURN]

# # # Bindu allocation rules (1-based house numbers)
# # BINDU_RULES = {
# #     "Sun": {
# #         "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
# #         "Jupiter": [5, 6, 9, 11],
# #         "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
# #         "Sun": [1, 2, 4, 7, 8, 9, 10, 11],
# #         "Venus": [6, 7, 12],
# #         "Mercury": [3, 5, 6, 9, 10, 11, 12],
# #         "Moon": [3, 6, 10, 11],
# #         "Ascendant": [3, 4, 6, 10, 11, 12]
# #     },
# #     "Moon": {
# #         "Saturn": [3, 5, 6, 11],
# #         "Jupiter": [1, 4, 7, 8, 10, 11, 12],
# #         "Mars": [2, 3, 5, 6, 9, 10, 11],
# #         "Sun": [3, 6, 7, 8, 10, 11],
# #         "Venus": [3, 4, 5, 7, 9, 10, 11],
# #         "Mercury": [1, 3, 4, 5, 7, 8, 10, 11],
# #         "Moon": [1, 3, 6, 7, 10, 11],
# #         "Ascendant": [3, 6, 10, 11]
# #     },
# #     "Mars": {
# #         "Saturn": [1, 4, 7, 8, 9, 10, 11],
# #         "Jupiter": [6, 10, 11, 12],
# #         "Mars": [1, 2, 4, 7, 8, 10, 11],
# #         "Sun": [3, 5, 6, 10, 11],
# #         "Venus": [6, 8, 11, 12],
# #         "Mercury": [3, 5, 6, 11],
# #         "Moon": [3, 6, 11],
# #         "Ascendant": [1, 3, 6, 10, 11]
# #     },
# #     "Mercury": {
# #         "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
# #         "Jupiter": [6, 8, 11, 12],
# #         "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
# #         "Sun": [5, 6, 9, 11, 12],
# #         "Venus": [1, 2, 3, 4, 5, 8, 9, 11],
# #         "Mercury": [1, 3, 5, 6, 9, 10, 11, 12],
# #         "Moon": [2, 4, 6, 8, 10, 11],
# #         "Ascendant": [1, 2, 4, 6, 8, 10, 11]
# #     },
# #     "Venus": {
# #         "Saturn": [3, 4, 5, 8, 9, 10, 11],
# #         "Jupiter": [5, 8, 9, 10, 11],
# #         "Mars": [3, 5, 6, 9, 11, 12],
# #         "Sun": [8, 11, 12],
# #         "Venus": [1, 2, 3, 4, 5, 8, 9, 10, 11],
# #         "Mercury": [3, 5, 6, 9, 11],
# #         "Moon": [1, 2, 3, 4, 5, 8, 9, 11, 12],
# #         "Ascendant": [1, 2, 3, 4, 5, 8, 9, 11]
# #     },
# #     "Jupiter": {
# #         "Saturn": [3, 5, 6, 12],
# #         "Jupiter": [1, 2, 3, 4, 7, 8, 10, 11],
# #         "Mars": [1, 2, 4, 7, 8, 10, 11],
# #         "Sun": [1, 2, 3, 4, 7, 8, 9, 10, 11],
# #         "Venus": [2, 5, 6, 9, 10, 11],
# #         "Mercury": [1, 2, 4, 5, 6, 9, 10, 11],
# #         "Moon": [2, 5, 7, 9, 11],
# #         "Ascendant": [1, 2, 4, 5, 6, 7, 9, 10, 11]
# #     },
# #     "Saturn": {
# #         "Saturn": [3, 5, 6, 11],
# #         "Jupiter": [5, 6, 11, 12],
# #         "Mars": [3, 5, 6, 10, 11, 12],
# #         "Sun": [1, 2, 4, 7, 8, 10, 11],
# #         "Venus": [6, 11, 12],
# #         "Mercury": [6, 8, 9, 10, 11, 12],
# #         "Moon": [3, 6, 11],
# #         "Ascendant": [1, 3, 4, 6, 10, 11]
# #     },
# #     "Ascendant": {
# #         "Saturn": [1, 3, 4, 6, 10, 11],
# #         "Jupiter": [1, 2, 4, 5, 6, 7, 9, 10, 11],
# #         "Mars": [1, 3, 6, 10, 11],
# #         "Sun": [3, 4, 6, 10, 11, 12],
# #         "Venus": [1, 2, 3, 4, 5, 8, 9],
# #         "Mercury": [1, 2, 4, 6, 8, 10, 11],
# #         "Moon": [3, 6, 10, 11, 12],
# #         "Ascendant": [3, 6, 10, 11]
# #     }
# # }



# # # Expected bindu totals for validation
# # EXPECTED_TOTALS = {
# #     "Sun": 48, "Moon": 49, "Mars": 39, "Mercury": 54,
# #     "Venus": 52, "Jupiter": 56, "Saturn": 39, "Ascendant": 49
# # }

# # def astro_binna_get_julian_day(birth_date, birth_time, tz_offset):
# #     """Convert birth date and time to Julian Day with timezone adjustment."""
# #     logging.debug(f"Calculating Julian Day for {birth_date} {birth_time} with TZ offset {tz_offset}")
# #     local_dt = datetime.strptime(birth_date + " " + birth_time, "%Y-%m-%d %H:%M:%S")
# #     ut_dt = local_dt - timedelta(hours=tz_offset)
# #     jd = swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, ut_dt.hour + ut_dt.minute / 60.0 + ut_dt.second / 3600.0)
# #     logging.debug(f"Julian Day: {jd}")
# #     return jd

# # def astro_binna_calculate_ascendant(jd, latitude, longitude):
# #     """Calculate sidereal Ascendant longitude using Lahiri Ayanamsa."""
# #     logging.debug(f"Calculating Ascendant for JD: {jd}, Lat: {latitude}, Lon: {longitude}")
# #     swe.set_sid_mode(swe.SIDM_LAHIRI)
# #     houses = swe.houses_ex(jd, latitude, longitude, flags=swe.FLG_SIDEREAL)
# #     asc_lon = houses[0][0]  # Ascendant longitude
# #     logging.debug(f"Ascendant Longitude: {asc_lon}")
# #     return asc_lon

# # def astro_utils_calculate_sidereal_longitude(jd, planet_code):
# #     """Calculate sidereal longitude of a planet using Lahiri Ayanamsa."""
# #     logging.debug(f"Calculating sidereal longitude for planet code: {planet_code}")
# #     swe.set_sid_mode(swe.SIDM_LAHIRI)
# #     pos, _ = swe.calc_ut(jd, planet_code, swe.FLG_SIDEREAL)
# #     longitude = pos[0] % 360
# #     logging.debug(f"Sidereal Longitude: {longitude}")
# #     return longitude

# # def astro_binna_get_sign_index(longitude):
# #     """Determine zodiac sign index (0-based) from longitude."""
# #     sign_index = int(longitude // 30) % 12
# #     logging.debug(f"Longitude {longitude} corresponds to sign index: {sign_index}")
# #     return sign_index

# # def astro_utils_calculate_planet_positions(jd):
# #     """Calculate sidereal positions of planets using Lahiri Ayanamsa."""
# #     logging.debug(f"Calculating planet positions for JD: {jd}")
# #     positions = {}
# #     for planet, code in zip(PLANETS, SWE_PLANETS):
# #         lon = astro_utils_calculate_sidereal_longitude(jd, code)
# #         positions[planet] = {"longitude": lon, "sign_index": astro_utils_get_sign_index(lon)}
# #     return positions

# # def astro_utils_calculate_bhinnashtakavarga(positions):
# #     """Calculate Bhinnashtakavarga matrix with precise bindu assignment."""
# #     contributors = PLANETS + ['Ascendant']
# #     targets = PLANETS + ['Ascendant']
# #     bhinnashtakavarga = {target: [0] * 12 for target in targets}

# #     for target in targets:
# #         for contributor in contributors:
# #             if contributor not in positions:
# #                 continue
# #             contributor_sign = positions[contributor]["sign_index"]
# #             for sign_idx in range(12):  # 0-based: Aries=0, ..., Pisces=11
# #                 relative_house = (sign_idx - contributor_sign) % 12 + 1  # 1-based house
# #                 if relative_house in BINDU_RULES[target][contributor]:
# #                     bhinnashtakavarga[target][sign_idx] += 1

# #     return bhinnashtakavarga

# # def astro_utils_validate_totals(bhinnashtakavarga):
# #     """Validate Bhinnashtakvarga totals against expected values."""
# #     errors = []
# #     for target, expected in EXPECTED_TOTALS.items():
# #         total = sum(bhinnashtakavarga[target])
# #         if total != expected:
# #             errors.append(f"{target}: {total} (expected {expected})")
# #     if errors:
# #         raise ValueError("Validation failed: " + "; ".join(errors))

# # def astro_utils_format_dms(degrees):
# #     """Convert decimal degrees to degrees, minutes, seconds format."""
# #     d = int(degrees)
# #     m = int((degrees - d) * 60)
# #     s = (degrees - d - m / 60.0) * 3600.0
# #     return f"{d}° {abs(m)}' {abs(s):.2f}\""









# import swisseph as swe
# from datetime import datetime, timedelta

# # Constants
# SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
#          "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
# PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
# SWE_PLANETS = [swe.SUN, swe.MOON, swe.MARS, swe.MERCURY, swe.JUPITER, swe.VENUS, swe.SATURN, swe.MEAN_NODE]
# NAKSHATRA_NAMES = [
#     'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
#     'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
#     'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
#     'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta',
#     'Shatabhisha', 'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
# ]
# BINDU_RULES = {
#     "Sun": {
#         "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
#         "Jupiter": [5, 6, 9, 11],
#         "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
#         "Sun": [1, 2, 4, 7, 8, 9, 10, 11],
#         "Venus": [6, 7, 12],
#         "Mercury": [3, 5, 6, 9, 10, 11, 12],
#         "Moon": [3, 6, 10, 11],
#         "Ascendant": [3, 4, 6, 10, 11, 12]
#     },
#     "Moon": {
#         "Saturn": [3, 5, 6, 11],
#         "Jupiter": [1, 4, 7, 8, 10, 11, 12],
#         "Mars": [2, 3, 5, 6, 9, 10, 11],
#         "Sun": [3, 6, 7, 8, 10, 11],
#         "Venus": [3, 4, 5, 7, 9, 10, 11],
#         "Mercury": [1, 3, 4, 5, 7, 8, 10, 11],
#         "Moon": [1, 3, 6, 7, 10, 11],
#         "Ascendant": [3, 6, 10, 11]
#     },
#     "Mars": {
#         "Saturn": [1, 4, 7, 8, 9, 10, 11],
#         "Jupiter": [6, 10, 11, 12],
#         "Mars": [1, 2, 4, 7, 8, 10, 11],
#         "Sun": [3, 5, 6, 10, 11],
#         "Venus": [6, 8, 11, 12],
#         "Mercury": [3, 5, 6, 11],
#         "Moon": [3, 6, 11],
#         "Ascendant": [1, 3, 6, 10, 11]
#     },
#     "Mercury": {
#         "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
#         "Jupiter": [6, 8, 11, 12],
#         "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
#         "Sun": [5, 6, 9, 11, 12],
#         "Venus": [1, 2, 3, 4, 5, 8, 9, 11],
#         "Mercury": [1, 3, 5, 6, 9, 10, 11, 12],
#         "Moon": [2, 4, 6, 8, 10, 11],
#         "Ascendant": [1, 2, 4, 6, 8, 10, 11]
#     },
#     "Venus": {
#         "Saturn": [3, 4, 5, 8, 9, 10, 11],
#         "Jupiter": [5, 8, 9, 10, 11],
#         "Mars": [3, 5, 6, 9, 11, 12],
#         "Sun": [8, 11, 12],
#         "Venus": [1, 2, 3, 4, 5, 8, 9, 10, 11],
#         "Mercury": [3, 5, 6, 9, 11],
#         "Moon": [1, 2, 3, 4, 5, 8, 9, 11, 12],
#         "Ascendant": [1, 2, 3, 4, 5, 8, 9, 11]
#     },
#     "Jupiter": {
#         "Saturn": [3, 5, 6, 12],
#         "Jupiter": [1, 2, 3, 4, 7, 8, 10, 11],
#         "Mars": [1, 2, 4, 7, 8, 10, 11],
#         "Sun": [1, 2, 3, 4, 7, 8, 9, 10, 11],
#         "Venus": [2, 5, 6, 9, 10, 11],
#         "Mercury": [1, 2, 4, 5, 6, 9, 10, 11],
#         "Moon": [2, 5, 7, 9, 11],
#         "Ascendant": [1, 2, 4, 5, 6, 7, 9, 10, 11]
#     },
#     "Saturn": {
#         "Saturn": [3, 5, 6, 11],
#         "Jupiter": [5, 6, 11, 12],
#         "Mars": [3, 5, 6, 10, 11, 12],
#         "Sun": [1, 2, 4, 7, 8, 10, 11],
#         "Venus": [6, 11, 12],
#         "Mercury": [6, 8, 9, 10, 11, 12],
#         "Moon": [3, 6, 11],
#         "Ascendant": [1, 3, 4, 6, 10, 11]
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
# EXPECTED_TOTALS = {
#     "Sun": 48, "Moon": 49, "Mars": 39, "Mercury": 54,
#     "Venus": 52, "Jupiter": 56, "Saturn": 39, "Ascendant": 49
# }

# def bv_get_julian_day(date_str, time_str, tz_offset):
#     """Convert birth date, time, and timezone offset to Julian Day."""
#     local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
#     ut_dt = local_dt - timedelta(hours=tz_offset)
#     hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
#     jd = swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal, swe.GREG_CAL)
#     return jd

# def bv_calculate_ayanamsa(jd):
#     """Calculate Raman Ayanamsa for the given Julian Day."""
#     swe.set_sid_mode(swe.SIDM_RAMAN)
#     ayanamsa = swe.get_ayanamsa_ut(jd)
#     return ayanamsa

# def bv_calculate_sidereal_longitude(jd, planet_code):
#     """Calculate sidereal longitude and retrograde status using Raman Ayanamsa."""
#     swe.set_sid_mode(swe.SIDM_RAMAN)
#     try:
#         pos, ret = swe.calc_ut(jd, planet_code, swe.FLG_SIDEREAL | swe.FLG_SPEED)
#         if ret < 0:
#             raise Exception(f"Error calculating position for planet code {planet_code}")
#         longitude = pos[0] % 360
#         speed = pos[3]
#         retrograde = speed < 0
#         return longitude, retrograde
#     except Exception as e:
#         raise Exception(f"Failed to calculate longitude: {str(e)}")

# def bv_calculate_ascendant(jd, latitude, longitude):
#     """Calculate sidereal Ascendant longitude using Raman Ayanamsa."""
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

# def get_nakshatra_pada(longitude):
#     """Determine nakshatra and pada from sidereal longitude."""
#     longitude = longitude % 360
#     pada_size = 360 / 108  # 3.3333° per pada
#     pada_index = int(longitude / pada_size) % 108
#     nakshatra_index = pada_index // 4
#     pada_number = (pada_index % 4) + 1
#     nakshatra_name = NAKSHATRA_NAMES[nakshatra_index]
#     return nakshatra_name, pada_number

# def bv_calculate_bhinnashtakavarga_matrix(positions):
#     """Calculate Bhinnashtakavarga matrix with bindu counts per sign."""
#     contributors = list(PLANETS) + ["Ascendant"]
#     targets = list(PLANETS) + ["Ascendant"]
#     bhinnashtakavarga = {target: [0] * 12 for target in targets}

#     for target in targets:
#         for contributor in contributors:
#             if contributor not in positions:
#                 continue
#             contributor_sign = positions[contributor]["sign_index"]
#             for sign_idx in range(12):
#                 relative_house = bv_calculate_relative_house(contributor_sign, sign_idx)
#                 if relative_house in BINDU_RULES.get(target, {}).get(contributor, []):
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
#     return True

# def bv_format_dms(degrees):
#     """Format degrees into DMS (degrees, minutes, seconds)."""
#     degrees = degrees % 360
#     d = int(degrees)
#     m = int((degrees - d) * 60)
#     s = (degrees - d - m / 60) * 3600
#     return f"{d}° {m}' {s:.2f}\""

# def raman_bhinnashtakavarga(birth_date, birth_time, latitude, longitude, tz_offset):
#     """Calculate Bhinnashtakavarga with Raman ayanamsa, including tuple format, tables, and validation."""
#     jd = bv_get_julian_day(birth_date, birth_time, tz_offset)
#     ayanamsa = bv_calculate_ayanamsa(jd)

#     # Calculate planetary positions
#     positions = {}
#     for planet in PLANETS:
#         if planet == "Ketu":
#             rahu_lon, rahu_retro = positions["Rahu"]["longitude"], positions["Rahu"]["retrograde"]
#             lon = (rahu_lon + 180) % 360
#             retro = rahu_retro
#         else:
#             code = SWE_PLANETS[PLANETS.index(planet)]
#             lon, retro = bv_calculate_sidereal_longitude(jd, code)
#         sign_idx = bv_get_sign_index(lon)
#         nakshatra, pada = get_nakshatra_pada(lon)
#         positions[planet] = {
#             "longitude": lon,
#             "sign_index": sign_idx,
#             "retrograde": retro,
#             "nakshatra": nakshatra,
#             "pada": pada
#         }

#     # Calculate Ascendant
#     asc_lon = bv_calculate_ascendant(jd, latitude, longitude)
#     asc_sign_idx = bv_get_sign_index(asc_lon)
#     asc_nakshatra, asc_pada = get_nakshatra_pada(asc_lon)
#     positions["Ascendant"] = {
#         "longitude": asc_lon,
#         "sign_index": asc_sign_idx,
#         "nakshatra": asc_nakshatra,
#         "pada": asc_pada
#     }

#     # Calculate Bhinnashtakavarga
#     bhinnashtakavarga = bv_calculate_bhinnashtakavarga_matrix(positions)
#     bv_validate_totals(bhinnashtakavarga)

#     # Format planetary positions
#     planetary_positions = {}
#     for planet in PLANETS:
#         data = positions[planet]
#         sign_deg = data["longitude"] % 30
#         planetary_positions[planet] = {
#             "sign": SIGNS[data["sign_index"]],
#             "degrees": bv_format_dms(sign_deg),
#             "retrograde": data["retrograde"],
#             "nakshatra": data["nakshatra"],
#             "pada": data["pada"]
#         }

#     asc_data = positions["Ascendant"]
#     asc_deg = asc_data["longitude"] % 30
#     ascendant = {
#         "sign": SIGNS[asc_data["sign_index"]],
#         "degrees": bv_format_dms(asc_deg),
#         "nakshatra": asc_data["nakshatra"],
#         "pada": asc_data["pada"]
#     }

#     # Bhinnashtakavarga output with tables, tuple format, and totals
#     bhinnashtakavarga_output = {}
#     for target, bindus in bhinnashtakavarga.items():
#         bindu_presence = tuple(1 if b > 0 else 0 for b in bindus)  # Tuple of 0s and 1s
#         total_bindus = sum(bindus)
#         table = dict(zip(SIGNS, bindus))  # Table with sign-wise bindu counts
#         bhinnashtakavarga_output[target] = {
#             "bindu_presence": bindu_presence,
#             "table": table,
#             "total_bindus": total_bindus,
#             "valid": total_bindus == EXPECTED_TOTALS[target]  # Exact validation
#         }

#     return {
#         "planetary_positions": planetary_positions,
#         "ascendant": ascendant,
#         "bhinnashtakavarga": bhinnashtakavarga_output,
#         "ayanamsa": ayanamsa
#     }









import swisseph as swe
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Constants
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
SWE_PLANETS = [swe.SUN, swe.MOON, swe.MARS, swe.MERCURY, swe.JUPITER, swe.VENUS, swe.SATURN]

# Nakshatras and their spans (simplified for demonstration)
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu",
    "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta",
    "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati"
]

def bv_get_julian_day(birth_date, birth_time, tz_offset):
    """Convert birth date and time to Julian day."""
    dt = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M:%S")
    dt -= timedelta(hours=tz_offset)
    return swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60 + dt.second / 3600)

def bv_calculate_ayanamsa(jd):
    """Calculate Raman ayanamsa for the given Julian day."""
    swe.set_sid_mode(swe.SIDM_RAMAN)
    return swe.get_ayanamsa(jd)

def bv_calculate_sidereal_longitude(jd, planet):
    """Calculate sidereal longitude and retrograde status of a planet."""
    lon, lat, dist, lon_speed, lat_speed, dist_speed = swe.calc_ut(jd, planet, swe.FLG_SWIEPH + swe.FLG_SIDEREAL)
    return lon[0], lon_speed[0] < 0

def bv_get_sign_index(longitude):
    """Get the sign index (0-11) from longitude."""
    return int(longitude // 30) % 12

def get_nakshatra_pada(longitude):
    """Calculate Nakshatra and Pada from longitude."""
    nak_span = 13 + 20 / 60  # 13 degrees 20 minutes per nakshatra
    nak_idx = int(longitude // nak_span) % 27
    pada = int((longitude % nak_span) // (nak_span / 4)) + 1
    return NAKSHATRAS[nak_idx], pada

def bv_calculate_ascendant(jd, latitude, longitude):
    """Calculate the Ascendant longitude."""
    swe.set_sid_mode(swe.SIDM_RAMAN)
    cusps, ascmc = swe.houses(jd, latitude, longitude, b'W')  # Whole Sign houses
    return ascmc[0]  # Ascendant longitude

def bv_format_dms(degrees):
    """Format degrees into degrees, minutes, seconds."""
    deg = int(degrees)
    minutes = int((degrees - deg) * 60)
    seconds = int(((degrees - deg) * 60 - minutes) * 60)
    return f"{deg}° {minutes}' {seconds}\""

def bv_calculate_bhinnashtakavarga_matrix(positions):
    """Simplified Bhinnashtakavarga calculation (placeholder)."""
    # Placeholder logic: Assign 1 bindu to each planet's sign for demonstration
    matrix = {planet: [0] * 12 for planet in PLANETS}
    for planet, data in positions.items():
        if planet != "Ascendant":
            sign_idx = data["sign_index"]
            matrix[planet][sign_idx] = 1
    return matrix

def bv_validate_totals(bhinnashtakavarga):
    """Validate Bhinnashtakavarga totals (placeholder)."""
    for planet, bindus in bhinnashtakavarga.items():
        total = sum(bindus)
        logger.debug(f"{planet} total bindus: {total}")

def raman_bhinnashtakavarga(birth_date, birth_time, latitude, longitude, tz_offset):
    """Calculate Bhinnashtakavarga with Raman ayanamsa."""
    try:
        # Calculate Julian day and ayanamsa
        jd = bv_get_julian_day(birth_date, birth_time, tz_offset)
        ayanamsa = bv_calculate_ayanamsa(jd)
        logger.debug(f"Julian Day: {jd}, Ayanamsa: {ayanamsa}")

        # Calculate planetary positions
        planetary_positions = {}
        positions = {}
        for planet, swe_planet in zip(PLANETS, SWE_PLANETS):
            try:
                lon, retrograde = bv_calculate_sidereal_longitude(jd, swe_planet)
                sign_idx = bv_get_sign_index(lon)
                nakshatra, pada = get_nakshatra_pada(lon)
                sign_deg = lon % 30
                planetary_positions[planet] = {
                    "sign": SIGNS[sign_idx],
                    "degrees": bv_format_dms(sign_deg),
                    "retrograde": retrograde,
                    "nakshatra": nakshatra,
                    "pada": pada
                }
                positions[planet] = {
                    "longitude": lon,
                    "sign_index": sign_idx,
                    "retrograde": retrograde,
                    "nakshatra": nakshatra,
                    "pada": pada
                }
            except Exception as e:
                logger.error(f"Failed to calculate position for {planet}: {str(e)}")
                raise

        # Calculate Ascendant
        asc_lon = bv_calculate_ascendant(jd, latitude, longitude)
        asc_sign_idx = bv_get_sign_index(asc_lon)
        asc_nakshatra, asc_pada = get_nakshatra_pada(asc_lon)
        asc_deg = asc_lon % 30
        ascendant = {
            "sign": SIGNS[asc_sign_idx],
            "degrees": bv_format_dms(asc_deg),
            "nakshatra": asc_nakshatra,
            "pada": asc_pada
        }
        positions["Ascendant"] = {
            "longitude": asc_lon,
            "sign_index": asc_sign_idx,
            "nakshatra": asc_nakshatra,
            "pada": asc_pada
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

        return {
            "planetary_positions": planetary_positions,
            "ascendant": ascendant,
            "bhinnashtakavarga": bhinnashtakavarga_output,
            "ayanamsa": ayanamsa
        }

    except Exception as e:
        logger.error(f"Error in raman_bhinnashtakavarga: {str(e)}")
        raise Exception(f"Calculation failed: {str(e)}")
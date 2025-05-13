# import swisseph as swe
# from datetime import datetime, timedelta

# # Constants
# SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
# PLANET_IDS = {
#     'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS, 'Mercury': swe.MERCURY,
#     'Jupiter': swe.JUPITER, 'Venus': swe.VENUS, 'Saturn': swe.SATURN,
#     'Rahu': swe.MEAN_NODE, 'Ketu': None  # Ketu calculated from Rahu
# }

# def get_julian_day(date_str, time_str, tz_offset):
#     """Convert local date and time to Julian Day (UT)."""
#     try:
#         dt = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M:%S')
#         ut_dt = dt - timedelta(hours=tz_offset)
#         jd = swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, ut_dt.hour + ut_dt.minute / 60.0 + ut_dt.second / 3600.0)
#         return jd
#     except ValueError as e:
#         raise ValueError(f"Invalid date or time format: {str(e)}")

# def calculate_sunrise(jd, lat, lon, tz_offset):
#     """Calculate sunrise time and Sun's longitude at sunrise with fallback."""
#     if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
#         raise ValueError(f"Invalid coordinates: lat={lat}, lon={lon}")

#     geopos = [lon, lat, 0.0]  # [longitude, latitude, elevation]
#     flags = swe.CALC_RISE | swe.BIT_DISC_CENTER | swe.BIT_NO_REFRACTION

#     # Try sunrise calculation for ±3 days
#     for offset in range(-3, 4):
#         search_jd = jd + offset
#         try:
#             ret, t_rise = swe.rise_trans(search_jd - 1.0, swe.SUN, geopos, flags=flags)
#             if ret == 0 and t_rise[0] is not None:
#                 sunrise_jd = t_rise[0]
#                 sun_lon = swe.calc_ut(sunrise_jd, swe.SUN, swe.FLG_SIDEREAL)[0][0] % 360
#                 return sunrise_jd, sun_lon
#         except Exception:
#             pass  # Continue to next offset

#     # Fallback: Approximate sunrise as 6 AM local time
#     try:
#         dt = datetime.strptime(f"{jd_to_date(jd)} 06:00:00", '%Y-%m-%d %H:%M:%S')
#         sunrise_jd = swe.julday(dt.year, dt.month, dt.day, 6.0 - tz_offset)
#         sun_lon = swe.calc_ut(sunrise_jd, swe.SUN, swe.FLG_SIDEREAL)[0][0] % 360
#         return sunrise_jd, sun_lon
#     except Exception as e:
#         raise ValueError(f"Unable to calculate sunrise time after multiple attempts: {str(e)}")

# def calculate_bhava_lagna(birth_jd, sunrise_jd, sunrise_sun_lon):
#     """Calculate Bhava Lagna longitude."""
#     time_elapsed = (birth_jd - sunrise_jd) * 1440  # Convert days to minutes
#     if time_elapsed < 0:
#         time_elapsed += 1440  # Adjust for birth before sunrise
#     degrees_progressed = time_elapsed / 4.0  # 1° per 4 minutes
#     bl_lon = (sunrise_sun_lon + degrees_progressed) % 360
#     return bl_lon

# def get_sign_and_degrees(longitude):
#     """Convert longitude to sign and degrees."""
#     sign_index = int(longitude // 30)
#     degrees = longitude % 30
#     return SIGNS[sign_index % 12], degrees

# def calculate_house(planet_sign, bl_sign):
#     """Assign house using Whole Sign system."""
#     planet_index = SIGNS.index(planet_sign)
#     bl_index = SIGNS.index(bl_sign)
#     return (planet_index - bl_index) % 12 + 1

# def jd_to_date(jd):
#     """Convert Julian Day to date string (YYYY-MM-DD)."""
#     y, m, d, _ = swe.revjul(jd)
#     return f"{y:04d}-{m:02d}-{d:02d}"










import swisseph as swe
from datetime import datetime, timedelta

ZODIAC_SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

PLANETS = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS, 'Mercury': swe.MERCURY,
    'Jupiter': swe.JUPITER, 'Venus': swe.VENUS, 'Saturn': swe.SATURN,
    'Rahu': swe.MEAN_NODE, 'Ketu': 'Ketu'
}

NAKSHATRAS = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
    'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
    'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
    'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta',
    'Shatabhisha', 'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
]

def bava_local_to_ut(date_str, time_str, tz_offset):
    local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    ut_dt = local_dt - timedelta(hours=tz_offset)
    return ut_dt

def bava_get_julian_day(dt):
    jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0 + dt.second / 3600.0)
    return jd

def bava_calculate_lahiri_ayanamsa(jd):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa = swe.get_ayanamsa_ut(jd)
    return ayanamsa

def bava_calculate_ascendant(jd, latitude, longitude):
    house_cusps, asc_mc = swe.houses_ex(jd, latitude, longitude, hsys=b'W')
    tropical_asc = asc_mc[0]
    ayanamsa = bava_calculate_lahiri_ayanamsa(jd)
    sidereal_asc = (tropical_asc - ayanamsa) % 360
    return sidereal_asc

def bava_calculate_nakshatra(longitude):
    nakshatra_size = 13.333333  # 360° / 27 nakshatras
    nakshatra_index = int(longitude / nakshatra_size)
    return NAKSHATRAS[nakshatra_index % 27]

def bava_calculate_planetary_positions(jd, ayanamsa):
    positions = {}
    for planet, code in PLANETS.items():
        if planet == 'Ketu':
            rahu_lon = positions['Rahu']['longitude']
            positions['Ketu'] = {'longitude': (rahu_lon + 180) % 360, 'retrograde': False}
        else:
            tropical_data = swe.calc_ut(jd, code)
            tropical_lon = tropical_data[0][0]
            sidereal_lon = (tropical_lon - ayanamsa) % 360
            retrograde = tropical_data[0][3] < 0  # Speed < 0 indicates retrograde
            positions[planet] = {'longitude': sidereal_lon, 'retrograde': retrograde}
    return positions

def bava_format_dms(degrees):
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = ((degrees - d) * 60 - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def bava_assign_planets_to_houses(planetary_positions, ascendant):
    asc_sign_index = int(ascendant // 30)
    houses = {i: [] for i in range(1, 13)}
    for planet, data in planetary_positions.items():
        lon = data['longitude']
        planet_sign_index = int(lon // 30)
        house = (planet_sign_index - asc_sign_index) % 12 + 1
        degrees_in_sign = lon % 30
        nakshatra = bava_calculate_nakshatra(lon)
        houses[house].append({
            'planet': planet,
            'sign': ZODIAC_SIGNS[planet_sign_index],
            'degrees': degrees_in_sign,
            'degrees_dms': bava_format_dms(degrees_in_sign),
            'retrograde': data['retrograde'],
            'nakshatra': nakshatra
        })
    return houses

def bava_calculate_bhava_lagna(date_str, time_str, latitude, longitude, tz_offset):
    ut_dt = bava_local_to_ut(date_str, time_str, tz_offset)
    jd = bava_get_julian_day(ut_dt)
    ayanamsa = bava_calculate_lahiri_ayanamsa(jd)
    bhava_lagna = bava_calculate_ascendant(jd, latitude, longitude)
    bhava_lagna_sign = ZODIAC_SIGNS[int(bhava_lagna // 30)]
    bhava_lagna_degrees = bhava_lagna % 30
    planetary_positions = bava_calculate_planetary_positions(jd, ayanamsa)
    houses_with_planets = bava_assign_planets_to_houses(planetary_positions, bhava_lagna)
    return {
        "bhava_lagna": {
            "sign": bhava_lagna_sign,
            "degrees": bava_format_dms(bhava_lagna_degrees),
            "nakshatra": bava_calculate_nakshatra(bhava_lagna)
        },
        "planets_in_houses": {
            f"House {house}": [
                {
                    "planet": planet_info['planet'],
                    "sign": planet_info['sign'],
                    "degrees": planet_info['degrees_dms'],
                    "retrograde": planet_info['retrograde'],
                    "nakshatra": planet_info['nakshatra']
                } for planet_info in planets
            ] for house, planets in houses_with_planets.items()
        }
    }
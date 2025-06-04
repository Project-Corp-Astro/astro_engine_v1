# import swisseph as swe
# from datetime import datetime, timedelta

# ZODIAC_SIGNS = [
#     'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
#     'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
# ]

# PLANETS = {
#     'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS, 'Mercury': swe.MERCURY,
#     'Jupiter': swe.JUPITER, 'Venus': swe.VENUS, 'Saturn': swe.SATURN,
#     'Rahu': swe.MEAN_NODE, 'Ketu': 'Ketu'
# }

# NAKSHATRAS = [
#     'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
#     'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
#     'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
#     'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta',
#     'Shatabhisha', 'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
# ]

# def local_to_ut(date_str, time_str, tz_offset):
#     local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
#     ut_dt = local_dt - timedelta(hours=tz_offset)
#     return ut_dt

# def get_julian_day(dt):
#     jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0 + dt.second / 3600.0)
#     return jd

# def calculate_lahiri_ayanamsa(jd):
#     swe.set_sid_mode(swe.SIDM_RAMAN)
#     ayanamsa = swe.get_ayanamsa_ut(jd)
#     return ayanamsa

# def calculate_ascendant(jd, latitude, longitude):
#     house_cusps, asc_mc = swe.houses_ex(jd, latitude, longitude, hsys=b'W')
#     tropical_asc = asc_mc[0]
#     ayanamsa = calculate_lahiri_ayanamsa(jd)
#     sidereal_asc = (tropical_asc - ayanamsa) % 360
#     return sidereal_asc

# def calculate_planetary_positions(jd, ayanamsa):
#     positions = {}
#     for planet, code in PLANETS.items():
#         if planet == 'Ketu':
#             rahu_lon = positions['Rahu']
#             positions['Ketu'] = (rahu_lon + 180) % 360
#         else:
#             tropical_lon = swe.calc_ut(jd, code)[0][0]
#             sidereal_lon = (tropical_lon - ayanamsa) % 360
#             positions[planet] = sidereal_lon
#     return positions

# def assign_planets_to_houses(planetary_positions, ascendant):
#     asc_sign_index = int(ascendant // 30)
#     houses = {i: [] for i in range(1, 13)}
#     for planet, lon in planetary_positions.items():
#         planet_sign_index = int(lon // 30)
#         house = (planet_sign_index - asc_sign_index) % 12 + 1
#         degrees_in_sign = lon % 30
#         nakshatra = get_nakshatra(lon)
#         houses[house].append({
#             'planet': planet,
#             'sign': ZODIAC_SIGNS[planet_sign_index],
#             'degrees': degrees_in_sign,
#             'degrees_dms': format_dms(degrees_in_sign),
#             'nakshatra': nakshatra
#         })
#     return houses

# def format_dms(degrees):
#     d = int(degrees)
#     m = int((degrees - d) * 60)
#     s = ((degrees - d) * 60 - m) * 60
#     return f"{d}° {m}' {s:.2f}\""

# def get_nakshatra(longitude):
#     nakshatra_index = int((longitude % 360) / (360 / 27))
#     return NAKSHATRAS[nakshatra_index]

# def raman_bava_lagna(birth_date, birth_time, latitude, longitude, timezone_offset, user_name='Unknown'):
#     ut_dt = local_to_ut(birth_date, birth_time, timezone_offset)
#     jd = get_julian_day(ut_dt)
#     ayanamsa = calculate_lahiri_ayanamsa(jd)
#     bhava_lagna = calculate_ascendant(jd, latitude, longitude)
#     bhava_lagna_sign = ZODIAC_SIGNS[int(bhava_lagna // 30)]
#     bhava_lagna_degrees = bhava_lagna % 30
#     bhava_lagna_nakshatra = get_nakshatra(bhava_lagna)
#     planetary_positions = calculate_planetary_positions(jd, ayanamsa)
#     houses_with_planets = assign_planets_to_houses(planetary_positions, bhava_lagna)
#     response = {
#         "user_name": user_name,
#         "bhava_lagna": {
#             "sign": bhava_lagna_sign,
#             "degrees": format_dms(bhava_lagna_degrees),
#             "nakshatra": bhava_lagna_nakshatra
#         },
#         "planets_in_houses": {
#             f"House {house}": [
#                 {
#                     "planet": planet_info['planet'],
#                     "sign": planet_info['sign'],
#                     "degrees": planet_info['degrees_dms'],
#                     "nakshatra": planet_info['nakshatra']
#                 } for planet_info in planets
#             ] for house, planets in houses_with_planets.items()
#         },
#         "metadata": {
#             "ayanamsa": "Lahiri",
#             "house_system": "Whole Sign",
#             "calculation_time": datetime.utcnow().isoformat()
#         }
#     }
#     return response





import swisseph as swe
from datetime import datetime, timedelta

SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
PLANET_IDS = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS, 'Mercury': swe.MERCURY,
    'Jupiter': swe.JUPITER, 'Venus': swe.VENUS, 'Saturn': swe.SATURN,
    'Rahu': swe.MEAN_NODE, 'Ketu': None  # Ketu will be handled separately
}
NAKSHATRAS = [
    ("Ashwini", "Ketu"), ("Bharani", "Venus"), ("Krittika", "Sun"),
    ("Rohini", "Moon"), ("Mrigashira", "Mars"), ("Ardra", "Rahu"),
    ("Punarvasu", "Jupiter"), ("Pushya", "Saturn"), ("Ashlesha", "Mercury"),
    ("Magha", "Ketu"), ("Purva Phalguni", "Venus"), ("Uttara Phalguni", "Sun"),
    ("Hasta", "Moon"), ("Chitra", "Mars"), ("Swati", "Rahu"),
    ("Vishakha", "Jupiter"), ("Anuradha", "Saturn"), ("Jyeshtha", "Mercury"),
    ("Mula", "Ketu"), ("Purva Ashadha", "Venus"), ("Uttara Ashadha", "Sun"),
    ("Shravana", "Moon"), ("Dhanishta", "Mars"), ("Shatabhisha", "Rahu"),
    ("Purva Bhadrapada", "Jupiter"), ("Uttara Bhadrapada", "Saturn"), ("Revati", "Mercury"),
]
NAK_LEN = 13 + 1/3  # 13.33333°
PADA_LEN = NAK_LEN / 4  # 3.33333°

def raman_bava_get_julian_day(date_str, time_str, tz_offset):
    dt = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M:%S')
    ut_dt = dt - timedelta(hours=tz_offset)
    return swe.julday(
        ut_dt.year, ut_dt.month, ut_dt.day, 
        ut_dt.hour + ut_dt.minute / 60.0 + ut_dt.second / 3600.0
    )

def raman_bava_calculate_sunrise(jd, lat, lon, tz_offset):
    geopos = [lon, lat, 0.0]
    flags = swe.CALC_RISE | swe.BIT_DISC_CENTER | swe.BIT_NO_REFRACTION
    for offset in range(-3, 4):
        search_jd = jd + offset
        try:
            ret, t_rise = swe.rise_trans(search_jd - 1.0, swe.SUN, geopos, flags=flags)
            if ret == 0 and t_rise[0] is not None:
                sunrise_jd = t_rise[0]
                sun_lon = swe.calc_ut(sunrise_jd, swe.SUN, swe.FLG_SIDEREAL)[0][0] % 360
                return sunrise_jd, sun_lon
        except Exception:
            continue
    # Fallback: 6 AM local time
    dt = datetime.strptime(f"{raman_bava_jd_to_date(jd)} 06:00:00", '%Y-%m-%d %H:%M:%S')
    sunrise_jd = swe.julday(dt.year, dt.month, dt.day, 6.0 - tz_offset)
    sun_lon = swe.calc_ut(sunrise_jd, swe.SUN, swe.FLG_SIDEREAL)[0][0] % 360
    return sunrise_jd, sun_lon

def raman_bava_calculate_bhava_lagna(birth_jd, sunrise_jd, sunrise_sun_lon):
    time_elapsed = (birth_jd - sunrise_jd) * 1440
    if time_elapsed < 0:
        time_elapsed += 1440
    degrees_progressed = time_elapsed / 4.0
    bl_lon = (sunrise_sun_lon + degrees_progressed) % 360
    return bl_lon

def raman_bava_get_sign_and_degrees(longitude):
    sign_index = int(longitude // 30)
    degrees = longitude % 30
    return SIGNS[sign_index % 12], degrees

def raman_bava_calculate_house(planet_sign, bl_sign):
    planet_index = SIGNS.index(planet_sign)
    bl_index = SIGNS.index(bl_sign)
    return (planet_index - bl_index) % 12 + 1

def raman_bava_jd_to_date(jd):
    y, m, d, _ = swe.revjul(jd)
    return f"{y:04d}-{m:02d}-{d:02d}"

def raman_bava_nakshatra_and_pada(lon):
    nak_num = int(lon // NAK_LEN)
    nak_deg = lon - nak_num * NAK_LEN
    pada_num = int(nak_deg // PADA_LEN) + 1  # Pada 1-4
    nak_name, nak_lord = NAKSHATRAS[nak_num % 27]
    return nak_name, nak_lord, pada_num










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

# def bava_local_to_ut(date_str, time_str, tz_offset):
#     local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
#     ut_dt = local_dt - timedelta(hours=tz_offset)
#     return ut_dt

# def bava_get_julian_day(dt):
#     jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0 + dt.second / 3600.0)
#     return jd

# def bava_calculate_lahiri_ayanamsa(jd):
#     swe.set_sid_mode(swe.SIDM_LAHIRI)
#     ayanamsa = swe.get_ayanamsa_ut(jd)
#     return ayanamsa

# def bava_calculate_ascendant(jd, latitude, longitude):
#     house_cusps, asc_mc = swe.houses_ex(jd, latitude, longitude, hsys=b'W')
#     tropical_asc = asc_mc[0]
#     ayanamsa = bava_calculate_lahiri_ayanamsa(jd)
#     sidereal_asc = (tropical_asc - ayanamsa) % 360
#     return sidereal_asc

# def bava_calculate_nakshatra(longitude):
#     nakshatra_size = 13.333333  # 360° / 27 nakshatras
#     nakshatra_index = int(longitude / nakshatra_size)
#     return NAKSHATRAS[nakshatra_index % 27]

# def bava_calculate_planetary_positions(jd, ayanamsa):
#     positions = {}
#     for planet, code in PLANETS.items():
#         if planet == 'Ketu':
#             rahu_lon = positions['Rahu']['longitude']
#             positions['Ketu'] = {'longitude': (rahu_lon + 180) % 360, 'retrograde': False}
#         else:
#             tropical_data = swe.calc_ut(jd, code)
#             tropical_lon = tropical_data[0][0]
#             sidereal_lon = (tropical_lon - ayanamsa) % 360
#             retrograde = tropical_data[0][3] < 0  # Speed < 0 indicates retrograde
#             positions[planet] = {'longitude': sidereal_lon, 'retrograde': retrograde}
#     return positions

# def bava_format_dms(degrees):
#     d = int(degrees)
#     m = int((degrees - d) * 60)
#     s = ((degrees - d) * 60 - m) * 60
#     return f"{d}° {m}' {s:.2f}\""

# def bava_assign_planets_to_houses(planetary_positions, ascendant):
#     asc_sign_index = int(ascendant // 30)
#     houses = {i: [] for i in range(1, 13)}
#     for planet, data in planetary_positions.items():
#         lon = data['longitude']
#         planet_sign_index = int(lon // 30)
#         house = (planet_sign_index - asc_sign_index) % 12 + 1
#         degrees_in_sign = lon % 30
#         nakshatra = bava_calculate_nakshatra(lon)
#         houses[house].append({
#             'planet': planet,
#             'sign': ZODIAC_SIGNS[planet_sign_index],
#             'degrees': degrees_in_sign,
#             'degrees_dms': bava_format_dms(degrees_in_sign),
#             'retrograde': data['retrograde'],
#             'nakshatra': nakshatra
#         })
#     return houses

# def bava_calculate_bhava_lagna(date_str, time_str, latitude, longitude, tz_offset):
#     ut_dt = bava_local_to_ut(date_str, time_str, tz_offset)
#     jd = bava_get_julian_day(ut_dt)
#     ayanamsa = bava_calculate_lahiri_ayanamsa(jd)
#     bhava_lagna = bava_calculate_ascendant(jd, latitude, longitude)
#     bhava_lagna_sign = ZODIAC_SIGNS[int(bhava_lagna // 30)]
#     bhava_lagna_degrees = bhava_lagna % 30
#     planetary_positions = bava_calculate_planetary_positions(jd, ayanamsa)
#     houses_with_planets = bava_assign_planets_to_houses(planetary_positions, bhava_lagna)
#     return {
#         "bhava_lagna": {
#             "sign": bhava_lagna_sign,
#             "degrees": bava_format_dms(bhava_lagna_degrees),
#             "nakshatra": bava_calculate_nakshatra(bhava_lagna)
#         },
#         "planets_in_houses": {
#             f"House {house}": [
#                 {
#                     "planet": planet_info['planet'],
#                     "sign": planet_info['sign'],
#                     "degrees": planet_info['degrees_dms'],
#                     "retrograde": planet_info['retrograde'],
#                     "nakshatra": planet_info['nakshatra']
#                 } for planet_info in planets
#             ] for house, planets in houses_with_planets.items()
#         }
#     }









import swisseph as swe
from datetime import datetime, timedelta
import math

# Constants
ZODIAC_SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

PLANETS = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS, 'Mercury': swe.MERCURY,
    'Jupiter': swe.JUPITER, 'Venus': swe.VENUS, 'Saturn': swe.SATURN,
    'Rahu': swe.MEAN_NODE, 'Ketu': 'Ketu'  # Ketu is handled separately
}

NAKSHATRAS = [
    ('Ashwini', 0), ('Bharani', 13.3333), ('Krittika', 26.6667), ('Rohini', 40),
    ('Mrigashira', 53.3333), ('Ardra', 66.6667), ('Punarvasu', 80), ('Pushya', 93.3333),
    ('Ashlesha', 106.6667), ('Magha', 120), ('Purva Phalguni', 133.3333), ('Uttara Phalguni', 146.6667),
    ('Hasta', 160), ('Chitra', 173.3333), ('Swati', 186.6667), ('Vishakha', 200),
    ('Anuradha', 213.3333), ('Jyeshtha', 226.6667), ('Mula', 240), ('Purva Ashadha', 253.3333),
    ('Uttara Ashadha', 266.6667), ('Shravana', 280), ('Dhanishta', 293.3333), ('Shatabhisha', 306.6667),
    ('Purva Bhadrapada', 320), ('Uttara Bhadrapada', 333.3333), ('Revati', 346.6667)
]

def local_to_ut(date_str, time_str, tz_offset):
    local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    ut_dt = local_dt - timedelta(hours=tz_offset)
    return ut_dt

def get_julian_day(dt):
    jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0 + dt.second / 3600.0)
    return jd

def calculate_lahiri_ayanamsa(jd):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa = swe.get_ayanamsa_ut(jd)
    return ayanamsa

def calculate_ascendant(jd, latitude, longitude):
    house_cusps, asc_mc = swe.houses_ex(jd, latitude, longitude, hsys=b'W')
    tropical_asc = asc_mc[0]
    ayanamsa = calculate_lahiri_ayanamsa(jd)
    sidereal_asc = (tropical_asc - ayanamsa) % 360
    return sidereal_asc

def calculate_planetary_positions(jd, ayanamsa):
    positions = {}
    for planet, code in PLANETS.items():
        if planet == 'Ketu':
            rahu_lon = positions['Rahu']
            positions['Ketu'] = (rahu_lon + 180) % 360
        else:
            tropical_lon = swe.calc_ut(jd, code)[0][0]
            sidereal_lon = (tropical_lon - ayanamsa) % 360
            positions[planet] = sidereal_lon
    return positions

def get_retrograde_status(jd, planet):
    if planet in ['Sun', 'Moon', 'Rahu', 'Ketu']:
        return ''  # These planets don't have retrograde motion
    pos = swe.calc_ut(jd, PLANETS[planet])[0]
    speed = pos[3]  # Speed in longitude
    return 'R' if speed < 0 else ''

def get_nakshatra_and_pada(longitude):
    longitude = longitude % 360
    for nakshatra, start in NAKSHATRAS:
        end = start + 13.3333
        if start <= longitude < end:
            nakshatra_name = nakshatra
            pada = int((longitude - start) / 3.3333) + 1
            return nakshatra_name, pada
    return "Revati", 4  # Fallback for edge case

def assign_planets_to_houses(planetary_positions, ascendant, jd):
    asc_sign_index = int(ascendant // 30)
    houses = {i: [] for i in range(1, 13)}
    for planet, lon in planetary_positions.items():
        planet_sign_index = int(lon // 30)
        house = (planet_sign_index - asc_sign_index) % 12 + 1
        degrees_in_sign = lon % 30
        retrograde = get_retrograde_status(jd, planet)
        nakshatra, pada = get_nakshatra_and_pada(lon)
        houses[house].append({
            'planet': planet,
            'sign': ZODIAC_SIGNS[planet_sign_index],
            'degrees': degrees_in_sign,
            'degrees_dms': format_dms(degrees_in_sign),
            'retrograde': retrograde,
            'nakshatra': nakshatra,
            'pada': pada
        })
    return houses

def format_dms(degrees):
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = ((degrees - d) * 60 - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def lahairi_bava_lagan(birth_date, birth_time, latitude, longitude, timezone_offset):
    ut_dt = local_to_ut(birth_date, birth_time, timezone_offset)
    jd = get_julian_day(ut_dt)
    ayanamsa = calculate_lahiri_ayanamsa(jd)

    bhava_lagna = calculate_ascendant(jd, latitude, longitude)
    bhava_lagna_sign = ZODIAC_SIGNS[int(bhava_lagna // 30)]
    bhava_lagna_degrees = bhava_lagna % 30
    bhava_lagna_nakshatra, bhava_lagna_pada = get_nakshatra_and_pada(bhava_lagna)

    planetary_positions = calculate_planetary_positions(jd, ayanamsa)
    houses_with_planets = assign_planets_to_houses(planetary_positions, bhava_lagna, jd)

    response = {
        "bhava_lagna": {
            "sign": bhava_lagna_sign,
            "degrees": format_dms(bhava_lagna_degrees),
            "nakshatra": bhava_lagna_nakshatra,
            "pada": bhava_lagna_pada
        },
        "planets_in_houses": {
            f"House {house}": [
                {
                    "planet": planet_info['planet'],
                    "sign": planet_info['sign'],
                    "degrees": planet_info['degrees_dms'],
                    "retrograde": planet_info['retrograde'],
                    "nakshatra": planet_info['nakshatra'],
                    "pada": planet_info['pada']
                } for planet_info in planets
            ] for house, planets in houses_with_planets.items()
        },
        "metadata": {
            "ayanamsa": "Lahiri",
            "house_system": "Whole Sign",
            "calculation_time": datetime.utcnow().isoformat()
        }
    }
    return response
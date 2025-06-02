import swisseph as swe
from datetime import datetime, timedelta

SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

ODD_SIGN_D30_RANGES = [
    (0, 5, 'Aries'),
    (5, 10, 'Aquarius'),
    (10, 18, 'Sagittarius'),
    (18, 25, 'Gemini'),
    (25, 30, 'Libra')
]

EVEN_SIGN_D30_RANGES = [
    (0, 5, 'Taurus'),
    (5, 12, 'Virgo'),
    (12, 20, 'Pisces'),
    (20, 25, 'Capricorn'),
    (25, 30, 'Scorpio')
]

NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashirsha", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]
NAKSHATRA_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"
]

def raman_d30_get_julian_day(date_str, time_str, tz_offset):
    local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    ut_dt = local_dt - timedelta(hours=tz_offset)
    hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
    return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal, swe.GREG_CAL)

def raman_d30_calculate_sidereal_longitudes(jd, latitude, longitude):
    swe.set_sid_mode(swe.SIDM_RAMAN)
    planets = {
        'Sun': swe.SUN, 'Moon': swe.MOON, 'Mercury': swe.MERCURY, 'Venus': swe.VENUS,
        'Mars': swe.MARS, 'Jupiter': swe.JUPITER, 'Saturn': swe.SATURN,
        'Rahu': swe.MEAN_NODE
    }
    positions = {}
    for planet, code in planets.items():
        pos = swe.calc_ut(jd, code, swe.FLG_SIDEREAL | swe.FLG_SPEED)
        lon = pos[0][0] % 360
        speed = pos[0][3] if len(pos[0]) > 3 else 0
        retro = speed < 0 if planet not in ['Rahu'] else True
        positions[planet] = {'longitude': lon, 'retrograde': retro}
    rahu_lon = positions['Rahu']['longitude']
    positions['Ketu'] = {'longitude': (rahu_lon + 180) % 360, 'retrograde': True}
    cusps, ascmc = swe.houses_ex(jd, float(latitude), float(longitude), b'W', flags=swe.FLG_SIDEREAL)
    positions['Ascendant'] = {'longitude': ascmc[0] % 360, 'retrograde': False}
    return positions

def raman_d30_get_d30_sign_and_degree(longitude):
    sign_index = int(longitude // 30)
    degree_in_sign = longitude % 30
    natal_sign = SIGNS[sign_index]
    is_odd = sign_index % 2 == 0
    ranges = ODD_SIGN_D30_RANGES if is_odd else EVEN_SIGN_D30_RANGES
    for start, end, sign in ranges:
        if start <= degree_in_sign < end:
            range_length = end - start
            position_in_range = (degree_in_sign - start) / range_length
            d30_degree = position_in_range * 30
            d30_sign_index = SIGNS.index(sign)
            return sign, d30_degree, d30_sign_index, natal_sign, degree_in_sign
    start, end, sign = ranges[-1]
    d30_degree = ((degree_in_sign - start) / (end - start)) * 30
    d30_sign_index = SIGNS.index(sign)
    return sign, d30_degree, d30_sign_index, natal_sign, degree_in_sign

def raman_d30_get_nakshatra_and_pada(longitude):
    nak_num = int(longitude // (13 + 1/3))
    nakshatra = NAKSHATRA_NAMES[nak_num]
    nak_lord = NAKSHATRA_LORDS[nak_num]
    nak_start = nak_num * 13.3333333333
    deg_in_nak = longitude - nak_start
    pada = int(deg_in_nak // 3.3333333333) + 1
    return nakshatra, nak_lord, pada

def raman_d30_format_degree(deg):
    d = int(deg)
    m = int((deg - d) * 60)
    s = (deg - d - m / 60) * 3600
    return f"{d}° {m}' {s:.2f}\""

def raman_d30_assign_houses(d30_positions, asc_sign_index):
    for planet, pdata in d30_positions.items():
        planet_sign_index = pdata['d30_sign_index']
        house = (planet_sign_index - asc_sign_index) % 12 + 1
        pdata['house'] = house

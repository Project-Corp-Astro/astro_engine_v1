import swisseph as swe
from datetime import datetime, timedelta

SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
PLANET_IDS = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS, 'Mercury': swe.MERCURY,
    'Jupiter': swe.JUPITER, 'Venus': swe.VENUS, 'Saturn': swe.SATURN,
    'Rahu': swe.MEAN_NODE, 'Ketu': None
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
NAK_LEN = 13 + 1/3
PADA_LEN = NAK_LEN / 4

def bava_get_julian_day(date_str, time_str, tz_offset):
    dt = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M:%S')
    ut_dt = dt - timedelta(hours=tz_offset)
    return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, ut_dt.hour + ut_dt.minute / 60.0 + ut_dt.second / 3600.0)

def bava_calculate_sunrise(jd, lat, lon, tz_offset):
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
    # Fallback: 6 AM local
    dt = datetime.strptime(f"{bava_jd_to_date(jd)} 06:00:00", '%Y-%m-%d %H:%M:%S')
    sunrise_jd = swe.julday(dt.year, dt.month, dt.day, 6.0 - tz_offset)
    sun_lon = swe.calc_ut(sunrise_jd, swe.SUN, swe.FLG_SIDEREAL)[0][0] % 360
    return sunrise_jd, sun_lon

def bava_calculate_bhava_lagna(birth_jd, sunrise_jd, sunrise_sun_lon):
    time_elapsed = (birth_jd - sunrise_jd) * 1440
    if time_elapsed < 0:
        time_elapsed += 1440
    degrees_progressed = time_elapsed / 4.0
    bl_lon = (sunrise_sun_lon + degrees_progressed) % 360
    return bl_lon

def bava_get_sign_and_degrees(longitude):
    sign_index = int(longitude // 30)
    degrees = longitude % 30
    return SIGNS[sign_index % 12], degrees

def bava_calculate_house(planet_sign, bl_sign):
    planet_index = SIGNS.index(planet_sign)
    bl_index = SIGNS.index(bl_sign)
    return (planet_index - bl_index) % 12 + 1

def bava_jd_to_date(jd):
    y, m, d, _ = swe.revjul(jd)
    return f"{y:04d}-{m:02d}-{d:02d}"

def bava_nakshatra_and_pada(lon):
    nak_num = int(lon // NAK_LEN)
    nak_deg = lon - nak_num * NAK_LEN
    pada_num = int(nak_deg // PADA_LEN) + 1
    nak_name, nak_lord = NAKSHATRAS[nak_num % 27]
    return nak_name, nak_lord, pada_num

import swisseph as swe
from datetime import datetime, timedelta
swe.set_sid_mode(swe.SIDM_LAHIRI)


SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio',
    'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]
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

def lahiri_hora_get_julian_day(date_str, time_str, tz_offset):
    dt = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M:%S')
    ut_dt = dt - timedelta(hours=tz_offset)
    return swe.julday(
        ut_dt.year, ut_dt.month, ut_dt.day,
        ut_dt.hour + ut_dt.minute / 60.0 + ut_dt.second / 3600.0
    )

def lahiri_hora_calculate_sunrise_jd_and_asc(jd, lat, lon, tz_offset):
    geopos = [lon, lat, 0.0]
    flags = swe.CALC_RISE | swe.BIT_DISC_CENTER | swe.BIT_NO_REFRACTION
    for offset in range(-1, 2):
        search_jd = jd + offset
        try:
            ret, t_rise = swe.rise_trans(search_jd - 1.0, swe.SUN, geopos, flags=flags)
            if ret == 0 and t_rise[0] is not None:
                sunrise_jd = t_rise[0]
                house_cusps, ascmc = swe.houses_ex(sunrise_jd, lat, lon, b'P', swe.FLG_SIDEREAL)
                sunrise_asc = ascmc[0] % 360
                return sunrise_jd, sunrise_asc
        except Exception:
            continue
    # fallback: 6am
    dt = datetime.strptime(f"{lahiri_hora_jd_to_date(jd)} 06:00:00", '%Y-%m-%d %H:%M:%S')
    sunrise_jd = swe.julday(dt.year, dt.month, dt.day, 6.0 - tz_offset)
    house_cusps, ascmc = swe.houses_ex(sunrise_jd, lat, lon, b'P', swe.FLG_SIDEREAL)
    sunrise_asc = ascmc[0] % 360
    return sunrise_jd, sunrise_asc

def lahiri_hora_calculate_hora_lagna(birth_jd, sunrise_jd, sunrise_asc):
    elapsed_minutes = (birth_jd - sunrise_jd) * 24 * 60
    if elapsed_minutes < 0:
        elapsed_minutes += 720  # wrap for 12 hours
    degrees_progressed = elapsed_minutes * 0.5  # 1° per 2 min
    hl_lon = (sunrise_asc + degrees_progressed) % 360
    return hl_lon

def lahiri_hora_get_sign_and_degrees(longitude):
    sign_index = int(longitude // 30)
    degrees = longitude % 30
    return SIGNS[sign_index % 12], degrees

def lahiri_hora_calculate_house(planet_sign, hl_sign):
    planet_index = SIGNS.index(planet_sign)
    hl_index = SIGNS.index(hl_sign)
    return (planet_index - hl_index) % 12 + 1

def lahiri_hora_jd_to_date(jd):
    y, m, d, _ = swe.revjul(jd)
    return f"{y:04d}-{m:02d}-{d:02d}"

def lahiri_hora_nakshatra_and_pada(lon):
    nak_num = int(lon // NAK_LEN)
    nak_deg = lon - nak_num * NAK_LEN
    pada_num = int(nak_deg // PADA_LEN) + 1
    nak_name, nak_lord = NAKSHATRAS[nak_num % 27]
    return nak_name, nak_lord, pada_num

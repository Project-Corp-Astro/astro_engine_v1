import swisseph as swe
from datetime import datetime, timedelta

SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
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

def raman_hora_get_julian_day(date_str, time_str, tz_offset):
    dt = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M:%S')
    ut_dt = dt - timedelta(hours=tz_offset)
    return swe.julday(
        ut_dt.year, ut_dt.month, ut_dt.day,
        ut_dt.hour + ut_dt.minute / 60.0 + ut_dt.second / 3600.0
    )

def raman_hora_jd_to_date(jd):
    y, m, d, _ = swe.revjul(jd)
    return f"{y:04d}-{m:02d}-{d:02d}"

def raman_hora_find_sunrise_before_birth(birth_jd, lat, lon, tz_offset):
    for delta in [0, -1]:
        jd_day = int(birth_jd) + delta
        geopos = [lon, lat, 0.0]
        flags = swe.CALC_RISE | swe.BIT_DISC_CENTER | swe.BIT_NO_REFRACTION
        try:
            ret, t_rise = swe.rise_trans(jd_day - 1.0, swe.SUN, geopos, flags=flags)
            if ret == 0 and t_rise[0] is not None and t_rise[0] <= birth_jd + 1e-4:
                house_cusps, ascmc = swe.houses_ex(t_rise[0], lat, lon, b'W', swe.FLG_SIDEREAL)
                sunrise_jd = t_rise[0]
                sunrise_asc = ascmc[0] % 360
                return sunrise_jd, sunrise_asc
        except Exception:
            continue
    dt = datetime.strptime(f"{raman_hora_jd_to_date(birth_jd)} 06:00:00", '%Y-%m-%d %H:%M:%S')
    ut_dt = dt - timedelta(hours=tz_offset)
    sunrise_jd = swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, ut_dt.hour + ut_dt.minute / 60.0)
    house_cusps, ascmc = swe.houses_ex(sunrise_jd, lat, lon, b'W', swe.FLG_SIDEREAL)
    sunrise_asc = ascmc[0] % 360
    return sunrise_jd, sunrise_asc

def raman_hora_calculate_hora_lagna(birth_jd, sunrise_jd, sunrise_asc):
    elapsed_minutes = (birth_jd - sunrise_jd) * 24 * 60
    if elapsed_minutes < 0:
        elapsed_minutes += 1440
    degrees_progressed = elapsed_minutes * 0.5
    hl_lon = (sunrise_asc + degrees_progressed) % 360
    return hl_lon

def raman_hora_get_sign_and_degrees(longitude):
    sign_index = int(longitude // 30)
    degrees = longitude % 30
    return SIGNS[sign_index % 12], degrees

def raman_hora_calculate_house(planet_sign, hl_sign):
    planet_index = SIGNS.index(planet_sign)
    hl_index = SIGNS.index(hl_sign)
    return (planet_index - hl_index) % 12 + 1

def raman_hora_nakshatra_and_pada(lon):
    nak_num = int(lon // NAK_LEN)
    nak_deg = lon - nak_num * NAK_LEN
    pada_num = int(nak_deg // PADA_LEN) + 1
    nak_name, nak_lord = NAKSHATRAS[nak_num % 27]
    return nak_name, nak_lord, pada_num

def raman_hora_calculate_chart(birth_date, birth_time, lat, lon, tz_offset):
    birth_jd = raman_hora_get_julian_day(birth_date, birth_time, tz_offset)
    sunrise_jd, sunrise_asc = raman_hora_find_sunrise_before_birth(birth_jd, lat, lon, tz_offset)
    hl_lon = raman_hora_calculate_hora_lagna(birth_jd, sunrise_jd, sunrise_asc)
    hl_sign, hl_degrees = raman_hora_get_sign_and_degrees(hl_lon)
    hl_nak, hl_nak_lord, hl_pada = raman_hora_nakshatra_and_pada(hl_lon)

    positions = {}
    for planet, pid in PLANET_IDS.items():
        if planet == 'Ketu':
            continue
        pos_data = swe.calc_ut(birth_jd, pid, swe.FLG_SIDEREAL | swe.FLG_SPEED)[0]
        lon = pos_data[0] % 360
        sign, degrees = raman_hora_get_sign_and_degrees(lon)
        retrograde = 'R' if pos_data[3] < 0 else ''
        house = raman_hora_calculate_house(sign, hl_sign)
        nak, nak_lord, pada = raman_hora_nakshatra_and_pada(lon)
        positions[planet] = {
            "degrees": round(degrees, 4), "sign": sign, "retrograde": retrograde,
            "house": house, "nakshatra": nak, "nakshatra_lord": nak_lord, "pada": pada
        }

    rahu_lon = positions['Rahu']['degrees'] + (SIGNS.index(positions['Rahu']['sign']) * 30)
    ketu_lon = (rahu_lon + 180) % 360
    ketu_sign, ketu_degrees = raman_hora_get_sign_and_degrees(ketu_lon)
    ketu_nak, ketu_nak_lord, ketu_pada = raman_hora_nakshatra_and_pada(ketu_lon)
    positions['Ketu'] = {
        "degrees": round(ketu_degrees, 4), "sign": ketu_sign, "retrograde": "",
        "house": raman_hora_calculate_house(ketu_sign, hl_sign),
        "nakshatra": ketu_nak, "nakshatra_lord": ketu_nak_lord, "pada": ketu_pada
    }

    return {
        "hora_lagna": {
            "sign": hl_sign, "degrees": round(hl_degrees, 4),
            "nakshatra": hl_nak, "nakshatra_lord": hl_nak_lord, "pada": hl_pada
        },
        "planets": positions
    }

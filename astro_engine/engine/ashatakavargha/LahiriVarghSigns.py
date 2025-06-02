import swisseph as swe
from datetime import datetime, timedelta

SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]
PLANETS = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS, 'Mercury': swe.MERCURY,
    'Jupiter': swe.JUPITER, 'Venus': swe.VENUS, 'Saturn': swe.SATURN, 'Rahu': swe.MEAN_NODE
}
DCHARTS = [
    ("D1", 1),   ("D2", 2),   ("D3", 3),   ("D4", 4),   ("D7", 7),   ("D9", 9),   ("D10", 10),
    ("D12", 12), ("D16", 16), ("D20", 20), ("D24", 24), ("D27", 27), ("D30", 30), ("D40", 40),
    ("D45", 45), ("D60", 60)
]

def lahiri_sign_element(sign_idx):
    if sign_idx in [0, 4, 8]:   return 'fire'
    if sign_idx in [1, 5, 9]:   return 'earth'
    if sign_idx in [2, 6, 10]:  return 'air'
    if sign_idx in [3, 7, 11]:  return 'water'

def lahiri_sign_local_to_utc(birth_date, birth_time, timezone_offset):
    dt = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M:%S")
    return dt - timedelta(hours=float(timezone_offset))

def lahiri_sign_julian_day(dt):
    return swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60 + dt.second/3600)

def lahiri_sign_get_sidereal_positions(jd):
    positions = {}
    for pname, code in PLANETS.items():
        swe.set_sid_mode(swe.SIDM_LAHIRI)

        pos, _ = swe.calc_ut(jd, code, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
        lon = pos[0] % 360
        sign_idx = int(lon // 30)
        deg_in_sign = lon % 30
        positions[pname] = (lon, sign_idx, deg_in_sign)
    positions['Ketu'] = ((positions['Rahu'][0] + 180) % 360,
                         int(((positions['Rahu'][0] + 180) % 360) // 30),
                         (positions['Rahu'][0] + 180) % 30)
    return positions

def lahiri_sign_get_sidereal_asc(jd, lat, lon):
    house_cusps, ascmc = swe.houses(jd, lat, lon, b'P')
    ayanamsa = swe.get_ayanamsa_ut(jd)
    tropical_asc = ascmc[0]
    sidereal_asc = (tropical_asc - ayanamsa) % 360
    sign_idx = int(sidereal_asc // 30)
    deg_in_sign = sidereal_asc % 30
    return sidereal_asc, sign_idx, deg_in_sign

def lahiri_sign_varga_sign(p, deg_in_sign, natal_sign_idx, chart, asc=False):
    N = {
        "D1": 1, "D2": 2, "D3": 3, "D4": 4, "D7": 7, "D9": 9, "D10": 10, "D12": 12,
        "D16": 16, "D20": 20, "D24": 24, "D27": 27, "D30": 30, "D40": 40, "D45": 45, "D60": 60
    }[chart]

    if chart == "D1":
        return natal_sign_idx

    if chart == "D2":
        if natal_sign_idx % 2 == 0:
            return 4 if deg_in_sign < 15 else 3
        else:
            return 3 if deg_in_sign < 15 else 4

    if chart == "D3":
        if deg_in_sign < 10:
            return natal_sign_idx
        elif deg_in_sign < 20:
            return (natal_sign_idx + 4) % 12
        else:
            return (natal_sign_idx + 8) % 12

    if chart == "D4":
        if deg_in_sign < 7.5:
            return natal_sign_idx
        elif deg_in_sign < 15:
            return (natal_sign_idx + 3) % 12
        elif deg_in_sign < 22.5:
            return (natal_sign_idx + 6) % 12
        else:
            return (natal_sign_idx + 9) % 12

    if chart == "D7":
        div = int(deg_in_sign * 7 // 30)
        start = natal_sign_idx if natal_sign_idx % 2 == 0 else (natal_sign_idx + 6) % 12
        return (start + div) % 12

    if chart == "D9":
        div = int(deg_in_sign * 9 // 30)
        element = lahiri_sign_element(natal_sign_idx)
        start = {'fire': 0, 'earth': 9, 'air': 6, 'water': 3}[element]
        return (start + div) % 12

    if chart == "D10":
        div = int(deg_in_sign * 10 // 30)
        start = natal_sign_idx if natal_sign_idx % 2 == 0 else (natal_sign_idx + 8) % 12
        return (start + div) % 12

    if chart == "D12":
        div = int(deg_in_sign * 12 // 30)
        return (natal_sign_idx + div) % 12

    if chart == "D16":
        div = int(deg_in_sign * 16 // 30)
        mfd = natal_sign_idx % 3
        start = [0, 4, 8][mfd]
        return (start + div) % 12

    if chart == "D20":
        div = int(deg_in_sign * 20 // 30)
        element = lahiri_sign_element(natal_sign_idx)
        start = {'fire': 0, 'earth': 8, 'air': 4, 'water': 3}[element]
        return (start + div) % 12

    if chart == "D24":
        div = int(deg_in_sign * 24 // 30)
        start = 4 if natal_sign_idx % 2 == 0 else 3
        return (start + div) % 12

    if chart == "D27":
        div = int(deg_in_sign * 27 // 30)
        element = lahiri_sign_element(natal_sign_idx)
        start = {'fire': 0, 'earth': 3, 'air': 6, 'water': 9}[element]
        return (start + div) % 12

    if chart == "D30":
        odd = natal_sign_idx % 2 == 0
        if odd:
            if deg_in_sign < 5:    return 0
            elif deg_in_sign < 10: return 10
            elif deg_in_sign < 18: return 2
            elif deg_in_sign < 25: return 6
            else:                  return 8
        else:
            if deg_in_sign < 5:    return 1
            elif deg_in_sign < 12: return 5
            elif deg_in_sign < 20: return 11
            elif deg_in_sign < 25: return 9
            else:                  return 7

    if chart == "D40":
        div = int(deg_in_sign * 40 // 30)
        start = 0 if natal_sign_idx % 2 == 0 else 6
        return (start + div) % 12

    if chart == "D45":
        div = int(deg_in_sign * 45 // 30)
        start = 0 if natal_sign_idx % 2 == 0 else 8
        return (start + div) % 12

    if chart == "D60":
        div = int(deg_in_sign * 60 // 30)
        return (natal_sign_idx + div) % 12

    div = int(deg_in_sign * N // 30)
    return (natal_sign_idx + div) % 12

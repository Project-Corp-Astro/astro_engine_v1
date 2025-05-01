# C:\Users\prave\Documents\Astro_Engine\astro_engine\engine\natalCharts\natal.py
import swisseph as swe
from datetime import datetime, timedelta

signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

def get_house(lon, asc_sign_index, orientation_shift=0):
    sign_index = int(lon // 30) % 12
    house_index = (sign_index - asc_sign_index + orientation_shift) % 12
    return house_index + 1

def longitude_to_sign(deg):
    deg = deg % 360
    sign_index = int(deg // 30)
    sign = signs[sign_index]
    sign_deg = deg % 30
    return sign, sign_deg

def format_dms(deg):
    d = int(deg)
    m_fraction = (deg - d) * 60
    m = int(m_fraction)
    s = (m_fraction - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def calculate_natal_chart(birth_data):
    # Parse date and time
    birth_date = datetime.strptime(birth_data['birth_date'], '%Y-%m-%d')
    birth_time = datetime.strptime(birth_data['birth_time'], '%H:%M:%S').time()
    local_datetime = datetime.combine(birth_date, birth_time)
    ut_datetime = local_datetime - timedelta(hours=float(birth_data['timezone_offset']))
    hour_decimal = ut_datetime.hour + ut_datetime.minute / 60.0 + ut_datetime.second / 3600.0
    jd_ut = swe.julday(ut_datetime.year, ut_datetime.month, ut_datetime.day, hour_decimal)

    # Set Lahiri ayanamsa
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa_value = swe.get_ayanamsa_ut(jd_ut)

    # Planetary positions
    planets = [
        (swe.SUN, 'Sun'), (swe.MOON, 'Moon'), (swe.MARS, 'Mars'),
        (swe.MERCURY, 'Mercury'), (swe.JUPITER, 'Jupiter'), (swe.VENUS, 'Venus'),
        (swe.SATURN, 'Saturn'), (swe.TRUE_NODE, 'Rahu')
    ]
    flag = swe.FLG_SIDEREAL | swe.FLG_SPEED
    planet_positions = {}
    for planet_id, planet_name in planets:
        pos, ret = swe.calc_ut(jd_ut, planet_id, flag)
        if ret < 0:
            raise Exception(f"Error calculating {planet_name}")
        lon = pos[0] % 360
        speed = pos[3]
        retrograde = 'R' if speed < 0 else ''
        planet_positions[planet_name] = (lon, retrograde)

    # Calculate Ketu
    rahu_lon = planet_positions['Rahu'][0]
    ketu_lon = (rahu_lon + 180) % 360
    planet_positions['Ketu'] = (ketu_lon, '')

    # Ascendant and houses
    cusps, ascmc = swe.houses_ex(jd_ut, float(birth_data['latitude']), float(birth_data['longitude']), b'W', flags=swe.FLG_SIDEREAL)
    ascendant_lon = ascmc[0] % 360
    asc_sign_index = int(ascendant_lon // 30)
    asc_sign = signs[asc_sign_index]

    # Assign house signs
    house_signs = []
    for i in range(12):
        sign_index = (asc_sign_index + i) % 12
        sign_start_lon = (sign_index * 30)
        house_signs.append({"sign": signs[sign_index], "start_longitude": sign_start_lon})

    # Calculate houses
    orientation_shift = int(birth_data.get('orientation_shift', 0))
    planet_houses = {planet: get_house(lon, asc_sign_index, orientation_shift=orientation_shift)
                     for planet, (lon, _) in planet_positions.items()}

    # Format output
    planetary_positions_json = {}
    for planet_name, (lon, retro) in planet_positions.items():
        sign, sign_deg = longitude_to_sign(lon)
        dms = format_dms(sign_deg)
        house = planet_houses[planet_name]
        planetary_positions_json[planet_name] = {
            "sign": sign,
            "degrees": dms,
            "retrograde": retro,
            "house": house
        }

    ascendant_json = {"sign": asc_sign, "degrees": format_dms(ascendant_lon % 30)}
    house_signs_json = {f"House {i+1}": {"sign": house["sign"], "start_longitude": format_dms(house["start_longitude"])}
                       for i, house in enumerate(house_signs)}

    return {
        "user_name": birth_data['user_name'],
        "birth_details": {
            "birth_date": birth_data['birth_date'],
            "birth_time": birth_time.strftime('%H:%M:%S'),
            "latitude": float(birth_data['latitude']),
            "longitude": float(birth_data['longitude']),
            "timezone_offset": float(birth_data['timezone_offset'])
        },
        "planetary_positions": planetary_positions_json,
        "ascendant": ascendant_json,
        "house_signs": house_signs_json,
        "notes": {
            "ayanamsa": "Lahiri",
            "ayanamsa_value": f"{ayanamsa_value:.6f}",
            "chart_type": "Rasi",
            "house_system": "Whole Sign"
        }
    }
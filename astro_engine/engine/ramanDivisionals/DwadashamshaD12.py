import swisseph as swe
from datetime import datetime, timedelta

# Zodiac signs list (0 = Aries, 1 = Taurus, ..., 11 = Pisces)
signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

# Nakshatra list (27 nakshatras)
nakshatras = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra', 
    'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni', 
    'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha', 
    'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta', 
    'Shatabhisha', 'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
]

def get_julian_day(date_str, time_str, timezone_offset):
    """
    Convert birth date and time to Julian Day for astronomical calculations.
    """
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        time_obj = datetime.strptime(time_str, '%H:%M:%S')
        local_datetime = datetime.combine(date_obj, time_obj.time())
        ut_datetime = local_datetime - timedelta(hours=timezone_offset)
        hour_decimal = ut_datetime.hour + (ut_datetime.minute / 60.0) + (ut_datetime.second / 3600.0)
        return swe.julday(ut_datetime.year, ut_datetime.month, ut_datetime.day, hour_decimal)
    except ValueError as e:
        raise ValueError(f"Invalid date or time format: {str(e)}")

def format_dms(deg):
    """
    Format degrees into degrees, minutes, and seconds for readability.
    """
    d = int(deg)
    m_fraction = (deg - d) * 60
    m = int(m_fraction)
    s = (m_fraction - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def get_nakshatra(longitude):
    """
    Determine the nakshatra based on sidereal longitude.
    """
    nakshatra_index = int((longitude % 360) / 13.3333) % 27
    return nakshatras[nakshatra_index]

def get_d12_position(d1_lon_sidereal):
    """
    Calculate the D12 sign, degree, and nakshatra from the D1 sidereal longitude.
    
    Logic:
    - Each 30° zodiac sign is divided into 12 parts of 2.5° each.
    - D12 sign starts from the D1 sign and progresses sequentially based on the segment.
    """
    d1_sign_index = int(d1_lon_sidereal // 30)  # D1 sign index (0–11)
    d1_sign_position = d1_lon_sidereal % 30     # Degrees within the sign (0–29.999...)
    d12_segment = int(d1_sign_position / 2.5)   # D12 segment number (0–11)
    d12_sign_index = (d1_sign_index + d12_segment) % 12  # Corrected D12 sign index
    segment_position = d1_sign_position % 2.5   # Position within the 2.5° segment
    d12_degree = (segment_position / 2.5) * 30  # Scale to 0–30° in D12 sign
    d12_lon = (d12_sign_index * 30) + d12_degree  # Full D12 longitude for house calculation
    nakshatra = get_nakshatra(d1_lon_sidereal)  # Use D1 longitude for nakshatra
    
    return {
        "sign": signs[d12_sign_index],
        "degrees": format_dms(d12_degree),
        "nakshatra": nakshatra,
        "longitude": d12_lon
    }

def get_d12_house(d12_lon, d12_asc_sign_index):
    """
    Assign house number in the D12 chart using Whole Sign system.
    """
    sign_index = int(d12_lon // 30) % 12
    house_index = (sign_index - d12_asc_sign_index + 12) % 12  # Ensure positive offset
    return house_index + 1

def raman_dwadashamsha(data):
    """
    Calculate the complete Dwadasamsa (D12) chart with nakshatras.
    
    Args:
        data (dict): Input data containing birth_date, birth_time, latitude, longitude, timezone_offset
    
    Returns:
        dict: D12 chart details including ascendant, planetary positions, and house signs
    """
    birth_date = data['birth_date']
    birth_time = data['birth_time']
    latitude = float(data['latitude'])
    longitude = float(data['longitude'])
    timezone_offset = float(data['timezone_offset'])

    # Calculate Julian Day
    jd_ut = get_julian_day(birth_date, birth_time, timezone_offset)

    # Set Lahiri Ayanamsa
    swe.set_sid_mode(swe.SIDM_RAMAN)

    # Calculate D1 sidereal positions for planets
    planets = [
        (swe.SUN, 'Sun'), (swe.MOON, 'Moon'), (swe.MARS, 'Mars'),
        (swe.MERCURY, 'Mercury'), (swe.JUPITER, 'Jupiter'), (swe.VENUS, 'Venus'),
        (swe.SATURN, 'Saturn'), (swe.TRUE_NODE, 'Rahu')
    ]
    flag = swe.FLG_SIDEREAL | swe.FLG_SPEED
    d1_positions_sidereal = {}
    for planet_id, planet_name in planets:
        pos, ret = swe.calc_ut(jd_ut, planet_id, flag)
        if ret < 0:
            raise ValueError(f"Error calculating {planet_name}")
        lon = pos[0] % 360
        speed = pos[3]
        retrograde = 'R' if speed < 0 else ''
        d1_positions_sidereal[planet_name] = (lon, retrograde)

    # Calculate Ketu (180° opposite Rahu)
    rahu_lon = d1_positions_sidereal['Rahu'][0]
    ketu_lon = (rahu_lon + 180) % 360
    d1_positions_sidereal['Ketu'] = (ketu_lon, '')

    # Calculate D1 sidereal ascendant
    cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b'W', flags=swe.FLG_SIDEREAL)
    d1_asc_lon_sidereal = ascmc[0] % 360

    # Calculate D12 ascendant
    d12_asc = get_d12_position(d1_asc_lon_sidereal)
    d12_asc_sign_index = signs.index(d12_asc['sign'])

    # Calculate D12 positions for planets
    d12_positions = {}
    for planet, (d1_lon, retro) in d1_positions_sidereal.items():
        d12_pos = get_d12_position(d1_lon)
        d12_lon = d12_pos['longitude']
        house = get_d12_house(d12_lon, d12_asc_sign_index)
        d12_positions[planet] = {
            "sign": d12_pos['sign'],
            "degrees": d12_pos['degrees'],
            "retrograde": retro,
            "house": house,
            "nakshatra": d12_pos['nakshatra']
        }

    # Calculate house signs based on D12 ascendant
    house_signs = []
    for i in range(12):
        sign_index = (d12_asc_sign_index + i) % 12
        house_signs.append({"house": i + 1, "sign": signs[sign_index]})

    # Construct the response
    response = {
        "d12_ascendant": d12_asc,
        "planetary_positions": d12_positions,
        "house_signs": house_signs,
        "notes": {
            "ayanamsa": "Lahiri",
            "chart_type": "Dwadasamsa (D12)",
            "house_system": "Whole Sign"
        }
    }

    return response
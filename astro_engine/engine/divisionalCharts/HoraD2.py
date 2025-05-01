# calculations.py
import swisseph as swe
from datetime import datetime, timedelta

# Sidereal zodiac signs (0 = Aries, ..., 11 = Pisces)
SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

# Nakshatras (27 divisions, 13°20' each)
NAKSHATRAS = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra', 
    'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni', 
    'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha', 
    'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta', 
    'Shatabhisha', 'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
]

def get_julian_day(date_str, time_str, timezone_offset):
    """Convert birth date and time to Julian Day (UT)."""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        time_obj = datetime.strptime(time_str, '%H:%M:%S')
        local_dt = datetime.combine(date_obj, time_obj.time())
        ut_dt = local_dt - timedelta(hours=timezone_offset)
        hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
        return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal)
    except ValueError as e:
        raise ValueError(f"Invalid date/time format: {e}")

def format_dms(degrees):
    """Format degrees into degrees, minutes, seconds."""
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = (degrees - d - m / 60.0) * 3600
    return f"{d}° {m}' {s:.2f}\""

def get_nakshatra(longitude):
    """Calculate nakshatra from sidereal longitude."""
    nakshatra_index = int((longitude % 360) / 13.3333) % 27
    return NAKSHATRAS[nakshatra_index]

def get_d2_position(d1_longitude):
    """Calculate D2 sign and degrees using Parashara's method."""
    # Extract D1 sign index and degrees within the sign
    d1_sign_index = int(d1_longitude // 30) % 12
    d1_sign_deg = d1_longitude % 30
    # Determine if the sign is odd (0, 2, 4, ...) or even (1, 3, 5, ...)
    is_odd = d1_sign_index % 2 == 0
    # Apply Parashara D2 mapping
    if is_odd:
        if d1_sign_deg < 15:
            d2_sign, d2_sign_index = "Leo", 4  # First half of odd sign
        else:
            d2_sign, d2_sign_index = "Cancer", 3  # Second half of odd sign
    else:
        if d1_sign_deg < 15:
            d2_sign, d2_sign_index = "Cancer", 3  # First half of even sign
        else:
            d2_sign, d2_sign_index = "Leo", 4  # Second half of even sign
    d2_deg = d1_sign_deg  # Degrees remain unchanged in D2
    d2_sidereal_lon = (d2_sign_index * 30) + d2_deg
    return {
        "sign": d2_sign,
        "degrees": format_dms(d2_deg),
        "nakshatra": get_nakshatra(d2_sidereal_lon),
        "sign_index": d2_sign_index
    }

def get_d2_house(d2_sign_index, d2_asc_sign_index):
    """Assign house number using Whole Sign system."""
    return (d2_sign_index - d2_asc_sign_index) % 12 + 1

def calculate_d2_chart(data):
    """
    Calculate the Hora (D2) chart based on birth data.
    
    Parameters:
    - data: Dictionary containing birth_date, birth_time, latitude, longitude, timezone_offset.
    
    Returns:
    - Dictionary containing the D2 chart data or raises an exception on error.
    """
    # Calculate Julian Day
    jd_ut = get_julian_day(data['birth_date'], data['birth_time'], float(data['timezone_offset']))

    # Set Lahiri Ayanamsa
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    # Calculate D1 sidereal positions for planets
    planets = [
        (swe.SUN, 'Sun'), (swe.MOON, 'Moon'), (swe.MARS, 'Mars'),
        (swe.MERCURY, 'Mercury'), (swe.JUPITER, 'Jupiter'), (swe.VENUS, 'Venus'),
        (swe.SATURN, 'Saturn'), (swe.TRUE_NODE, 'Rahu')
    ]
    flag = swe.FLG_SIDEREAL | swe.FLG_SPEED
    d1_positions = {}
    for planet_id, name in planets:
        pos, ret = swe.calc_ut(jd_ut, planet_id, flag)
        if ret < 0:
            raise ValueError(f"Error calculating {name}")
        lon = pos[0] % 360
        speed = pos[3]
        retrograde = 'R' if speed < 0 else ''
        d1_positions[name] = (lon, retrograde)

    # Calculate Ketu (opposite Rahu)
    rahu_lon = d1_positions['Rahu'][0]
    ketu_lon = (rahu_lon + 180) % 360
    d1_positions['Ketu'] = (ketu_lon, '')

    # Calculate D1 sidereal ascendant
    cusps, ascmc = swe.houses_ex(jd_ut, float(data['latitude']), float(data['longitude']), b'W', flags=swe.FLG_SIDEREAL)
    d1_asc_sidereal = ascmc[0] % 360

    # Calculate D2 ascendant using the unified function
    d2_asc = get_d2_position(d1_asc_sidereal)
    d2_asc_sign_index = SIGNS.index(d2_asc['sign'])

    # Calculate D2 positions for planets
    d2_positions = {}
    for planet, (d1_lon, retro) in d1_positions.items():
        d2_pos = get_d2_position(d1_lon)
        house = get_d2_house(d2_pos['sign_index'], d2_asc_sign_index)
        d2_positions[planet] = {
            "sign": d2_pos['sign'],
            "degrees": d2_pos['degrees'],
            "retrograde": retro,
            "house": house,
            "nakshatra": d2_pos['nakshatra']
        }

    # Generate house-to-sign mappings (Whole Sign system)
    house_signs = [{"house": i + 1, "sign": SIGNS[(d2_asc_sign_index + i) % 12]} for i in range(12)]

    # Construct the response
    response = {
        "d2_ascendant": {
            "sign": d2_asc['sign'],
            "degrees": d2_asc['degrees'],
            "nakshatra": d2_asc['nakshatra']
        },
        "planetary_positions": d2_positions,
        "house_signs": house_signs,
        "metadata": {
            "ayanamsa": "Lahiri",
            "chart_type": "Hora (D2)",
            "house_system": "Whole Sign"
        }
    }
    return response

# calculations.py
import swisseph as swe
from datetime import datetime, timedelta

# List of zodiac signs
signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

def get_house(lon, asc_sign_index, orientation_shift=0):
    """
    Calculate house number based on planet longitude and ascendant sign index for Whole Sign system.
    
    Args:
        lon (float): Planet's longitude (0–360°)
        asc_sign_index (int): Ascendant's sign index (0–11, Aries–Pisces)
        orientation_shift (int): Shift in house numbering (default 0 for standard Whole Sign)
    
    Returns:
        int: House number (1–12)
    """
    sign_index = int(lon // 30) % 12  # Planet's sign index
    house_index = (sign_index - asc_sign_index + orientation_shift) % 12  # Adjusted house index
    return house_index + 1  # 1-based house number

def longitude_to_sign(deg):
    """
    Convert longitude to sign and degree within sign.
    
    Args:
        deg (float): Longitude in degrees
    
    Returns:
        tuple: (sign name, degrees within sign)
    """
    deg = deg % 360
    sign_index = int(deg // 30)
    sign = signs[sign_index]
    sign_deg = deg % 30
    return sign, sign_deg

def format_dms(deg):
    """
    Format degrees as degrees, minutes, seconds.
    
    Args:
        deg (float): Degrees to format
    
    Returns:
        str: Formatted string (e.g., "15° 30' 45.00\"")
    """
    d = int(deg)
    m_fraction = (deg - d) * 60
    m = int(m_fraction)
    s = (m_fraction - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def get_navamsa_position(d1_lon):
    """
    Calculate D9 sign and degree from D1 sidereal longitude.
    
    Args:
        d1_lon (float): D1 sidereal longitude (0–360°)
    
    Returns:
        tuple: (D9 sign index, D9 degree within sign)
    """
    navamsa_division = 30 / 9  # Each Navamsa division is 3.3333°
    navamsa_index = int(d1_lon / navamsa_division) % 12
    d9_degree = (d1_lon % navamsa_division) * 9
    return navamsa_index, d9_degree

def calculate_navamsa_chart(data):
    """
    Calculate the Navamsa (D9) chart based on birth data.
    
    Parameters:
    - data: Dictionary containing birth_date, birth_time, latitude, longitude, timezone_offset.
    
    Returns:
    - Dictionary containing the D9 chart data or raises an exception on error.
    """
    # Parse birth date and time
    birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d')
    birth_time = datetime.strptime(data['birth_time'], '%H:%M:%S').time()
    local_datetime = datetime.combine(birth_date, birth_time)
    ut_datetime = local_datetime - timedelta(hours=float(data['timezone_offset']))
    hour_decimal = ut_datetime.hour + ut_datetime.minute / 60.0 + ut_datetime.second / 3600.0
    jd_ut = swe.julday(ut_datetime.year, ut_datetime.month, ut_datetime.day, hour_decimal)

    # Set Lahiri Ayanamsa for sidereal calculations
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa_value = swe.get_ayanamsa_ut(jd_ut)

    # Calculate D1 planetary positions (sidereal)
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
            raise ValueError(f"Error calculating {planet_name}")
        lon = pos[0] % 360
        speed = pos[3]
        retrograde = 'R' if speed < 0 else ''
        planet_positions[planet_name] = (lon, retrograde)

    # Calculate Ketu (180° opposite Rahu)
    rahu_lon = planet_positions['Rahu'][0]
    ketu_lon = (rahu_lon + 180) % 360
    planet_positions['Ketu'] = (ketu_lon, '')

    # Calculate D1 Ascendant (sidereal)
    cusps, ascmc = swe.houses_ex(jd_ut, float(data['latitude']), float(data['longitude']), b'W', flags=swe.FLG_SIDEREAL)
    ascendant_lon = ascmc[0] % 360
    asc_sign_index = int(ascendant_lon // 30)

    # Calculate D9 positions
    d9_positions = {}
    for planet, (lon, retro) in planet_positions.items():
        d9_sign_index, d9_degree = get_navamsa_position(lon)
        d9_lon = (d9_sign_index * 30) + d9_degree
        d9_positions[planet] = (d9_lon, retro)

    # Calculate D9 Ascendant
    d9_asc_sign_index, d9_asc_degree = get_navamsa_position(ascendant_lon)
    d9_asc_lon = (d9_asc_sign_index * 30) + d9_asc_degree

    # Assign D9 houses based on D9 Ascendant
    planet_houses = {planet: get_house(d9_lon, d9_asc_sign_index) 
                     for planet, (d9_lon, _) in d9_positions.items()}

    # Format output
    planetary_positions_json = {}
    for planet, (d9_lon, retro) in d9_positions.items():
        sign, sign_deg = longitude_to_sign(d9_lon)
        dms = format_dms(sign_deg)
        house = planet_houses[planet]
        planetary_positions_json[planet] = {
            "sign": sign,
            "degrees": dms,
            "retrograde": retro,
            "house": house
        }

    ascendant_json = {"sign": signs[d9_asc_sign_index], "degrees": format_dms(d9_asc_lon % 30)}

    # Construct response
    response = {
        "planetary_positions": planetary_positions_json,
        "ascendant": ascendant_json,
        "notes": {
            "ayanamsa": "Lahiri",
            "ayanamsa_value": f"{ayanamsa_value:.6f}",
            "chart_type": "Navamsa (D9)",
            "house_system": "Whole Sign"
        }
    }
    return response
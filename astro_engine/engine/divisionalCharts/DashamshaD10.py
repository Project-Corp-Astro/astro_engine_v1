# calculations.py
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
    Convert birth date and time to Julian Day in UTC.

    Args:
        date_str (str): Date in 'YYYY-MM-DD' format
        time_str (str): Time in 'HH:MM:SS' format
        timezone_offset (float): Offset from UTC in hours

    Returns:
        float: Julian Day in UTC
    """
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        time_obj = datetime.strptime(time_str, '%H:%M:%S')
        local_datetime = datetime.combine(date_obj, time_obj.time())
        ut_datetime = local_datetime - timedelta(hours=timezone_offset)
        hour_decimal = ut_datetime.hour + (ut_datetime.minute / 60.0) + (ut_datetime.second / 3600.0)
        jd = swe.julday(ut_datetime.year, ut_datetime.month, ut_datetime.day, hour_decimal)
        return jd
    except ValueError as e:
        raise ValueError(f"Invalid date or time format: {str(e)}")

def format_dms(deg):
    """
    Format degrees into degrees, minutes, and seconds for readability.

    Args:
        deg (float): Degree value

    Returns:
        str: Formatted string (e.g., "10° 15' 30.00\"")
    """
    d = int(deg)
    m_fraction = (deg - d) * 60
    m = int(m_fraction)
    s = (m_fraction - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def get_nakshatra(longitude):
    """
    Determine the nakshatra based on sidereal longitude.

    Args:
        longitude (float): Sidereal longitude (0–360°)

    Returns:
        str: Nakshatra name
    """
    nakshatra_index = int((longitude % 360) / 13.3333) % 27
    return nakshatras[nakshatra_index]

def get_d10_position(d1_lon_sidereal):
    """
    Calculate D10 sign index, degree, and longitude from D1 sidereal longitude.

    Args:
        d1_lon_sidereal (float): D1 sidereal longitude (0–360°)

    Returns:
        tuple: (D10 sign index, D10 degree, D10 longitude)
    """
    d1_sign_index = int(d1_lon_sidereal // 30)  # D1 sign index (0–11)
    d1_sign_position = d1_lon_sidereal % 30     # Degrees within D1 sign (0–29.999...)
    d10_segment = int(d1_sign_position // 3)    # Segment within D1 sign (0–9)

    # Determine starting D10 sign based on D1 sign's parity
    if d1_sign_index % 2 == 0:  # Odd signs (Aries, Gemini, Leo, Libra, Sagittarius, Aquarius)
        start_sign = d1_sign_index
    else:  # Even signs (Taurus, Cancer, Virgo, Scorpio, Capricorn, Pisces)
        start_sign = (d1_sign_index + 9 - 1) % 12  # 9th sign from D1

    # Calculate D10 sign index and degree
    d10_sign_index = (start_sign + d10_segment) % 12
    d10_degree = (d1_sign_position % 3) * 10  # Scale remainder to 0–30°
    d10_lon = (d10_sign_index * 30) + d10_degree

    return d10_sign_index, d10_degree, d10_lon

def get_d10_house(d10_lon, d10_asc_sign_index):
    """
    Assign house number in the D10 chart using Whole Sign system.

    Args:
        d10_lon (float): D10 longitude (0–360°)
        d10_asc_sign_index (int): D10 ascendant sign index (0–11)

    Returns:
        int: House number (1–12)
    """
    sign_index = int(d10_lon // 30) % 12
    house_index = (sign_index - d10_asc_sign_index) % 12
    return house_index + 1

def get_conjunct_planets(d10_asc_lon, d10_positions, orb=2.0):
    """
    Identify planets conjunct with the ascendant within a specified orb.

    Args:
        d10_asc_lon (float): D10 ascendant longitude
        d10_positions (dict): Dictionary of planet longitudes and retrograde status
        orb (float): Conjunction orb in degrees (default 2°)

    Returns:
        list: List of dictionaries with conjunct planet names and retrograde status
    """
    conjunct = []
    for planet, (lon, retro) in d10_positions.items():
        if abs(lon - d10_asc_lon) <= orb or abs((lon - d10_asc_lon + 360) % 360) <= orb:
            conjunct.append({"planet": planet, "retrograde": retro})
    return conjunct

def calculate_d10_chart(data):
    """
    Calculate the Dashamsha (D10) chart based on birth data.
    
    Parameters:
    - data: Dictionary containing birth_date, birth_time, latitude, longitude, timezone_offset.
    
    Returns:
    - Dictionary containing the D10 chart data or raises an exception on error.
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
    for planet_id, planet_name in planets:
        pos, ret = swe.calc_ut(jd_ut, planet_id, flag)
        if ret < 0:
            raise ValueError(f"Error calculating {planet_name}: {swe.get_err_msg().decode()}")
        lon = pos[0] % 360
        speed = pos[3]
        retrograde = 'R' if speed < 0 else ''
        d1_positions[planet_name] = (lon, retrograde)

    # Calculate Ketu (180° opposite Rahu)
    rahu_lon = d1_positions['Rahu'][0]
    ketu_lon = (rahu_lon + 180) % 360
    d1_positions['Ketu'] = (ketu_lon, '')

    # Calculate D1 sidereal ascendant
    cusps, ascmc = swe.houses_ex(jd_ut, float(data['latitude']), float(data['longitude']), b'W', flags=swe.FLG_SIDEREAL)
    ascendant_d1_sidereal = ascmc[0] % 360

    # Calculate D10 positions
    d10_positions = {}
    for planet, (d1_lon, retro) in d1_positions.items():
        d10_sign_index, d10_degree, d10_lon = get_d10_position(d1_lon)
        d10_positions[planet] = (d10_lon, retro)

    # Calculate D10 ascendant
    d10_asc_sign_index, d10_asc_degree, d10_asc_lon = get_d10_position(ascendant_d1_sidereal)

    # Check for planets conjunct with ascendant
    asc_conjunct = get_conjunct_planets(d10_asc_lon, d10_positions, orb=2.0)

    # Assign houses
    planet_houses = {planet: get_d10_house(d10_lon, d10_asc_sign_index) 
                     for planet, (d10_lon, _) in d10_positions.items()}

    # Calculate house signs
    house_signs = []
    for i in range(12):
        sign_index = (d10_asc_sign_index + i) % 12
        house_signs.append({"house": i + 1, "sign": signs[sign_index]})

    # Format planetary positions
    planetary_positions_json = {}
    for planet, (d10_lon, retro) in d10_positions.items():
        sign_index = int(d10_lon // 30) % 12
        sign = signs[sign_index]
        sign_deg = d10_lon % 30
        dms = format_dms(sign_deg)
        house = planet_houses[planet]
        nakshatra = get_nakshatra(d10_lon)
        planetary_positions_json[planet] = {
            "sign": sign,
            "degrees": dms,
            "retrograde": retro,
            "house": house,
            "nakshatra": nakshatra
        }

    # Format ascendant with conjunctions
    ascendant_json = {
        "sign": signs[d10_asc_sign_index],
        "degrees": format_dms(d10_asc_degree),
        "nakshatra": get_nakshatra(d10_asc_lon),
        "conjunct": asc_conjunct
    }

    # Construct response
    response = {
        "planetary_positions": planetary_positions_json,
        "ascendant": ascendant_json,
        "house_signs": house_signs,
        "notes": {
            "ayanamsa": "Lahiri",
            "chart_type": "Dashamsha (D10)",
            "house_system": "Whole Sign",
            "d1_ascendant_longitude": ascendant_d1_sidereal
        }
    }

    return response

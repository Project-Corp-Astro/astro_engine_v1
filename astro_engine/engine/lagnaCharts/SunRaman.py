import swisseph as swe
from datetime import datetime, timedelta

# Set Swiss Ephemeris path
swe.set_ephe_path('astro_api/ephe')

# Zodiac signs list
SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Nakshatra names
NAKSHATRAS = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra', 'Punarvasu', 'Pushya', 'Ashlesha',
    'Magha', 'Purva Phalguni', 'Uttara Phalguni', 'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshta',
    'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta', 'Shatabhisha', 'Purva Bhadrapada',
    'Uttara Bhadrapada', 'Revati'
]

def get_julian_day(date_str, time_str, tz_offset):
    """
    Calculate Julian Day in Universal Time (UT) from local time.
    Args:
        date_str (str): Birth date in 'YYYY-MM-DD' format
        time_str (str): Birth time in 'HH:MM:SS' format
        tz_offset (float): Timezone offset from UTC in hours
    Returns:
        float: Julian Day in UT
    """
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        time_obj = datetime.strptime(time_str, '%H:%M:%S')
        local_dt = datetime.combine(date_obj, time_obj.time())
        ut_dt = local_dt - timedelta(hours=tz_offset)
        hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
        return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal, swe.GREG_CAL)
    except ValueError as e:
        raise ValueError(f"Invalid date or time format: {str(e)}")

def calculate_planetary_positions(jd):
    """
    Calculate sidereal positions and retrograde status of planets using Lahiri Ayanamsa.
    Args:
        jd (float): Julian Day in UT
    Returns:
        dict: Planetary positions with longitudes and retrograde status
    """
    try:
        swe.set_sid_mode(swe.SIDM_RAMAN)
        planets = {
            'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS, 'Mercury': swe.MERCURY,
            'Jupiter': swe.JUPITER, 'Venus': swe.VENUS, 'Saturn': swe.SATURN,
            'Rahu': swe.MEAN_NODE, 'Ketu': None
        }
        positions = {}
        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
        
        for planet, pid in planets.items():
            if planet == 'Ketu':
                continue
            pos, ret = swe.calc_ut(jd, pid, flags)
            if ret < 0:
                raise ValueError(f"Error calculating position for {planet}")
            longitude = pos[0] % 360.0
            speed = pos[3]  # Longitudinal speed in degrees per day
            # Determine retrograde status
            if planet in ['Sun', 'Moon']:
                retrograde = False  # Sun and Moon are never retrograde
            elif planet == 'Rahu':
                retrograde = True   # Rahu is always retrograde in Vedic astrology
            else:
                retrograde = speed < 0  # Negative speed indicates retrograde motion
            positions[planet] = (longitude, retrograde)
        
        # Ketu: 180° opposite Rahu, always retrograde
        rahu_lon = positions['Rahu'][0]
        ketu_lon = (rahu_lon + 180.0) % 360.0
        positions['Ketu'] = (ketu_lon, True)
        return positions
    except Exception as e:
        raise Exception(f"Planetary calculation failed: {str(e)}")

def calculate_whole_sign_cusps(sun_longitude):
    """
    Calculate house cusps for the Sun Chart using Whole Sign system.
    Args:
        sun_longitude (float): Sun's sidereal longitude in degrees
    Returns:
        list: 12 house cusps in degrees
    """
    sun_sign_index = int(sun_longitude // 30)
    # Whole Sign cusps: Start at the Sun's sign, each house spans 30°
    house_cusps = [(sun_sign_index * 30 + i * 30) % 360 for i in range(12)]
    return house_cusps

def assign_planets_to_houses(planetary_positions, sun_sign_index):
    """
    Assign planets to houses in the Sun Chart using Whole Sign system.
    Args:
        planetary_positions (dict): Planetary longitudes and retrograde statuses
        sun_sign_index (int): Index of Sun's sign (0=Aries, 11=Pisces)
    Returns:
        dict: House assignments for each planet
    """
    house_assignments = {}
    for planet, (longitude, _) in planetary_positions.items():
        planet_sign_index = int(longitude // 30)
        house = (planet_sign_index - sun_sign_index) % 12 + 1
        house_assignments[planet] = house
    return house_assignments

def format_dms(degrees):
    """
    Format degrees into degrees, minutes, and seconds with high precision.
    Args:
        degrees (float): Angle in decimal degrees
    Returns:
        str: Formatted string (e.g., "1° 20' 0.00\"")
    """
    degrees = degrees % 360.0
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = ((degrees - d) * 60 - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def validate_input(data):
    """
    Validate input JSON data.
    Args:
        data (dict): Input JSON data
    Raises:
        ValueError: If validation fails
    """
    required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
    if not all(key in data for key in required_fields):
        raise ValueError("Missing required parameters")
    latitude = float(data['latitude'])
    longitude = float(data['longitude'])
    if not (-90 <= latitude <= 90):
        raise ValueError("Latitude must be between -90 and 90 degrees")
    if not (-180 <= longitude <= 180):
        raise ValueError("Longitude must be between -180 and 180 degrees")

def get_nakshatra(longitude):
    """
    Calculate the nakshatra (star) based on longitude.
    Args:
        longitude (float): Longitude in degrees (0–360°)
    Returns:
        str: Nakshatra name
    """
    nakshatra_index = int(longitude / (360 / 27)) % 27
    return NAKSHATRAS[nakshatra_index]

def raman_sun(data):
    """
    Calculate Sun Chart (sidereal) with Whole Sign house system using Raman Ayanamsa.
    Args:
        data (dict): Input JSON data
    Returns:
        dict: Sun Chart data with Surya Lagna, house cusps, planetary positions, and nakshatras
    """
    # Validate input
    validate_input(data)
    
    # Extract input data
    user_name = data.get('user_name', 'Unknown')
    birth_date = data['birth_date']
    birth_time = data['birth_time']
    latitude = float(data['latitude'])
    longitude = float(data['longitude'])
    tz_offset = float(data['timezone_offset'])

    # Calculate Julian Day
    jd = get_julian_day(birth_date, birth_time, tz_offset)

    # Calculate planetary positions with retrograde status
    planetary_positions = calculate_planetary_positions(jd)

    # Sun's position (Surya Lagna)
    sun_longitude = planetary_positions['Sun'][0]
    sun_sign_index = int(sun_longitude // 30)
    sun_sign = SIGNS[sun_sign_index]
    sun_degree = sun_longitude % 30

    # Calculate house cusps for Sun Chart (Whole Sign)
    house_cusps = calculate_whole_sign_cusps(sun_longitude)

    # Assign planets to houses in Sun Chart
    house_assignments = assign_planets_to_houses(planetary_positions, sun_sign_index)

    # Prepare house cusps data
    house_data = [
        {
            "house": i + 1,
            "cusp": format_dms(house_cusps[i]),
            "sign": SIGNS[(sun_sign_index + i) % 12]
        }
        for i in range(12)
    ]

    # Prepare planetary positions data with retrograde status and nakshatras
    planetary_data = [
        {
            "planet": planet,
            "longitude": format_dms(longitude),
            "sign": SIGNS[int(longitude // 30)],
            "retrograde": retrograde,
            "house": house_assignments[planet],
            "nakshatra": get_nakshatra(longitude)
        }
        for planet, (longitude, retrograde) in planetary_positions.items()
    ]

    # Surya Lagna nakshatra
    surya_lagna_nakshatra = get_nakshatra(sun_longitude)

    # Construct response
    response = {
        "user_name": user_name,
        "surya_lagna": {
            "longitude": format_dms(sun_longitude),
            "sign": sun_sign,
            "degree": format_dms(sun_degree),
            "nakshatra": surya_lagna_nakshatra
        },
        "house_cusps": house_data,
        "planetary_positions": planetary_data,
        "metadata": {
            "ayanamsa": "Raman",  # Corrected to Raman as per swe.set_sid_mode
            "house_system": "Whole Sign",
            "calculation_time": datetime.utcnow().isoformat(),
            "input": {
                "birth_date": birth_date,
                "birth_time": birth_time,
                "latitude": latitude,
                "longitude": longitude,
                "timezone_offset": tz_offset
            }
        }
    }
    return response
import swisseph as swe
from datetime import datetime, timedelta

# Define zodiac signs
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

def get_julian_day(date_str, time_str, tz_offset):
    """
    Convert local birth date and time to Julian Day in Universal Time (UT).
    
    Args:
        date_str (str): Birth date in 'YYYY-MM-DD' format
        time_str (str): Birth time in 'HH:MM:SS' format
        tz_offset (float): Timezone offset in hours (e.g., 5.5 for IST)
    
    Returns:
        float: Julian Day for the UT time
    """
    local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    ut_dt = local_dt - timedelta(hours=tz_offset)
    hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
    return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal, swe.GREG_CAL)

def calculate_sidereal_positions(jd, latitude, longitude):
    """
    Calculate sidereal longitudes of planets and ascendant using Lahiri Ayanamsa.
    
    Args:
        jd (float): Julian Day in UT
        latitude (float): Latitude of birth place in degrees
        longitude (float): Longitude of birth place in degrees
    
    Returns:
        dict: Sidereal longitudes of planets and ascendant
    """
    swe.set_sid_mode(swe.SIDM_LAHIRI)  # Set Lahiri Ayanamsa
    positions = {}
    planet_ids = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY, "Venus": swe.VENUS,
        "Mars": swe.MARS, "Jupiter": swe.JUPITER, "Saturn": swe.SATURN,
        "Rahu": swe.MEAN_NODE, "Ketu": (swe.MEAN_NODE, 180)  # Ketu is 180° from Rahu
    }
    
    # Calculate planetary positions
    for planet, pid in planet_ids.items():
        if planet == "Ketu":
            rahu_pos = swe.calc_ut(jd, pid[0], swe.FLG_SIDEREAL)[0][0]
            positions[planet] = (rahu_pos + pid[1]) % 360
        else:
            pos = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL)[0][0]
            positions[planet] = pos % 360
    
    # Calculate ascendant
    _, ascmc = swe.houses_ex(jd, latitude, longitude, b'W', swe.FLG_SIDEREAL)  # 'W' for whole sign
    positions["Ascendant"] = ascmc[0] % 360
    
    return positions

def get_sign(longitude):
    """
    Determine the zodiac sign and degree within the sign from longitude.
    
    Args:
        longitude (float): Sidereal longitude in degrees
    
    Returns:
        tuple: (sign name, degrees within sign)
    """
    sign_idx = int(longitude // 30)
    return SIGNS[sign_idx], longitude % 30

def generate_chart(positions, reference_sign_idx):
    """
    Generate a chart (Lagna, Chandra, or Surya) using the whole sign house system.
    
    Args:
        positions (dict): Sidereal longitudes of planets and ascendant
        reference_sign_idx (int): Index of the reference sign (0-11)
    
    Returns:
        dict: Chart with house numbers mapped to signs and planets
    """
    chart = {sign: [] for sign in SIGNS}
    for planet, lon in positions.items():
        sign, _ = get_sign(lon)
        chart[sign].append(planet)
    
    # Assign house numbers relative to the reference sign
    house_chart = {}
    for i, sign in enumerate(SIGNS):
        house_num = (i - reference_sign_idx) % 12 + 1
        house_chart[house_num] = {"sign": sign, "planets": chart[sign]}
    return house_chart
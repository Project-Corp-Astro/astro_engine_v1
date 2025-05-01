import swisseph as swe
from datetime import datetime, timedelta

# Constants
SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
PLANET_IDS = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS, 'Mercury': swe.MERCURY,
    'Jupiter': swe.JUPITER, 'Venus': swe.VENUS, 'Saturn': swe.SATURN,
    'Rahu': swe.MEAN_NODE, 'Ketu': None  # Ketu calculated from Rahu
}

def get_julian_day(date_str, time_str, tz_offset):
    """Convert local date and time to Julian Day (UT)."""
    try:
        dt = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M:%S')
        ut_dt = dt - timedelta(hours=tz_offset)
        jd = swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, ut_dt.hour + ut_dt.minute / 60.0 + ut_dt.second / 3600.0)
        return jd
    except ValueError as e:
        raise ValueError(f"Invalid date or time format: {str(e)}")

def calculate_sunrise(jd, lat, lon, tz_offset):
    """Calculate sunrise time and Sun's longitude at sunrise with fallback."""
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise ValueError(f"Invalid coordinates: lat={lat}, lon={lon}")

    geopos = [lon, lat, 0.0]  # [longitude, latitude, elevation]
    flags = swe.CALC_RISE | swe.BIT_DISC_CENTER | swe.BIT_NO_REFRACTION

    # Try sunrise calculation for ±3 days
    for offset in range(-3, 4):
        search_jd = jd + offset
        try:
            ret, t_rise = swe.rise_trans(search_jd - 1.0, swe.SUN, geopos, flags=flags)
            if ret == 0 and t_rise[0] is not None:
                sunrise_jd = t_rise[0]
                sun_lon = swe.calc_ut(sunrise_jd, swe.SUN, swe.FLG_SIDEREAL)[0][0] % 360
                return sunrise_jd, sun_lon
        except Exception:
            pass  # Continue to next offset

    # Fallback: Approximate sunrise as 6 AM local time
    try:
        dt = datetime.strptime(f"{jd_to_date(jd)} 06:00:00", '%Y-%m-%d %H:%M:%S')
        sunrise_jd = swe.julday(dt.year, dt.month, dt.day, 6.0 - tz_offset)
        sun_lon = swe.calc_ut(sunrise_jd, swe.SUN, swe.FLG_SIDEREAL)[0][0] % 360
        return sunrise_jd, sun_lon
    except Exception as e:
        raise ValueError(f"Unable to calculate sunrise time after multiple attempts: {str(e)}")

def calculate_bhava_lagna(birth_jd, sunrise_jd, sunrise_sun_lon):
    """Calculate Bhava Lagna longitude."""
    time_elapsed = (birth_jd - sunrise_jd) * 1440  # Convert days to minutes
    if time_elapsed < 0:
        time_elapsed += 1440  # Adjust for birth before sunrise
    degrees_progressed = time_elapsed / 4.0  # 1° per 4 minutes
    bl_lon = (sunrise_sun_lon + degrees_progressed) % 360
    return bl_lon

def get_sign_and_degrees(longitude):
    """Convert longitude to sign and degrees."""
    sign_index = int(longitude // 30)
    degrees = longitude % 30
    return SIGNS[sign_index % 12], degrees

def calculate_house(planet_sign, bl_sign):
    """Assign house using Whole Sign system."""
    planet_index = SIGNS.index(planet_sign)
    bl_index = SIGNS.index(bl_sign)
    return (planet_index - bl_index) % 12 + 1

def jd_to_date(jd):
    """Convert Julian Day to date string (YYYY-MM-DD)."""
    y, m, d, _ = swe.revjul(jd)
    return f"{y:04d}-{m:02d}-{d:02d}"
import swisseph as swe
from datetime import datetime, timedelta
import math

# Constants
ZODIAC_SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
PLANETS = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu', 'Uranus', 'Neptune', 'Pluto']
SWE_PLANETS = [swe.SUN, swe.MOON, swe.MARS, swe.MERCURY, swe.JUPITER, swe.VENUS, swe.SATURN, swe.MEAN_NODE, swe.MEAN_NODE, swe.URANUS, swe.NEPTUNE, swe.PLUTO]
NAKSHATRAS = ['Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra', 'Punarvasu', 'Pushya', 'Ashlesha',
              'Magha', 'Purva Phalguni', 'Uttara Phalguni', 'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshta',
              'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta', 'Shatabhisha', 'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati']
STAR_LORDS = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury'] * 3
VIMSHOTTARI_PROPORTIONS = {'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10, 'Mars': 7, 'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17}
NAKSHATRA_SPAN = 13 + 1/3  # 13 degrees 20 minutes (13.333333 degrees)

def cupsal_get_julian_day(birth_date, birth_time, tz_offset):
    """Convert birth date and time to Julian Day with timezone adjustment."""
    local_dt = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M:%S")
    ut_dt = local_dt - timedelta(hours=tz_offset)
    return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, ut_dt.hour + ut_dt.minute / 60.0 + ut_dt.second / 3600.0)

def cupsal_calculate_kp_new_ayanamsa(jd):
    """Calculate KP New Ayanamsa for the given Julian Day."""
    ref_jd = swe.julday(291, 4, 15, 0)  # Reference date: 15th April 291 CE
    precession_rate = 50.2388475 / 3600.0  # Arcseconds to degrees
    years_elapsed = (jd - ref_jd) / 365.25
    return years_elapsed * precession_rate

def cupsal_calculate_ascendant_and_cusps(jd, latitude, longitude, kp_new_ayanamsa):
    """Calculate Ascendant and house cusps using Placidus system with KP New Ayanamsa."""
    houses = swe.houses_ex(jd, latitude, longitude, hsys=b'P')  # Placidus house system
    ascendant = (houses[0][0] - kp_new_ayanamsa) % 360
    house_cusps = [(cusp - kp_new_ayanamsa) % 360 for cusp in houses[0][:12]]
    return ascendant, house_cusps

def cupsal_calculate_planet_positions(jd, kp_new_ayanamsa):
    """Calculate sidereal positions of planets using KP New Ayanamsa."""
    positions = {}
    for planet, code in zip(PLANETS, SWE_PLANETS):
        if planet == 'Ketu':
            rahu_lon = positions['Rahu']
            ketu_lon = (rahu_lon + 180) % 360  # Ketu is 180° opposite to Rahu
            positions['Ketu'] = ketu_lon
        else:
            pos = swe.calc_ut(jd, code)[0][0]  # Tropical position
            sidereal_pos = (pos - kp_new_ayanamsa) % 360
            positions[planet] = sidereal_pos
    return positions

def cupsal_assign_nakshatra_and_lords(longitude):
    """Assign Nakshatra, star lord, and sub-lord to a longitude."""
    nakshatra_index = int(longitude / NAKSHATRA_SPAN)
    nakshatra = NAKSHATRAS[nakshatra_index % 27]
    star_lord = STAR_LORDS[nakshatra_index % 27]
    remaining_minutes = (longitude % NAKSHATRA_SPAN) * 60  # Convert remaining degrees to minutes
    sub_lord = cupsal_calculate_sub_lord(remaining_minutes)
    return nakshatra, star_lord, sub_lord

def cupsal_calculate_sub_lord(remaining_minutes):
    """Calculate sub-lord based on remaining longitude within Nakshatra."""
    total_minutes = NAKSHATRA_SPAN * 60  # 800 minutes per Nakshatra
    sub_lords = list(VIMSHOTTARI_PROPORTIONS.keys())
    sub_spans = [VIMSHOTTARI_PROPORTIONS[lord] / 120 * total_minutes for lord in sub_lords]
    cumulative = 0
    for i, span in enumerate(sub_spans):
        cumulative += span
        if remaining_minutes <= cumulative:
            return sub_lords[i]
    return sub_lords[-1]  # Fallback to last sub-lord

def cupsal_assign_planet_to_house(planet_lon, house_cusps):
    """Assign planet to house based on house cusps."""
    for i in range(12):
        cusp_start = house_cusps[i]
        cusp_end = house_cusps[(i + 1) % 12]
        if cusp_end < cusp_start:  # Handle zodiac boundary crossing
            if planet_lon >= cusp_start or planet_lon < cusp_end:
                return i + 1
        else:
            if cusp_start <= planet_lon < cusp_end:
                return i + 1
    return 12  # Fallback to 12th house

def cupsal_calculate_significators(planets, house_cusps):
    """Calculate significators for each house based on KP rules."""
    significators = {i: {'A': [], 'B': [], 'C': [], 'D': []} for i in range(1, 13)}
    house_lords = {
        'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury', 'Cancer': 'Moon', 'Leo': 'Sun',
        'Virgo': 'Mercury', 'Libra': 'Venus', 'Scorpio': 'Mars', 'Sagittarius': 'Jupiter',
        'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
    }
    
    for house in range(1, 13):
        cusp_start = house_cusps[house - 1]
        sign = ZODIAC_SIGNS[int(cusp_start // 30)]
        
        # Level A: Planets in the house
        for planet, lon in planets.items():
            house_number = cupsal_assign_planet_to_house(lon, house_cusps)
            if house_number == house:
                significators[house]['A'].append(planet)
        
        # Level C: House lord
        significators[house]['C'].append(house_lords[sign])
        
        # Level B: Planets in the star of occupants
        for planet, lon in planets.items():
            _, star_lord, _ = cupsal_assign_nakshatra_and_lords(lon)
            if planet in significators[house]['A'] and star_lord not in significators[house]['B']:
                significators[house]['B'].append(star_lord)
        
        # Level D: Planets in the star of house lord
        for planet, lon in planets.items():
            _, star_lord, _ = cupsal_assign_nakshatra_and_lords(lon)
            if significators[house]['C'][0] == star_lord and planet not in significators[house]['D']:
                significators[house]['D'].append(planet)
    
    return significators

def cupsal_format_dms(degrees):
    """Convert decimal degrees to degrees, minutes, seconds format."""
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = int(((degrees - d) * 60 - m) * 60)
    return f"{d}° {m}' {s}\""
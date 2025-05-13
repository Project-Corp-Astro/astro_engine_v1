import swisseph as swe
from datetime import datetime, timedelta

# Constants
PLANETS = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
PLANET_IDS = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS, 'Mercury': swe.MERCURY,
    'Jupiter': swe.JUPITER, 'Venus': swe.VENUS, 'Saturn': swe.SATURN, 'Rahu': swe.MEAN_NODE
}
SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
SIGN_RULERS = {
    'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury', 'Cancer': 'Moon', 'Leo': 'Sun',
    'Virgo': 'Mercury', 'Libra': 'Venus', 'Scorpio': 'Mars', 'Sagittarius': 'Jupiter',
    'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
}
NAKSHATRAS = ['Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra', 'Punarvasu', 'Pushya', 'Ashlesha',
              'Magha', 'Purva Phalguni', 'Uttara Phalguni', 'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshta',
              'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta', 'Shatabhisha', 'Purva Bhadrapada',
              'Uttara Bhadrapada', 'Revati']
NAKSHATRA_LORDS = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury'] * 3
NAKSHATRA_SPAN = 360 / 27  # 13.3333 degrees per nakshatra

# Utility Functions
def get_sign(longitude):
    """Determine the zodiac sign from a longitude (0-360 degrees)."""
    sign_index = int(longitude / 30) % 12
    return SIGNS[sign_index]

def get_nakshatra(longitude):
    """Determine the nakshatra and its lord from a longitude."""
    nak_index = int(longitude / NAKSHATRA_SPAN) % 27
    nakshatra = NAKSHATRAS[nak_index]
    lord = NAKSHATRA_LORDS[nak_index]
    return nakshatra, lord

def get_house(longitude, cusps):
    """Determine the house a planet falls into based on Placidus house cusps."""
    for i in range(12):
        cusp1 = cusps[i]
        cusp2 = cusps[(i + 1) % 12]
        if cusp2 < cusp1:  # Handle zodiac crossing (e.g., 360° to 0°)
            if longitude >= cusp1 or longitude < cusp2:
                return i + 1
        elif cusp1 <= longitude < cusp2:
            return i + 1
    return 12  # Default to 12th house if no match

def calculate_planets_significations(birth_date, birth_time, latitude, longitude, timezone_offset):
    """Calculate house significations based on KP Astrology rules."""
    # Convert local time to UTC
    local_dt = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M:%S")
    utc_dt = local_dt - timedelta(hours=timezone_offset)

    # Calculate Julian Day for Swiss Ephemeris
    hour_decimal = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_decimal)

    # Set KP New Ayanamsa (Krishnamurti)
    swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)

    # Calculate Placidus house cusps
    cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b'P', flags=swe.FLG_SIDEREAL)
    house_cusps = cusps[:12]  # First 12 are house cusps

    # Calculate sidereal planetary positions
    positions = {}
    for planet in PLANETS[:-1]:  # Exclude Ketu initially
        pos = swe.calc_ut(jd, PLANET_IDS[planet], swe.FLG_SIDEREAL)[0][0]  # Longitude only
        positions[planet] = pos
    positions['Ketu'] = (positions['Rahu'] + 180) % 360  # Ketu opposite Rahu

    # Determine house lords, occupants, and nakshatra details
    house_lords = {}
    house_occupants = {i: [] for i in range(1, 13)}
    cusp_details = {}
    planet_details = {}

    # Calculate cusp details (sign, nakshatra, nakshatra lord)
    for house in range(1, 13):
        cusp_long = house_cusps[house - 1]
        cusp_sign = get_sign(cusp_long)
        house_lords[house] = SIGN_RULERS[cusp_sign]
        nakshatra, nak_lord = get_nakshatra(cusp_long)
        cusp_details[house] = {
            'longitude': cusp_long,
            'sign': cusp_sign,
            'nakshatra': nakshatra,
            'nakshatra_lord': nak_lord
        }

    # Calculate planet details (house, nakshatra, nakshatra lord)
    for planet in PLANETS:
        planet_long = positions[planet]
        house = get_house(planet_long, house_cusps)
        house_occupants[house].append(planet)
        nakshatra, nak_lord = get_nakshatra(planet_long)
        planet_details[planet] = {
            'longitude': planet_long,
            'house': house,
            'nakshatra': nakshatra,
            'nakshatra_lord': nak_lord
        }

    # Calculate significators for each house
    significators = {}
    for house in range(1, 13):
        # Primary significators: occupants
        occupants = house_occupants[house]
        # Secondary significators: lord of the house
        lord = house_lords[house]
        # Tertiary significators: planets in the nakshatra of occupants or lord
        nakshatra_planets = []
        for planet in PLANETS:
            nak_lord = planet_details[planet]['nakshatra_lord']
            if nak_lord in occupants or nak_lord == lord:
                nakshatra_planets.append(planet)
        # Compile significators with cusp details
        significators[house] = {
            'cusp': {
                'longitude': cusp_details[house]['longitude'],
                'sign': cusp_details[house]['sign'],
                'nakshatra': cusp_details[house]['nakshatra'],
                'nakshatra_lord': cusp_details[house]['nakshatra_lord']
            },
            'occupants': occupants,
            'lord': lord,
            'nakshatra_planets': list(set(nakshatra_planets))  # Remove duplicates
        }

    return significators
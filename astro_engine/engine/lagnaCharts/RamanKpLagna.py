import swisseph as swe
from math import floor
from datetime import datetime, timedelta

# Set Swiss Ephemeris path
swe.set_ephe_path('astro_api/ephe')

# Define constants
PLANETS = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
NAKSHATRAS = [
    ('Ashwini', 0, 13.3333), ('Bharani', 13.3333, 26.6667), ('Krittika', 26.6667, 40),
    ('Rohini', 40, 53.3333), ('Mrigashira', 53.3333, 66.6667), ('Ardra', 66.6667, 80),
    ('Punarvasu', 80, 93.3333), ('Pushya', 93.3333, 106.6667), ('Ashlesha', 106.6667, 120),
    ('Magha', 120, 133.3333), ('Purva Phalguni', 133.3333, 146.6667), ('Uttara Phalguni', 146.6667, 160),
    ('Hasta', 160, 173.3333), ('Chitra', 173.3333, 186.6667), ('Swati', 186.6667, 200),
    ('Vishakha', 200, 213.3333), ('Anuradha', 213.3333, 226.6667), ('Jyeshtha', 226.6667, 240),
    ('Mula', 240, 253.3333), ('Purva Ashadha', 253.3333, 266.6667), ('Uttara Ashadha', 266.6667, 280),
    ('Shravana', 280, 293.3333), ('Dhanishta', 293.3333, 306.6667), ('Shatabhisha', 306.6667, 320),
    ('Purva Bhadrapada', 320, 333.3333), ('Uttara Bhadrapada', 333.3333, 346.6667), ('Revati', 346.6667, 360)
]
SUB_LORD_PROPORTIONS = [
    ('Ketu', 0.7778), ('Venus', 2.2222), ('Sun', 0.6667), ('Moon', 1.1111),
    ('Mars', 0.7778), ('Rahu', 2.0000), ('Jupiter', 1.7778), ('Saturn', 2.1111),
    ('Mercury', 1.8889)
]
SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

def get_julian_day(date_str, time_str, tz_offset):
    """Convert local birth date and time to Julian Day in UT."""
    local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    ut_dt = local_dt - timedelta(hours=tz_offset)
    hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
    return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal, swe.GREG_CAL)

def calculate_planet_positions(jd):
    """Calculate sidereal positions of planets using Raman Ayanamsa, including Ketu and retrograde status."""
    swe.set_sid_mode(swe.SIDM_RAMAN)
    planet_ids = {
        'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS, 'Mercury': swe.MERCURY,
        'Jupiter': swe.JUPITER, 'Venus': swe.VENUS, 'Saturn': swe.SATURN, 'Rahu': swe.MEAN_NODE
    }
    positions = {}
    for planet, pid in planet_ids.items():
        result = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL)
        positions[planet] = result[0][0] % 360
        speed = result[0][3]  # Speed in longitude
        positions[planet + '_retro'] = speed < 0
    
    positions['Ketu'] = (positions['Rahu'] + 180) % 360
    positions['Ketu_retro'] = positions['Rahu_retro']
    
    return positions

def calculate_house_cusps(jd, latitude, longitude):
    """Calculate sidereal house cusps using Placidus house system with Raman Ayanamsa."""
    swe.set_sid_mode(swe.SIDM_RAMAN)
    house_pos = swe.houses_ex(jd, latitude, longitude, b'P', flags=swe.FLG_SIDEREAL)
    cusps = [cusp % 360 for cusp in house_pos[0]]
    return cusps

def get_sign(longitude):
    """Get zodiac sign based on longitude."""
    sign_index = floor(longitude / 30) % 12
    return SIGNS[sign_index]

def get_nakshatra(longitude):
    """Get nakshatra name based on longitude."""
    for nakshatra, start, end in NAKSHATRAS:
        if start <= longitude < end:
            return nakshatra
    return 'Revati' if longitude >= 346.6667 else 'Ashwini'

def get_nakshatra_pada(longitude):
    """Get nakshatra and pada based on longitude."""
    longitude = longitude % 360
    pada_size = 360 / 108  # 3.3333° per pada
    pada_index = floor(longitude / pada_size)
    nakshatra_index = pada_index // 4
    pada_number = (pada_index % 4) + 1
    nakshatra = NAKSHATRAS[nakshatra_index][0]
    return nakshatra, pada_number

def get_sub_lord(longitude):
    """Get sub-lord based on longitude within nakshatra."""
    nakshatra_span = 13.3333
    nakshatra_start = floor(longitude / nakshatra_span) * nakshatra_span
    progress = longitude - nakshatra_start
    cumulative = 0
    for sub_lord, proportion in SUB_LORD_PROPORTIONS:
        cumulative += proportion
        if progress <= cumulative:
            return sub_lord
    return 'Mercury'

def assign_planets_to_houses(planet_positions, house_cusps):
    """Assign planets to houses based on their positions and house cusp ranges."""
    house_assignments = {}
    for planet, pos in planet_positions.items():
        if planet.endswith('_retro'):
            continue
        for i in range(12):
            cusp_start = house_cusps[i]
            cusp_end = house_cusps[(i + 1) % 12]
            if cusp_end > cusp_start:
                if cusp_start <= pos < cusp_end:
                    house_assignments[planet] = i + 1
                    break
            else:
                if pos >= cusp_start or pos < cusp_end:
                    house_assignments[planet] = i + 1
                    break
    return house_assignments

def calculate_significators(planet_positions, house_cusps):
    """Calculate significators for each house based on KP rules."""
    significators = {f"House {i+1}": [] for i in range(12)}
    house_assignments = assign_planets_to_houses(planet_positions, house_cusps)
    
    sign_lords = {
        'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury', 'Cancer': 'Moon',
        'Leo': 'Sun', 'Virgo': 'Mercury', 'Libra': 'Venus', 'Scorpio': 'Mars',
        'Sagittarius': 'Jupiter', 'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
    }
    
    nakshatra_lords = {
        'Ashwini': 'Ketu', 'Bharani': 'Venus', 'Krittika': 'Sun', 'Rohini': 'Moon',
        'Mrigashira': 'Mars', 'Ardra': 'Rahu', 'Punarvasu': 'Jupiter', 'Pushya': 'Saturn',
        'Ashlesha': 'Mercury', 'Magha': 'Ketu', 'Purva Phalguni': 'Venus', 'Uttara Phalguni': 'Sun',
        'Hasta': 'Moon', 'Chitra': 'Mars', 'Swati': 'Rahu', 'Vishakha': 'Jupiter',
        'Anuradha': 'Saturn', 'Jyeshtha': 'Mercury', 'Mula': 'Ketu', 'Purva Ashadha': 'Venus',
        'Uttara Ashadha': 'Sun', 'Shravana': 'Moon', 'Dhanishta': 'Mars', 'Shatabhisha': 'Rahu',
        'Purva Bhadrapada': 'Jupiter', 'Uttara Bhadrapada': 'Saturn', 'Revati': 'Mercury'
    }
    
    for house in range(1, 13):
        house_key = f"House {house}"
        cusp_sign = get_sign(house_cusps[house - 1])
        house_lord = sign_lords[cusp_sign]
        
        for planet, house_num in house_assignments.items():
            if house_num == house:
                if planet not in significators[house_key]:
                    significators[house_key].append(planet)
        
        for planet in significators[house_key][:]:
            nak = get_nakshatra(planet_positions[planet])
            nak_lord = nakshatra_lords[nak]
            if nak_lord not in significators[house_key]:
                significators[house_key].append(nak_lord)
        
        if house_lord not in significators[house_key]:
            significators[house_key].append(house_lord)
        
        nak = get_nakshatra(planet_positions[house_lord])
        nak_lord = nakshatra_lords[nak]
        if nak_lord not in significators[house_key]:
            significators[house_key].append(nak_lord)
    
    return significators

def raman_kp_bava(user_name, birth_date, birth_time, latitude, longitude, tz_offset):
    """Calculate KP Bhava Chart with Raman ayanamsa, including retrograde, nakshatra, and pada."""
    jd = get_julian_day(birth_date, birth_time, tz_offset)
    planet_positions = calculate_planet_positions(jd)
    house_cusps = calculate_house_cusps(jd, latitude, longitude)
    house_assignments = assign_planets_to_houses(planet_positions, house_cusps)
    significators = calculate_significators(planet_positions, house_cusps)

    planet_details = {}
    for planet in PLANETS:
        pos = planet_positions[planet]
        nakshatra, pada = get_nakshatra_pada(pos)
        planet_details[planet] = {
            'longitude': round(pos, 4),
            'sign': get_sign(pos),
            'nakshatra': nakshatra,
            'pada': pada,
            'sub_lord': get_sub_lord(pos),
            'house': house_assignments.get(planet, None),
            'retrograde': planet_positions.get(f"{planet}_retro", False)
        }

    cusp_details = []
    for i, cusp in enumerate(house_cusps, 1):
        nakshatra, pada = get_nakshatra_pada(cusp)
        cusp_details.append({
            'house': i,
            'longitude': round(cusp, 4),
            'sign': get_sign(cusp),
            'nakshatra': nakshatra,
            'pada': pada,
            'sub_lord': get_sub_lord(cusp)
        })

    ascendant = {
        'longitude': cusp_details[0]['longitude'],
        'sign': cusp_details[0]['sign'],
        'nakshatra': cusp_details[0]['nakshatra'],
        'pada': cusp_details[0]['pada'],
        'sub_lord': cusp_details[0]['sub_lord']
    }

    response = {
        'user_name': user_name,
        'ascendant': ascendant,
        # 'house_cusps': cusp_details,
        'planetary_positions': planet_details,
        # 'significators': significators
    }
    return response
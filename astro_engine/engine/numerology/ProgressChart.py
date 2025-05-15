



import swisseph as swe
from datetime import datetime, timedelta
import math

# Set ephemeris path and sidereal mode to Lahiri ayanamsa
swe.set_ephe_path('astro_api/ephe')
swe.set_sid_mode(swe.SIDM_LAHIRI)

# Define planets and corresponding Swiss Ephemeris constants
PLANETS = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mercury': swe.MERCURY, 'Venus': swe.VENUS,
    'Mars': swe.MARS, 'Jupiter': swe.JUPITER, 'Saturn': swe.SATURN, 'Uranus': swe.URANUS,
    'Neptune': swe.NEPTUNE, 'Pluto': swe.PLUTO, 'North Node': swe.MEAN_NODE
}

# Sidereal zodiac signs
SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio',
         'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

# Nakshatras with their longitude ranges (start, end in degrees)
NAKSHATRAS = [
    ('Ashwini', 0, 13.3333),
    ('Bharani', 13.3333, 26.6667),
    ('Krittika', 26.6667, 40),
    ('Rohini', 40, 53.3333),
    ('Mrigashira', 53.3333, 66.6667),
    ('Ardra', 66.6667, 80),
    ('Punarvasu', 80, 93.3333),
    ('Pushya', 93.3333, 106.6667),
    ('Ashlesha', 106.6667, 120),
    ('Magha', 120, 133.3333),
    ('Purva Phalguni', 133.3333, 146.6667),
    ('Uttara Phalguni', 146.6667, 160),
    ('Hasta', 160, 173.3333),
    ('Chitra', 173.3333, 186.6667),
    ('Swati', 186.6667, 200),
    ('Vishakha', 200, 213.3333),
    ('Anuradha', 213.3333, 226.6667),
    ('Jyeshtha', 226.6667, 240),
    ('Mula', 240, 253.3333),
    ('Purva Ashadha', 253.3333, 266.6667),
    ('Uttara Ashadha', 266.6667, 280),
    ('Shravana', 280, 293.3333),
    ('Dhanishta', 293.3333, 306.6667),
    ('Shatabhisha', 306.6667, 320),
    ('Purva Bhadrapada', 320, 333.3333),
    ('Uttara Bhadrapada', 333.3333, 346.6667),
    ('Revati', 346.6667, 360)
]

# Original astrological interpretations (unchanged)
SUN_INTERPRETATIONS = {
    'Aries': "Your core essence radiates with courage and initiative, urging you to lead and forge new paths with confidence.",
    'Taurus': "A steady, grounded energy shapes your identity, drawing you toward security, beauty, and tangible achievements.",
    'Gemini': "Your spirit thrives on curiosity and versatility, encouraging exploration of ideas and meaningful connections.",
    'Cancer': "Emotional depth and care define your evolving self, fostering a strong pull toward home and inner peace.",
    'Leo': "A vibrant, creative force emerges, illuminating your path with self-assurance and a desire to shine brightly.",
    'Virgo': "Precision and purpose guide your growth, as you refine your skills and dedicate yourself to meaningful service.",
    'Libra': "Grace and collaboration become central, as you seek balance and cultivate harmony in relationships.",
    'Scorpio': "A profound transformation stirs within, driving you to uncover hidden truths and embrace intensity.",
    'Sagittarius': "Your soul expands with optimism and adventure, yearning for wisdom and broader perspectives.",
    'Capricorn': "Ambition and discipline carve your journey, as you build a lasting foundation with patience and resolve.",
    'Aquarius': "Innovation and individuality light your way, inspiring you to break free and envision a unique future.",
    'Pisces': "A gentle, intuitive energy flows through you, deepening your compassion and spiritual connection."
}

MOON_INTERPRETATIONS = {
    'Aries': "Your inner world burns with passion and spontaneity, craving independence and bold emotional expression.",
    'Taurus': "A calm, nurturing stillness settles within, as you seek comfort and stability in your emotional life.",
    'Gemini': "Restless curiosity stirs your feelings, drawing you to explore new experiences and share your thoughts.",
    'Cancer': "Your heart opens to tenderness and protection, finding solace in family and emotional security.",
    'Leo': "Warmth and drama color your emotions, as you embrace joy and seek acknowledgment of your inner light.",
    'Virgo': "A quiet pragmatism shapes your feelings, guiding you to care for others and perfect your daily life.",
    'Libra': "Your emotional realm seeks peace and partnership, flourishing in beauty and mutual understanding.",
    'Scorpio': "Deep, powerful emotions rise, pulling you toward transformation and the mysteries of the soul.",
    'Sagittarius': "A buoyant, free-spirited energy lifts your heart, as you chase freedom and emotional growth.",
    'Capricorn': "Your inner self grows resolute and focused, finding strength in responsibility and long-term goals.",
    'Aquarius': "Unconventional waves ripple through your emotions, urging you toward independence and collective ideals.",
    'Pisces': "A tide of empathy and dreams washes over you, attuning your heart to the subtle and the sacred."
}

ASCENDANT_INTERPRETATIONS = {
    'Aries': "You greet the world with fearless energy and determination, ready to initiate and assert your presence.",
    'Taurus': "A serene, dependable aura surrounds you, as you approach life with patience and a love for the tangible.",
    'Gemini': "Your presence sparkles with wit and adaptability, engaging others with lively curiosity and charm.",
    'Cancer': "A gentle, protective vibe defines your approach, as you connect with others through care and intuition.",
    'Leo': "You radiate confidence and charisma, stepping into life with a bold, theatrical flair.",
    'Virgo': "A thoughtful, meticulous energy marks your demeanor, reflecting a desire to serve and improve.",
    'Libra': "Grace and diplomacy shine in your interactions, as you seek to create harmony and connection.",
    'Scorpio': "An enigmatic, magnetic force shapes your persona, hinting at depth and transformative power.",
    'Sagittarius': "You exude enthusiasm and openness, approaching life as an adventure to be explored.",
    'Capricorn': "A serious, authoritative air defines you, as you present yourself with ambition and structure.",
    'Aquarius': "Your approach is fresh and forward-thinking, reflecting a spirit of innovation and independence.",
    'Pisces': "A dreamy, compassionate essence flows from you, inviting others into your world of sensitivity."
}

HOUSE_INTERPRETATIONS = {
    1: "Your identity and how you present yourself to the world take center stage.",
    2: "Material resources, personal values, and self-esteem become focal points.",
    3: "Communication, learning, and your immediate environment gain prominence.",
    4: "Roots, home life, and your emotional foundation grow in significance.",
    5: "Creativity, romance, and personal joy rise as key themes.",
    6: "Daily routines, health, and service to others come into focus.",
    7: "Relationships and partnerships shape your experiences deeply.",
    8: "Transformation, shared resources, and inner mysteries hold your attention.",
    9: "Higher learning, travel, and philosophical growth guide your path.",
    10: "Career, reputation, and public standing take priority.",
    11: "Friendships, aspirations, and community ties flourish.",
    12: "Spirituality, solitude, and the subconscious unfold quietly."
}

ASPECTS = {
    'Conjunction': {'angle': 0, 'orb': 8},
    'Sextile': {'angle': 60, 'orb': 6},
    'Square': {'angle': 90, 'orb': 8},
    'Trine': {'angle': 120, 'orb': 8},
    'Opposition': {'angle': 180, 'orb': 8}
}

ASPECT_INTERPRETATIONS = {
    'Conjunction': "Energies merge intensely, creating a potent fusion that amplifies both strengths and challenges.",
    'Sextile': "A gentle harmony offers opportunities for growth, blending talents with ease and grace.",
    'Square': "Tension sparks dynamic growth, urging you to resolve conflicts and harness resilience.",
    'Trine': "A natural flow of support blesses you, bringing effortless alignment and positive momentum.",
    'Opposition': "Polarities call for balance, challenging you to integrate opposites for greater wholeness."
}

# Original calculation functions (unchanged)
def get_julian_day(date_str, time_str, tz_offset):
    """Convert date, time, and timezone offset to Julian Day."""
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    dt_utc = dt - timedelta(hours=tz_offset)
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                      dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0)

def format_position(longitude):
    """Format celestial longitude into sign, degrees, minutes, and seconds."""
    longitude = longitude % 360
    sign_idx = int(longitude // 30)
    sign = SIGNS[sign_idx]
    degree = longitude % 30
    d = int(degree)
    m = int((degree - d) * 60)
    s = int(((degree - d) * 60 - m) * 60)
    return {
        'longitude': longitude,
        'sign': sign,
        'degree': f"{d}° {m}' {s}\""
    }

def calculate_planetary_positions(jd):
    """Compute sidereal positions of planets for a given Julian Day."""
    positions = {}
    for planet_name, planet_id in PLANETS.items():
        result = swe.calc_ut(jd, planet_id, swe.FLG_SIDEREAL)
        lon = result[0][0]
        positions[planet_name] = format_position(lon)
    nn_lon = positions['North Node']['longitude']
    sn_lon = (nn_lon + 180) % 360
    positions['South Node'] = format_position(sn_lon)
    return positions

def calculate_angles(jd, lat, lon):
    """Determine progressed Ascendant and Midheaven."""
    house_cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', flags=swe.FLG_SIDEREAL)
    asc = ascmc[0] % 360
    mc = ascmc[1] % 360
    return asc, mc

def get_whole_sign_cusps(asc):
    """Generate whole sign house cusps based on Ascendant."""
    asc_sign_idx = int(asc // 30)
    cusps = {}
    for i in range(12):
        sign_idx = (asc_sign_idx + i) % 12
        cusp_lon = sign_idx * 30
        cusps[f'House {i+1}'] = format_position(cusp_lon)
    return cusps

def assign_planets_to_houses(positions, asc_sign_idx):
    """Place planets into whole sign houses."""
    houses = {}
    for planet, data in positions.items():
        longitude = data['longitude']
        planet_sign_idx = int(longitude // 30)
        house = (planet_sign_idx - asc_sign_idx) % 12 + 1
        houses[planet] = house
    return houses

def interpret_sun(sign, house):
    """Provide an interpretation for the progressed Sun."""
    sign_interp = SUN_INTERPRETATIONS.get(sign, "Your essence evolves in a distinctive, personal way.")
    house_interp = HOUSE_INTERPRETATIONS.get(house, "A unique life area shapes your journey.")
    return f"Progressed Sun in {sign} (House {house}): {sign_interp} {house_interp}"

def interpret_moon(sign, house):
    """Provide an interpretation for the progressed Moon."""
    sign_interp = MOON_INTERPRETATIONS.get(sign, "Your emotions shift in a subtle, personal rhythm.")
    house_interp = HOUSE_INTERPRETATIONS.get(house, "A distinct focus colors your inner life.")
    return f"Progressed Moon in {sign} (House {house}): {sign_interp} {house_interp}"

def interpret_ascendant(sign):
    """Provide an interpretation for the progressed Ascendant."""
    interp = ASCENDANT_INTERPRETATIONS.get(sign, "Your outward self evolves uniquely.")
    return f"Progressed Ascendant in {sign}: {interp}"

def calculate_aspects(prog_positions, natal_positions):
    """Identify major aspects between progressed and natal planets."""
    aspects = []
    for prog_planet, prog_data in prog_positions.items():
        if prog_planet in ['Sun', 'Moon']:  # Focus on key progressed planets
            prog_lon = prog_data['longitude']
            for natal_planet, natal_data in natal_positions.items():
                natal_lon = natal_data['longitude']
                diff = min(abs(prog_lon - natal_lon), 360 - abs(prog_lon - natal_lon))
                for aspect, data in ASPECTS.items():
                    if abs(diff - data['angle']) <= data['orb']:
                        aspects.append({
                            'prog_planet': prog_planet,
                            'natal_planet': natal_planet,
                            'aspect': aspect,
                            'angle': diff
                        })
    return aspects

def interpret_aspects(aspects):
    """Generate detailed interpretations for aspects."""
    interpretations = []
    for aspect in aspects:
        prog = aspect['prog_planet']
        natal = aspect['natal_planet']
        asp_type = aspect['aspect']
        interp = ASPECT_INTERPRETATIONS.get(asp_type, "A meaningful connection influences your path.")
        interpretations.append(f"Progressed {prog} {asp_type} Natal {natal}: {interp}")
    return interpretations

# New function to calculate nakshatra and pada
def get_nakshatra_pada(longitude):
    """Calculate nakshatra and pada for a given longitude."""
    longitude = longitude % 360
    for name, start, end in NAKSHATRAS:
        if start <= longitude < end:
            position_in_nakshatra = longitude - start
            pada = math.ceil(position_in_nakshatra / 3.3333)  # Each pada is 3°20' (3.3333°)
            return name, pada
    if math.isclose(longitude, 360, rel_tol=1e-5):
        return 'Revati', 4
    raise ValueError(f"Longitude {longitude} not in any nakshatra range")

# Main function as requested
def lahairi_progress(birth_date, birth_time, latitude, longitude, tz_offset, age):
    """Calculate progressed chart data with retrograde, nakshatras, and padas."""
    # Calculate Julian Days
    natal_jd = get_julian_day(birth_date, birth_time, tz_offset)
    progressed_jd = natal_jd + age  # Secondary progression: 1 day = 1 year
    
    # Compute natal positions (unchanged)
    natal_positions = calculate_planetary_positions(natal_jd)
    
    # Compute progressed positions with retrograde, nakshatra, and pada
    prog_positions = {}
    for planet_name, planet_id in PLANETS.items():
        result = swe.calc_ut(progressed_jd, planet_id, swe.FLG_SIDEREAL)
        lon = result[0][0]
        speed = result[0][3]  # Longitude speed to determine retrograde
        retrograde = speed < 0
        base_data = format_position(lon)
        nakshatra, pada = get_nakshatra_pada(lon)
        prog_positions[planet_name] = {
            **base_data,
            'retrograde': retrograde,
            'nakshatra': nakshatra,
            'pada': pada
        }
    # South Node (always retrograde)
    nn_lon = prog_positions['North Node']['longitude']
    sn_lon = (nn_lon + 180) % 360
    base_data = format_position(sn_lon)
    nakshatra, pada = get_nakshatra_pada(sn_lon)
    prog_positions['South Node'] = {
        **base_data,
        'retrograde': True,
        'nakshatra': nakshatra,
        'pada': pada
    }
    
    # Compute angles
    asc, mc = calculate_angles(progressed_jd, latitude, longitude)
    asc_sign_idx = int(asc // 30)
    prog_asc = format_position(asc)
    prog_mc = format_position(mc)
    
    # Add nakshatra and pada to Ascendant and Midheaven
    asc_nakshatra, asc_pada = get_nakshatra_pada(asc)
    mc_nakshatra, mc_pada = get_nakshatra_pada(mc)
    prog_asc.update({'nakshatra': asc_nakshatra, 'pada': asc_pada})
    prog_mc.update({'nakshatra': mc_nakshatra, 'pada': mc_pada})
    
    # Add Ascendant to progressed positions (no retrograde for angles)
    prog_positions['Ascendant'] = prog_asc
    
    # Assign houses
    houses = assign_planets_to_houses(prog_positions, asc_sign_idx)
    
    # Calculate aspects
    aspects = calculate_aspects(prog_positions, natal_positions)
    
    # Generate interpretations
    interpretations = {
        'sun': interpret_sun(prog_positions['Sun']['sign'], houses['Sun']),
        'moon': interpret_moon(prog_positions['Moon']['sign'], houses['Moon']),
        'ascendant': interpret_ascendant(prog_positions['Ascendant']['sign']),
        'aspects': interpret_aspects(aspects)
    }
    
    # Structure response data
    response_data = {
        'prog_positions': prog_positions,
        'prog_asc': prog_asc,
        'prog_mc': prog_mc,
        'house_cusps': get_whole_sign_cusps(asc),
        'interpretations': interpretations
    }
    
    return response_data
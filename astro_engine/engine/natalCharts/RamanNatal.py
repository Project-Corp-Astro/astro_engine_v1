# import swisseph as swe
# from datetime import datetime, timedelta

# # Define zodiac signs
# signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
#          'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

# # Define nakshatras (27 stars)
# nakshatras = ['Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra', 'Punarvasu', 'Pushya', 'Ashlesha',
#               'Magha', 'Purva Phalguni', 'Uttara Phalguni', 'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshta',
#               'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta', 'Shatabhisha', 'Purva Bhadrapada',
#               'Uttara Bhadrapada', 'Revati']

# # Nakshatra lords in Vimshottari Dasha order (repeats every 9)
# nakshatra_lords = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury'] * 3

# # Sub-lord sequence (same as nakshatra lords, used cyclically)
# sub_lord_sequence = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']

# # Vimshottari Dasha years for sub-lord proportions
# dasha_years = {
#     'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10, 'Mars': 7,
#     'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17
# }
# total_dasha_years = sum(dasha_years.values())

# # Each nakshatra spans 13°20' (360° / 27)
# nakshatra_span = 360 / 27  # 13.3333 degrees

# def get_nakshatra_and_sub_lord(lon):
#     """
#     Calculate nakshatra, nakshatra lord, and sub-lord for a given longitude.
    
#     Parameters:
#     - lon: Longitude in degrees (0–360°)
    
#     Returns:
#     - tuple: (nakshatra name, nakshatra lord, sub-lord)
#     """
#     # Determine nakshatra
#     nak_index = int(lon / nakshatra_span) % 27
#     nakshatra = nakshatras[nak_index]
#     nak_lord = nakshatra_lords[nak_index]
    
#     # Degrees into the nakshatra
#     degrees_into_nakshatra = lon % nakshatra_span
    
#     # Determine sub-lord
#     start_index = sub_lord_sequence.index(nak_lord)
#     sub_lord_order = sub_lord_sequence[start_index:] + sub_lord_sequence[:start_index]
    
#     # Calculate sub-lord spans proportional to dasha years
#     sub_spans = [(dasha_years[planet] / total_dasha_years) * nakshatra_span for planet in sub_lord_order]
#     cumulative_spans = [0] + [sum(sub_spans[:i + 1]) for i in range(len(sub_spans))]
    
#     # Find which sub-lord the longitude falls into
#     for i in range(len(cumulative_spans) - 1):
#         if cumulative_spans[i] <= degrees_into_nakshatra < cumulative_spans[i + 1]:
#             sub_lord = sub_lord_order[i]
#             break
#     else:
#         sub_lord = sub_lord_order[-1]  # Fallback to last sub-lord
    
#     return nakshatra, nak_lord, sub_lord

# def get_house(lon, asc_sign_index, orientation_shift=0):
#     """
#     Calculate house number based on planet longitude and ascendant sign index for Whole Sign system.
    
#     Parameters:
#     - lon: Planet's longitude (0–360°)
#     - asc_sign_index: Ascendant's sign index (0–11, Aries–Pisces)
#     - orientation_shift: Shift in house numbering (default 0)
    
#     Returns:
#     - House number (1–12)
#     """
#     sign_index = int(lon // 30) % 12
#     house_index = (sign_index - asc_sign_index + orientation_shift) % 12
#     return house_index + 1

# def longitude_to_sign(deg):
#     """
#     Convert longitude to sign and degree within sign.
    
#     Parameters:
#     - deg: Longitude in degrees
    
#     Returns:
#     - tuple: (sign name, degrees within sign)
#     """
#     deg = deg % 360
#     sign_index = int(deg // 30)
#     sign = signs[sign_index]
#     sign_deg = deg % 30
#     return sign, sign_deg

# def format_dms(deg):
#     """
#     Format degrees as degrees, minutes, seconds.
    
#     Parameters:
#     - deg: Degrees (float)
    
#     Returns:
#     - str: Formatted string (e.g., "10° 25' 36.50\"")
#     """
#     d = int(deg)
#     m_fraction = (deg - d) * 60
#     m = int(m_fraction)
#     s = (m_fraction - m) * 60
#     return f"{d}° {m}' {s:.2f}\""

# def raman_natal(birth_data):
#     """
#     Calculate natal chart with Raman Ayanamsa, Whole Sign houses, and nakshatra/sub-lord details.
    
#     Parameters:
#     - birth_data: dict with user_name, birth_date, birth_time, latitude, longitude, timezone_offset, orientation_shift (optional)
    
#     Returns:
#     - dict: Natal chart data with planetary positions, ascendant, house signs, and nakshatra details
#     """
#     latitude = float(birth_data['latitude'])
#     longitude = float(birth_data['longitude'])
#     timezone_offset = float(birth_data['timezone_offset'])

#     # Parse date and time
#     birth_date = datetime.strptime(birth_data['birth_date'], '%Y-%m-%d')
#     birth_time = datetime.strptime(birth_data['birth_time'], '%H:%M:%S').time()
#     local_datetime = datetime.combine(birth_date, birth_time)
#     ut_datetime = local_datetime - timedelta(hours=timezone_offset)
#     hour_decimal = ut_datetime.hour + ut_datetime.minute / 60.0 + ut_datetime.second / 3600.0
#     jd_ut = swe.julday(ut_datetime.year, ut_datetime.month, ut_datetime.day, hour_decimal)

#     # Set Raman Ayanamsa
#     swe.set_sid_mode(swe.SIDM_RAMAN)
#     ayanamsa_value = swe.get_ayanamsa_ut(jd_ut)

#     # Planetary positions
#     planets = [
#         (swe.SUN, 'Sun'), (swe.MOON, 'Moon'), (swe.MARS, 'Mars'),
#         (swe.MERCURY, 'Mercury'), (swe.JUPITER, 'Jupiter'), (swe.VENUS, 'Venus'),
#         (swe.SATURN, 'Saturn'), (swe.TRUE_NODE, 'Rahu')
#     ]
#     flag = swe.FLG_SIDEREAL | swe.FLG_SPEED
#     planet_positions = {}
#     for planet_id, planet_name in planets:
#         pos, ret = swe.calc_ut(jd_ut, planet_id, flag)
#         if ret < 0:
#             raise ValueError(f"Error calculating {planet_name}")
#         lon = pos[0] % 360
#         speed = pos[3]
#         retrograde = 'R' if speed < 0 else ''
#         nakshatra, nak_lord, sub_lord = get_nakshatra_and_sub_lord(lon)
#         planet_positions[planet_name] = (lon, retrograde, nakshatra, nak_lord, sub_lord)

#     # Calculate Ketu (180° opposite Rahu)
#     rahu_lon = planet_positions['Rahu'][0]
#     ketu_lon = (rahu_lon + 180) % 360
#     ketu_nakshatra, ketu_nak_lord, ketu_sub_lord = get_nakshatra_and_sub_lord(ketu_lon)
#     planet_positions['Ketu'] = (ketu_lon, '', ketu_nakshatra, ketu_nak_lord, ketu_sub_lord)

#     # Ascendant and houses (Whole Sign system)
#     cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b'P', flags=swe.FLG_SIDEREAL)
#     ascendant_lon = ascmc[0] % 360
#     asc_sign_index = int(ascendant_lon // 30)
#     asc_sign = signs[asc_sign_index]
#     asc_nakshatra, asc_nak_lord, asc_sub_lord = get_nakshatra_and_sub_lord(ascendant_lon)

#     # Assign house signs with starting longitudes
#     house_signs = []
#     for i in range(12):
#         sign_index = (asc_sign_index + i) % 12
#         sign_start_lon = (sign_index * 30)
#         house_signs.append({"sign": signs[sign_index], "start_longitude": sign_start_lon})

#     # Get orientation shift (default 0)
#     orientation_shift = int(birth_data.get('orientation_shift', 0))
#     planet_houses = {planet: get_house(lon, asc_sign_index, orientation_shift=orientation_shift) 
#                      for planet, (lon, _, _, _, _) in planet_positions.items()}

#     # Format output
#     planetary_positions_json = {}
#     for planet_name, (lon, retro, nakshatra, nak_lord, sub_lord) in planet_positions.items():
#         sign, sign_deg = longitude_to_sign(lon)
#         dms = format_dms(sign_deg)
#         house = planet_houses[planet_name]
#         planetary_positions_json[planet_name] = {
#             "sign": sign,
#             "degrees": dms,
#             "retrograde": retro,
#             "house": house,
#             "nakshatra": nakshatra,
#             "nakshatra_lord": nak_lord,
#             "sub_lord": sub_lord
#         }

#     ascendant_json = {
#         "sign": asc_sign,
#         "degrees": format_dms(ascendant_lon % 30),
#         "nakshatra": asc_nakshatra,
#         "nakshatra_lord": asc_nak_lord,
#         "sub_lord": asc_sub_lord
#     }

#     house_signs_json = {}
#     for i, house in enumerate(house_signs):
#         cusp_lon = house["start_longitude"]
#         nakshatra, nak_lord, sub_lord = get_nakshatra_and_sub_lord(cusp_lon)
#         house_signs_json[f"House {i+1}"] = {
#             "sign": house["sign"],
#             "start_longitude": format_dms(cusp_lon),
#             "nakshatra": nakshatra,
#             "nakshatra_lord": nak_lord,
#             "sub_lord": sub_lord
#         }

#     response = {
#         "user_name": birth_data['user_name'],
#         "birth_details": {
#             "birth_date": birth_data['birth_date'],
#             "birth_time": birth_time.strftime('%H:%M:%S'),
#             "latitude": latitude,
#             "longitude": longitude,
#             "timezone_offset": timezone_offset
#         },
#         "planetary_positions": planetary_positions_json,
#         "ascendant": ascendant_json,
#         "house_signs": house_signs_json,
#         "notes": {
#             "ayanamsa": "Raman",
#             "ayanamsa_value": f"{ayanamsa_value:.6f}",
#             "chart_type": "Rasi",
#             "house_system": "Whole Sign"
#         }
#     }

#     return response








import swisseph as swe
from datetime import datetime, timedelta
import math

# Constants
signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

nakshatras = [
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

# Helper Functions
def get_house(lon, asc_sign_index, orientation_shift=0):
    """
    Calculate house number based on planet longitude and ascendant sign index for Whole Sign system.
    """
    sign_index = int(lon // 30) % 12
    house_index = (sign_index - asc_sign_index + orientation_shift) % 12
    return house_index + 1

def longitude_to_sign(deg):
    """Convert longitude to sign and degree within sign."""
    deg = deg % 360
    sign_index = int(deg // 30)
    sign = signs[sign_index]
    sign_deg = deg % 30
    return sign, sign_deg

def format_dms(deg):
    """Format degrees as degrees, minutes, seconds."""
    d = int(deg)
    m_fraction = (deg - d) * 60
    m = int(m_fraction)
    s = (m_fraction - m) * 60
    return f"{d}° {m}' {s:.2f}\""

def get_nakshatra_and_pada(lon):
    """Calculate nakshatra and pada based on longitude."""
    lon = lon % 360
    for name, start, end in nakshatras:
        if start <= lon < end:
            position_in_nakshatra = lon - start
            pada = math.ceil(position_in_nakshatra / 3.3333)  # 3°20' = 3.3333°
            return name, pada
    return 'Revati', 4  # Fallback for edge case

# Main Calculation Function
def raman_natal(birth_data):
    """
    Calculate natal chart data using Lahiri ayanamsa, including retrograde, nakshatras, and padas.
    
    Parameters:
    - birth_data: Dictionary with birth details
    
    Returns:
    - Dictionary with calculated chart data
    """
    latitude = float(birth_data['latitude'])
    longitude = float(birth_data['longitude'])
    timezone_offset = float(birth_data['timezone_offset'])
    birth_date = datetime.strptime(birth_data['birth_date'], '%Y-%m-%d')
    birth_time = datetime.strptime(birth_data['birth_time'], '%H:%M:%S').time()
    local_datetime = datetime.combine(birth_date, birth_time)
    ut_datetime = local_datetime - timedelta(hours=timezone_offset)
    hour_decimal = ut_datetime.hour + ut_datetime.minute / 60.0 + ut_datetime.second / 3600.0
    jd_ut = swe.julday(ut_datetime.year, ut_datetime.month, ut_datetime.day, hour_decimal)

    # Set Lahiri ayanamsa
    swe.set_sid_mode(swe.SIDM_RAMAN)
    ayanamsa_value = swe.get_ayanamsa_ut(jd_ut)

    # Planetary positions
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
            raise Exception(f"Error calculating {planet_name}")
        lon = pos[0] % 360
        speed = pos[3]
        retrograde = 'R' if speed < 0 else ''
        nakshatra, pada = get_nakshatra_and_pada(lon)
        planet_positions[planet_name] = {
            'lon': lon,
            'retro': retrograde,
            'nakshatra': nakshatra,
            'pada': pada
        }

    # Calculate Ketu
    rahu_lon = planet_positions['Rahu']['lon']
    ketu_lon = (rahu_lon + 180) % 360
    ketu_nakshatra, ketu_pada = get_nakshatra_and_pada(ketu_lon)
    planet_positions['Ketu'] = {
        'lon': ketu_lon,
        'retro': '',
        'nakshatra': ketu_nakshatra,
        'pada': ketu_pada
    }

    # Ascendant and houses
    cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b'W', flags=swe.FLG_SIDEREAL)
    ascendant_lon = ascmc[0] % 360
    asc_sign_index = int(ascendant_lon // 30)
    asc_nakshatra, asc_pada = get_nakshatra_and_pada(ascendant_lon)

    # House signs
    house_signs = []
    for i in range(12):
        sign_index = (asc_sign_index + i) % 12
        sign_start_lon = (sign_index * 30)
        house_signs.append({"sign": signs[sign_index], "start_longitude": sign_start_lon})

    # Planet houses
    orientation_shift = int(birth_data.get('orientation_shift', 0))
    planet_houses = {planet: get_house(data['lon'], asc_sign_index, orientation_shift=orientation_shift)
                     for planet, data in planet_positions.items()}

    return {
        'planet_positions': planet_positions,
        'ascendant': {'lon': ascendant_lon, 'nakshatra': asc_nakshatra, 'pada': asc_pada},
        'house_signs': house_signs,
        'planet_houses': planet_houses,
        'ayanamsa_value': ayanamsa_value
    }
import swisseph as swe
from datetime import datetime, timedelta
import math

# Constants for KP Astrology
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
SUB_LORD_SEQUENCE = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']
NAKSHATRA_SPAN = 13 + 20 / 60  # 13.3333 degrees
PADA_SPAN = NAKSHATRA_SPAN / 4  # 3.3333 degrees

# Vimshottari Dasha years
DASHA_YEARS = {
    'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10, 'Mars': 7,
    'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17
}
TOTAL_DASHA_YEARS = 120

# Utility Functions
def degrees_to_dms(degrees):
    """Convert decimal degrees to degrees, minutes, seconds."""
    d = math.floor(degrees)
    m = math.floor((degrees - d) * 60)
    s = round(((degrees - d) * 60 - m) * 60, 2)
    return f"{d}° {m}' {s}\""

def get_sign(longitude):
    """Calculate the zodiac sign from longitude."""
    sign_index = math.floor(longitude / 30) % 12
    return SIGNS[sign_index]

def get_nakshatra(longitude):
    """Calculate nakshatra and its lord from longitude."""
    nak_index = math.floor(longitude / NAKSHATRA_SPAN) % 27
    return NAKSHATRAS[nak_index], NAKSHATRA_LORDS[nak_index]

def get_pada(longitude):
    """Calculate the pada (quarter) within the nakshatra."""
    degrees_into_nakshatra = longitude % NAKSHATRA_SPAN
    pada = math.ceil(degrees_into_nakshatra / PADA_SPAN)
    return min(pada, 4)  # Cap at 4

def get_sub_lord(longitude):
    """Calculate the sub-lord (SL) based on Vimshottari proportions."""
    nak_index = math.floor(longitude / NAKSHATRA_SPAN) % 27
    nak_start = nak_index * NAKSHATRA_SPAN
    degrees_into_nakshatra = longitude - nak_start

    # Nakshatra lord determines the starting sub-lord
    nak_lord = NAKSHATRA_LORDS[nak_index]
    start_index = SUB_LORD_SEQUENCE.index(nak_lord)
    sub_lord_order = SUB_LORD_SEQUENCE[start_index:] + SUB_LORD_SEQUENCE[:start_index]

    # Calculate sub-lord spans
    sub_spans = [(DASHA_YEARS[planet] / TOTAL_DASHA_YEARS) * NAKSHATRA_SPAN for planet in sub_lord_order]
    cumulative_spans = [0] + [sum(sub_spans[:i + 1]) for i in range(len(sub_spans))]

    # Find sub-lord
    for i in range(len(cumulative_spans) - 1):
        if cumulative_spans[i] <= degrees_into_nakshatra < cumulative_spans[i + 1]:
            return sub_lord_order[i]
    return sub_lord_order[-1]  # Fallback for edge case

def get_sub_sub_lord(longitude):
    """Calculate the sub-sub-lord (SS) with precise logic."""
    nak_index = math.floor(longitude / NAKSHATRA_SPAN) % 27
    nak_start = nak_index * NAKSHATRA_SPAN
    degrees_into_nakshatra = longitude - nak_start

    # Get sub-lord details
    sub_lord = get_sub_lord(longitude)
    nak_lord = NAKSHATRA_LORDS[nak_index]
    start_index = SUB_LORD_SEQUENCE.index(nak_lord)
    sub_lord_order = SUB_LORD_SEQUENCE[start_index:] + SUB_LORD_SEQUENCE[:start_index]
    sub_spans = [(DASHA_YEARS[planet] / TOTAL_DASHA_YEARS) * NAKSHATRA_SPAN for planet in sub_lord_order]
    cumulative_sub_spans = [0] + [sum(sub_spans[:i + 1]) for i in range(len(sub_spans))]

    # Find sub-lord span and degrees into it
    sub_lord_idx = sub_lord_order.index(sub_lord)
    sub_start = cumulative_sub_spans[sub_lord_idx]
    sub_span = sub_spans[sub_lord_idx]
    degrees_into_sub = degrees_into_nakshatra - sub_start

    # Sub-sub-lord sequence starts with the sub-lord
    ss_start_index = SUB_LORD_SEQUENCE.index(sub_lord)
    ss_order = SUB_LORD_SEQUENCE[ss_start_index:] + SUB_LORD_SEQUENCE[:ss_start_index]

    # Calculate sub-sub-lord spans within the sub-lord span
    ss_spans = [(DASHA_YEARS[planet] / TOTAL_DASHA_YEARS) * sub_span for planet in ss_order]
    cumulative_ss_spans = [0] + [sum(ss_spans[:i + 1]) for i in range(len(ss_spans))]

    # Find sub-sub-lord
    for i in range(len(cumulative_ss_spans) - 1):
        if cumulative_ss_spans[i] <= degrees_into_sub < cumulative_ss_spans[i + 1]:
            return ss_order[i]
    return ss_order[-1]  # Fallback for edge case

def calculate_bhava_houses_details(birth_date, birth_time, latitude, longitude, timezone_offset):
    """Calculate Bhava House Details using KP Astrology."""
    # Convert local time to UTC
    local_dt = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M:%S")
    utc_dt = local_dt - timedelta(hours=timezone_offset)

    # Calculate Julian Day
    hour_decimal = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_decimal)

    # Set KP New Ayanamsa
    swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)

    # Calculate Placidus house cusps
    cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b'P', flags=swe.FLG_SIDEREAL)
    house_cusps = cusps[:12]

    # Calculate Bhava details
    bhava_details = {}
    for house in range(1, 13):
        cusp_long = house_cusps[house - 1]
        sign = get_sign(cusp_long)
        nakshatra, nl = get_nakshatra(cusp_long)
        pada = get_pada(cusp_long)
        sl = get_sub_lord(cusp_long)
        ss = get_sub_sub_lord(cusp_long)
        rl = SIGN_RULERS[sign]

        # Convert longitude to DMS
        dms = degrees_to_dms(cusp_long)

        bhava_details[house] = {
            'longitude_dms': dms,
            'longitude_decimal': round(cusp_long, 6),
            'sign': sign,
            'nakshatra': nakshatra,
            'pada': pada,
            'RL': rl,
            'NL': nl,
            'SL': sl,
            'SS': ss
        }

    return bhava_details
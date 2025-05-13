import swisseph as swe
from datetime import datetime, timedelta

# Constants
ZODIAC_SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
SIGN_RULERS = {
    'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury', 'Cancer': 'Moon', 'Leo': 'Sun', 
    'Virgo': 'Mercury', 'Libra': 'Venus', 'Scorpio': 'Mars', 'Sagittarius': 'Jupiter', 
    'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
}
NAKSHATRAS = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra', 'Punarvasu', 'Pushya', 
    'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni', 'Hasta', 'Chitra', 'Swati', 
    'Vishakha', 'Anuradha', 'Jyeshta', 'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 
    'Dhanishta', 'Shatabhisha', 'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
]
NAKSHATRA_LORDS = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury'] * 3  # 27 Nakshatras
DASHA_YEARS = {
    'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10, 'Mars': 7, 'Rahu': 18, 
    'Jupiter': 16, 'Saturn': 19, 'Mercury': 17
}
NAKSHATRA_SPAN = 360 / 27  # 13.3333 degrees per Nakshatra

def ruling_get_sign(degree):
    """Determine the zodiac sign from a given longitude (0-360 degrees)."""
    sign_index = int(degree / 30) % 12
    return ZODIAC_SIGNS[sign_index]

def ruling_get_nakshatra_and_lord(degree):
    """Determine the Nakshatra and its lord from a given longitude."""
    nak_index = int(degree / NAKSHATRA_SPAN) % 27
    nakshatra = NAKSHATRAS[nak_index]
    lord = NAKSHATRA_LORDS[nak_index]
    return nakshatra, lord

def ruling_get_sub_lord(degree):
    """Calculate the Sub-Lord for a given longitude based on Vimshottari Dasha proportions."""
    lords = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']
    dasha_years = [7, 20, 6, 10, 7, 18, 16, 19, 17]
    nak_span = NAKSHATRA_SPAN
    nak_index = int(degree / nak_span) % 27
    nak_lord = NAKSHATRA_LORDS[nak_index]
    start_index = lords.index(nak_lord)
    sub_lord_sequence = (lords * 2)[start_index:start_index + 9]
    sub_spans = [(dasha_years[(start_index + i) % 9] / 120 * nak_span) for i in range(9)]
    cumulative_spans = [0] + [sum(sub_spans[:i + 1]) for i in range(9)]
    position_in_nak = degree % nak_span
    for i in range(9):
        if cumulative_spans[i] <= position_in_nak < cumulative_spans[i + 1]:
            return sub_lord_sequence[i]
    return sub_lord_sequence[-1]  # Fallback for edge case

def ruling_calculate_jd(birth_date, birth_time, timezone_offset):
    """Calculate Julian Day from birth date, time, and timezone offset."""
    local_dt = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M:%S")
    utc_dt = local_dt - timedelta(hours=timezone_offset)
    hour_decimal = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_decimal)
    return jd, utc_dt

def ruling_calculate_ascendant_and_cusps(jd, latitude, longitude):
    """Calculate Ascendant and house cusps using Placidus system."""
    swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)
    cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b'P', flags=swe.FLG_SIDEREAL)
    ascendant = cusps[0]  # Ascendant longitude (float)
    return ascendant, cusps

def ruling_calculate_planet_positions(jd):
    """Calculate sidereal planetary positions."""
    sun_pos = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL)[0][0]  # Longitude (float)
    moon_pos = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)[0][0]  # Longitude (float)
    rahu_pos = swe.calc_ut(jd, swe.MEAN_NODE, swe.FLG_SIDEREAL)[0][0]  # Longitude (float)
    ketu_pos = (rahu_pos + 180) % 360  # Ketu is 180° opposite Rahu (float)
    return sun_pos, moon_pos, rahu_pos, ketu_pos

def ruling_get_day_lord(utc_dt):
    """Determine the Day Lord based on UTC date."""
    day_of_week = utc_dt.weekday()  # 0 = Monday, 6 = Sunday
    day_lord = ['Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Sun'][day_of_week]
    return day_lord

def ruling_get_details(longitude):
    """Get sign, rashi lord, nakshatra, star lord, sub lord for a longitude."""
    sign = ruling_get_sign(longitude)
    rashi_lord = SIGN_RULERS[sign]
    nakshatra, star_lord = ruling_get_nakshatra_and_lord(longitude)
    sub_lord = ruling_get_sub_lord(longitude)
    return sign, rashi_lord, nakshatra, star_lord, sub_lord

def ruling_compile_core_rp(lagna_details, moon_details, day_lord):
    """Compile core Ruling Planets."""
    core_rp = set([
        lagna_details['rashi_lord'], lagna_details['star_lord'], lagna_details['sub_lord'],
        moon_details['rashi_lord'], moon_details['star_lord'], moon_details['sub_lord'],
        day_lord
    ])
    return core_rp

def ruling_check_rahu_ketu(rahu_pos, ketu_pos, core_rp):
    """Include Rahu/Ketu if their nakshatra lords are in core RP."""
    rahu_nak_lord = ruling_get_nakshatra_and_lord(rahu_pos)[1]
    ketu_nak_lord = ruling_get_nakshatra_and_lord(ketu_pos)[1]
    if rahu_nak_lord in core_rp:
        core_rp.add('Rahu')
    if ketu_nak_lord in core_rp:
        core_rp.add('Ketu')
    return core_rp

def ruling_calculate_fortuna(ascendant, moon_pos, sun_pos):
    """Calculate Fortuna (Part of Fortune)."""
    return (ascendant + moon_pos - sun_pos) % 360

def ruling_calculate_balance_of_dasha(moon_pos, moon_star_lord):
    """Calculate Balance of Dasha based on Moon's position."""
    nak_start = int(moon_pos / NAKSHATRA_SPAN) * NAKSHATRA_SPAN
    position_in_nak = moon_pos - nak_start
    fraction_passed = position_in_nak / NAKSHATRA_SPAN
    fraction_remaining = 1 - fraction_passed
    dasha_lord = moon_star_lord
    balance_years = fraction_remaining * DASHA_YEARS[dasha_lord]
    return dasha_lord, balance_years
import swisseph as swe
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Nakshatra details: name, start degree, ruling planet
NAKSHATRAS = [
    ("Ashwini", 0, "Ketu"), ("Bharani", 13.333, "Venus"), ("Krittika", 26.666, "Sun"),
    ("Rohini", 40, "Moon"), ("Mrigashira", 53.333, "Mars"), ("Ardra", 66.666, "Rahu"),
    ("Punarvasu", 80, "Jupiter"), ("Pushya", 93.333, "Saturn"), ("Ashlesha", 106.666, "Mercury"),
    ("Magha", 120, "Ketu"), ("Purva Phalguni", 133.333, "Venus"), ("Uttara Phalguni", 146.666, "Sun"),
    ("Hasta", 160, "Moon"), ("Chitra", 173.333, "Mars"), ("Swati", 186.666, "Rahu"),
    ("Vishakha", 200, "Jupiter"), ("Anuradha", 213.333, "Saturn"), ("Jyeshta", 226.666, "Mercury"),
    ("Mula", 240, "Ketu"), ("Purva Ashadha", 253.333, "Venus"), ("Uttara Ashadha", 266.666, "Sun"),
    ("Shravana", 280, "Moon"), ("Dhanishta", 293.333, "Mars"), ("Shatabhisha", 306.666, "Rahu"),
    ("Purva Bhadrapada", 320, "Jupiter"), ("Uttara Bhadrapada", 333.333, "Saturn"), ("Revati", 346.666, "Mercury")
]

# Planet durations for Mahadasha in years
PLANET_DURATIONS = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
    "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17
}

# Fixed order of planets for Mahadasha and Antardasha sequence
PLANET_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]

def get_julian_day_antar_raman(date_str, time_str, tz_offset):
    """Convert local birth date and time to Julian Day in UT."""
    local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    ut_dt = local_dt - relativedelta(hours=tz_offset)
    hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
    return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal, swe.GREG_CAL)

def calculate_moon_sidereal_position_raman_antar(jd):
    """Calculate the Moon's sidereal longitude using Raman Ayanamsa."""
    swe.set_sid_mode(swe.SIDM_RAMAN)
    moon_tropical = swe.calc_ut(jd, swe.MOON)[0][0]
    ayanamsa = swe.get_ayanamsa_ut(jd)
    moon_sidereal = (moon_tropical - ayanamsa) % 360
    return moon_sidereal

def get_nakshatra_and_lord_raman_antar(moon_longitude):
    """Determine the nakshatra, its ruling planet, and start longitude."""
    for nakshatra, start, lord in NAKSHATRAS:
        if start <= moon_longitude < start + 13.333:
            return nakshatra, lord, start
    if moon_longitude >= 346.666 or moon_longitude < 0:
        return "Revati", "Mercury", 346.666
    return None, None, None

def calculate_dasha_balance_raman_antar(moon_longitude, nakshatra_start, lord):
    """Calculate the remaining balance and elapsed time of the starting Mahadasha."""
    nakshatra_span = 13.333
    degrees_in_nakshatra = moon_longitude - nakshatra_start
    if degrees_in_nakshatra < 0:
        degrees_in_nakshatra += 360
    fraction_traversed = degrees_in_nakshatra / nakshatra_span
    mahadasha_duration = PLANET_DURATIONS[lord]
    elapsed_years = mahadasha_duration * fraction_traversed
    balance_years = mahadasha_duration - elapsed_years
    return balance_years, elapsed_years

def calculate_antardasha_duration(mahadasha_planet, antardasha_planet):
    """Calculate Antardasha duration in years."""
    total_cycle = 120.0
    return (PLANET_DURATIONS[mahadasha_planet] * PLANET_DURATIONS[antardasha_planet]) / total_cycle

def add_duration(start_date, duration_years):
    """Add duration to start date with precision."""
    years = int(duration_years)
    fractional_year = duration_years - years
    months = int(fractional_year * 12)
    fractional_month = (fractional_year * 12) - months
    days = int(fractional_month * 30.436875)  # Average days per month (365.2425 / 12)
    return start_date + relativedelta(years=years, months=months, days=days)

def find_starting_antardasha(mahadasha_planet, elapsed_years):
    """Find the starting Antardasha and elapsed time within it."""
    anta_sequence = PLANET_ORDER[PLANET_ORDER.index(mahadasha_planet):] + PLANET_ORDER[:PLANET_ORDER.index(mahadasha_planet)]
    cumulative_duration = 0
    for i, planet in enumerate(anta_sequence):
        anta_duration = calculate_antardasha_duration(mahadasha_planet, planet)
        if cumulative_duration + anta_duration > elapsed_years:
            return i, elapsed_years - cumulative_duration, anta_sequence
        cumulative_duration += anta_duration
    return 0, 0, anta_sequence

def raman_antar_dasha(mahadasha_planet, mahadasha_start, birth_datetime, is_first_maha, elapsed_years):
    """Calculate Antardashas with precise dates."""
    antardashas = []
    start_idx, elapsed_in_current, anta_sequence = find_starting_antardasha(mahadasha_planet, elapsed_years) if is_first_maha else (0, 0, PLANET_ORDER[PLANET_ORDER.index(mahadasha_planet):] + PLANET_ORDER[:PLANET_ORDER.index(mahadasha_planet)])
    
    current_start = birth_datetime if is_first_maha else mahadasha_start
    for i in range(start_idx, 9):
        anta_planet = anta_sequence[i]
        anta_duration = calculate_antardasha_duration(mahadasha_planet, anta_planet)
        if i == start_idx and is_first_maha:
            anta_duration -= elapsed_in_current
        anta_end = add_duration(current_start, anta_duration)
        antardashas.append({
            "planet": anta_planet,
            "start_date": current_start.strftime('%Y-%m-%d %H:%M:%S'),
            "end_date": anta_end.strftime('%Y-%m-%d %H:%M:%S'),
            "duration_years": round(anta_duration, 4)
        })
        current_start = anta_end
    return antardashas

def calculate_mahadasha_periods_antar_raman(birth_datetime, starting_planet, balance_years, elapsed_years):
    """Calculate Mahadasha periods with Antardashas."""
    mahadasha_sequence = []
    current_planet_idx = PLANET_ORDER.index(starting_planet)
    current_start = birth_datetime
    
    for i in range(9):
        planet = PLANET_ORDER[current_planet_idx]
        duration = balance_years if i == 0 else PLANET_DURATIONS[planet]
        antardashas = raman_antar_dasha(planet, current_start, birth_datetime, i == 0, elapsed_years if i == 0 else 0)
        end_date = add_duration(current_start, duration)
        mahadasha_sequence.append({
            "planet": planet,
            "start_date": current_start.strftime('%Y-%m-%d %H:%M:%S'),
            "end_date": end_date.strftime('%Y-%m-%d %H:%M:%S'),
            "duration_years": round(duration, 4),
            "antardashas": antardashas
        })
        current_start = end_date
        current_planet_idx = (current_planet_idx + 1) % 9
    return mahadasha_sequence
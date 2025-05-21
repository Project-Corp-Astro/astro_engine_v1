import swisseph as swe
from math import floor
from datetime import datetime, timedelta

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

# Fixed order of planets for sequence
PLANET_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]

# Days in a tropical year for precise calculations
DAYS_PER_YEAR = 365.242189

def get_julian_day_sookshma_raman(date_str, time_str, tz_offset):
    """Convert local birth date and time to Julian Day in Universal Time (UT)."""
    local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    ut_dt = local_dt - timedelta(hours=tz_offset)
    hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
    return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal, swe.GREG_CAL)

def jd_to_date(jd):
    """Convert Julian Day to Gregorian date string with time."""
    year, month, day, hour = swe.revjul(jd, swe.GREG_CAL)
    hour_int = int(hour)
    minute = int((hour - hour_int) * 60)
    second = int(((hour - hour_int) * 60 - minute) * 60)
    return f"{year}-{month:02d}-{day:02d} {hour_int:02d}:{minute:02d}:{second:02d}"

def calculate_moon_sidereal_sookshma_raman(jd):
    """Calculate the Moon's sidereal longitude using Raman Ayanamsa."""
    swe.set_sid_mode(swe.SIDM_RAMAN)
    moon_tropical = swe.calc_ut(jd, swe.MOON)[0][0]
    ayanamsa = swe.get_ayanamsa_ut(jd)
    moon_sidereal = (moon_tropical - ayanamsa) % 360
    return moon_sidereal

def get_nakshatra_and_lord_soo_raman(moon_longitude):
    """Determine the nakshatra, its ruling planet, and start longitude."""
    for nakshatra, start, lord in NAKSHATRAS:
        if start <= moon_longitude < (start + 13.333):
            return nakshatra, lord, start
    if moon_longitude >= 346.666 or moon_longitude < 0:
        return "Revati", "Mercury", 346.666
    return None, None, None

def calculate_sookshma_dasha_balance_raman(moon_longitude, nakshatra_start, lord):
    """Calculate the remaining balance and elapsed time of the starting Mahadasha."""
    nakshatra_span = 13.333
    degrees_in_nakshatra = moon_longitude - nakshatra_start
    if degrees_in_nakshatra < 0:
        degrees_in_nakshatra += 360
    fraction_elapsed = degrees_in_nakshatra / nakshatra_span
    mahadasha_duration = PLANET_DURATIONS[lord]
    elapsed_time = mahadasha_duration * fraction_elapsed
    remaining_time = mahadasha_duration - elapsed_time
    return remaining_time, mahadasha_duration, elapsed_time

def calculate_sub_periods(parent_duration, start_planet, elapsed_time=0):
    """Calculate sub-period durations, active period index, and remaining time."""
    total_cycle = 120
    start_idx = PLANET_ORDER.index(start_planet)
    durations = [(PLANET_DURATIONS[PLANET_ORDER[(start_idx + i) % 9]] * parent_duration) / total_cycle for i in range(9)]
    cumulative_duration = 0
    for i, duration in enumerate(durations):
        cumulative_duration += duration
        if cumulative_duration > elapsed_time:
            active_idx = i
            time_already_elapsed = elapsed_time - (cumulative_duration - duration)
            remaining_in_active = duration - time_already_elapsed
            return durations, active_idx, remaining_in_active, time_already_elapsed
    # If elapsed_time exceeds total duration, default to first period
    return durations, 0, durations[0], 0

def raman_sookshma_dasha(parent_planet, parent_duration, start_jd, elapsed_time=0):
    """Calculate Sookshma Dashas with precise start and end dates."""
    sookshma_dashas = []
    durations, active_idx, remaining_in_active, elapsed_in_active = calculate_sub_periods(parent_duration, parent_planet, elapsed_time)
    current_jd = start_jd + (elapsed_in_active * DAYS_PER_YEAR if elapsed_time > 0 else 0)
    start_idx = PLANET_ORDER.index(parent_planet)

    for i in range(9):
        planet = PLANET_ORDER[(start_idx + i) % 9]
        duration = remaining_in_active if i == active_idx else durations[i % 9]
        end_jd = current_jd + (duration * DAYS_PER_YEAR)
        sookshma_dashas.append({
            'planet': planet,
            'start_date': jd_to_date(current_jd),
            'end_date': jd_to_date(end_jd),
            'duration_days': round(duration * DAYS_PER_YEAR, 2)
        })
        current_jd = end_jd if i >= active_idx else current_jd
        if i < active_idx:
            current_jd += (durations[i] * DAYS_PER_YEAR)

    return sookshma_dashas

def calculate_pratyantardashas(parent_planet, parent_duration, start_jd, elapsed_time=0):
    """Calculate Pratyantardashas with nested Sookshma Dashas."""
    pratyantardashas = []
    durations, active_idx, remaining_in_active, elapsed_in_active = calculate_sub_periods(parent_duration, parent_planet, elapsed_time)
    current_jd = start_jd + (elapsed_in_active * DAYS_PER_YEAR if elapsed_time > 0 else 0)
    start_idx = PLANET_ORDER.index(parent_planet)

    for i in range(9):
        planet = PLANET_ORDER[(start_idx + i) % 9]
        duration = remaining_in_active if i == active_idx else durations[i % 9]
        end_jd = current_jd + (duration * DAYS_PER_YEAR)
        sookshma_dashas = raman_sookshma_dasha(planet, duration, current_jd, elapsed_in_active if i == active_idx else 0)
        pratyantardashas.append({
            'planet': planet,
            'start_date': jd_to_date(current_jd),
            'end_date': jd_to_date(end_jd),
            'duration_days': round(duration * DAYS_PER_YEAR, 2),
            'sookshma_dashas': sookshma_dashas
        })
        current_jd = end_jd if i >= active_idx else current_jd
        if i < active_idx:
            current_jd += (durations[i] * DAYS_PER_YEAR)

    return pratyantardashas

def calculate_antardashas(parent_planet, parent_duration, start_jd, elapsed_time=0):
    """Calculate Antardashas with nested Pratyantardashas."""
    antardashas = []
    durations, active_idx, remaining_in_active, elapsed_in_active = calculate_sub_periods(parent_duration, parent_planet, elapsed_time)
    current_jd = start_jd + (elapsed_in_active * DAYS_PER_YEAR if elapsed_time > 0 else 0)
    start_idx = PLANET_ORDER.index(parent_planet)

    for i in range(9):
        planet = PLANET_ORDER[(start_idx + i) % 9]
        duration = remaining_in_active if i == active_idx else durations[i % 9]
        end_jd = current_jd + (duration * DAYS_PER_YEAR)
        pratyantardashas = calculate_pratyantardashas(planet, duration, current_jd, elapsed_in_active if i == active_idx else 0)
        antardashas.append({
            'planet': planet,
            'start_date': jd_to_date(current_jd),
            'end_date': jd_to_date(end_jd),
            'duration_years': round(duration, 4),
            'pratyantardashas': pratyantardashas
        })
        current_jd = end_jd if i >= active_idx else current_jd
        if i < active_idx:
            current_jd += (durations[i] * DAYS_PER_YEAR)

    return antardashas

def calculate_sookshma_raman_periods(birth_jd, starting_planet, elapsed_time):
    """Calculate Mahadasha periods with nested sub-periods."""
    mahadasha_sequence = []
    start_idx = PLANET_ORDER.index(starting_planet)
    current_jd = birth_jd

    # First Mahadasha (active at birth)
    mahadasha_duration = PLANET_DURATIONS[starting_planet]
    remaining_time = mahadasha_duration - elapsed_time
    end_jd = current_jd + (remaining_time * DAYS_PER_YEAR)
    antardashas = calculate_antardashas(starting_planet, remaining_time, current_jd, elapsed_time)
    mahadasha_sequence.append({
        'planet': starting_planet,
        'start_date': jd_to_date(current_jd),
        'end_date': jd_to_date(end_jd),
        'duration_years': round(remaining_time, 4),
        'antardashas': antardashas
    })
    current_jd = end_jd

    # Subsequent Mahadashas
    for i in range(1, 9):
        planet = PLANET_ORDER[(start_idx + i) % 9]
        duration = PLANET_DURATIONS[planet]
        end_jd = current_jd + (duration * DAYS_PER_YEAR)
        antardashas = calculate_antardashas(planet, duration, current_jd)
        mahadasha_sequence.append({
            'planet': planet,
            'start_date': jd_to_date(current_jd),
            'end_date': jd_to_date(end_jd),
            'duration_years': round(duration, 4),
            'antardashas': antardashas
        })
        current_jd = end_jd

    return mahadasha_sequence
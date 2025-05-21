import swisseph as swe
from datetime import datetime, timedelta
import logging

# Nakshatra definitions with precise start degrees and ruling planets
NAKSHATRAS = [
    ("Ashwini", 0.0, "Ketu"), ("Bharani", 13.333333333333334, "Venus"), ("Krittika", 26.666666666666668, "Sun"),
    ("Rohini", 40.0, "Moon"), ("Mrigashira", 53.333333333333336, "Mars"), ("Ardra", 66.66666666666667, "Rahu"),
    ("Punarvasu", 80.0, "Jupiter"), ("Pushya", 93.33333333333333, "Saturn"), ("Ashlesha", 106.66666666666667, "Mercury"),
    ("Magha", 120.0, "Ketu"), ("Purva Phalguni", 133.33333333333334, "Venus"), ("Uttara Phalguni", 146.66666666666666, "Sun"),
    ("Hasta", 160.0, "Moon"), ("Chitra", 173.33333333333334, "Mars"), ("Swati", 186.66666666666666, "Rahu"),
    ("Vishakha", 200.0, "Jupiter"), ("Anuradha", 213.33333333333334, "Saturn"), ("Jyeshta", 226.66666666666666, "Mercury"),
    ("Mula", 240.0, "Ketu"), ("Purva Ashadha", 253.33333333333334, "Venus"), ("Uttara Ashadha", 266.6666666666667, "Sun"),
    ("Shravana", 280.0, "Moon"), ("Dhanishta", 293.3333333333333, "Mars"), ("Shatabhisha", 306.6666666666667, "Rahu"),
    ("Purva Bhadrapada", 320.0, "Jupiter"), ("Uttara Bhadrapada", 333.3333333333333, "Saturn"), ("Revati", 346.6666666666667, "Mercury")
]

# Mahadasha durations in years
PLANET_DURATIONS = {
    "Ketu": 7.0, "Venus": 20.0, "Sun": 6.0, "Moon": 10.0, "Mars": 7.0,
    "Rahu": 18.0, "Jupiter": 16.0, "Saturn": 19.0, "Mercury": 17.0
}

PLANET_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]

# Use tropical year for consistency with astrological calculations
VIMSHOTTARI_YEAR_DAYS = 365.2425

def get_julian_day_prataythar_raman(date_str, time_str, tz_offset):
    """Convert local birth date and time to Julian Day with timezone adjustment."""
    local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    ut_dt = local_dt - timedelta(hours=tz_offset)
    hour_decimal = ut_dt.hour + ut_dt.minute / 60.0 + ut_dt.second / 3600.0
    jd = swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal, swe.GREG_CAL)
    logging.debug(f"Julian Day: {jd}")
    return jd

def jd_to_date(jd):
    """Convert Julian Day back to Gregorian date with precise time."""
    year, month, day, hour = swe.revjul(jd, swe.GREG_CAL)
    hour_int = int(hour)
    minute = (hour - hour_int) * 60
    minute_int = int(minute)
    second = (hour - hour_int) * 3600 - minute_int * 60
    second_int = int(round(second))
    if second_int >= 60:
        second_int = 0
        minute_int += 1
        if minute_int >= 60:
            minute_int = 0
            hour_int += 1
    return f"{year}-{month:02d}-{day:02d} {hour_int:02d}:{minute_int:02d}:{second_int:02d}"

def calculate_moon_sidereal_position_prataythar_raman(jd):
    """Calculate Moon's sidereal longitude using Raman ayanamsa."""
    swe.set_sid_mode(swe.SIDM_RAMAN)
    moon_tropical = swe.calc_ut(jd, swe.MOON)[0][0]
    ayanamsa = swe.get_ayanamsa_ut(jd)
    moon_sidereal = (moon_tropical - ayanamsa) % 360
    logging.debug(f"Moon Tropical: {moon_tropical}, Ayanamsa: {ayanamsa}, Moon Sidereal: {moon_sidereal}")
    return moon_sidereal

def get_nakshatra_and_lord_prataythar_raman(moon_longitude):
    """Determine Nakshatra and its ruling planet based on Moon's longitude."""
    for nakshatra, start, lord in NAKSHATRAS:
        if start <= moon_longitude < start + 13.333333333333334:
            return nakshatra, lord, start
    if moon_longitude >= 346.6666666666667 or moon_longitude < 0:
        return "Revati", "Mercury", 346.6666666666667
    return None, None, None

def calculate_dasha_balance_prataythar_raman(moon_longitude, nakshatra_start, lord):
    """Calculate elapsed and remaining time in the first Mahadasha at birth with high precision."""
    nakshatra_span = 13.333333333333334
    degrees_in_nakshatra = moon_longitude - nakshatra_start
    if degrees_in_nakshatra < 0:
        degrees_in_nakshatra += 360
    fraction_elapsed = degrees_in_nakshatra / nakshatra_span
    mahadasha_duration = PLANET_DURATIONS[lord]
    elapsed_time = mahadasha_duration * fraction_elapsed
    remaining_time = mahadasha_duration - elapsed_time
    logging.debug(f"Degrees in Nakshatra: {degrees_in_nakshatra}, Fraction Elapsed: {fraction_elapsed}, "
                  f"Elapsed Time: {elapsed_time}, Remaining Time: {remaining_time}")
    return remaining_time, mahadasha_duration, elapsed_time

def raman_pratyantar_dasha(mahadasha_planet, antardasha_planet, antardasha_start_jd, antardasha_duration, birth_jd=None, elapsed_in_antardasha=0):
    """Calculate Pratyantardasha periods starting from birth date for the first Antardasha."""
    pratyantardashas = []
    total_cycle = 120.0
    start_idx = PLANET_ORDER.index(antardasha_planet)
    current_jd = antardasha_start_jd

    # Calculate all Pratyantardasha durations
    pratyantardasha_durations = [(PLANET_DURATIONS[PLANET_ORDER[(start_idx + i) % 9]] * antardasha_duration) / total_cycle for i in range(9)]

    if birth_jd is not None and elapsed_in_antardasha > 0:
        # Find the active Pratyantardasha at birth
        cumulative_duration = 0
        for i, duration in enumerate(pratyantardasha_durations):
            cumulative_duration += duration
            if cumulative_duration > elapsed_in_antardasha:
                start_pratyantardasha_idx = i
                time_already_elapsed = elapsed_in_antardasha - (cumulative_duration - duration)
                remaining_in_pratyantardasha = duration - time_already_elapsed
                break
        else:
            start_pratyantardasha_idx = 0
            time_already_elapsed = 0
            remaining_in_pratyantardasha = pratyantardasha_durations[0]

        # Start from the active Pratyantardasha at birth
        for i in range(9):
            planet_idx = (start_idx + (start_pratyantardasha_idx + i) % 9) % 9
            planet = PLANET_ORDER[planet_idx]
            duration_years = pratyantardasha_durations[(start_pratyantardasha_idx + i) % 9]
            
            if i == 0:
                # Active Pratyantardasha starts at birth
                start_jd = birth_jd
                end_jd = start_jd + (remaining_in_pratyantardasha * VIMSHOTTARI_YEAR_DAYS)
                duration = remaining_in_pratyantardasha
            else:
                # Subsequent Pratyantardashas
                start_jd = current_jd
                end_jd = start_jd + (duration_years * VIMSHOTTARI_YEAR_DAYS)
                duration = duration_years

            pratyantardashas.append({
                "planet": planet,
                "start_date": jd_to_date(start_jd),
                "end_date": jd_to_date(end_jd),
                "duration_years": duration
            })
            current_jd = end_jd
    else:
        # Full sequence for subsequent Antardashas
        for i in range(9):
            planet = PLANET_ORDER[(start_idx + i) % 9]
            duration_years = pratyantardasha_durations[i]
            end_jd = current_jd + (duration_years * VIMSHOTTARI_YEAR_DAYS)
            pratyantardashas.append({
                "planet": planet,
                "start_date": jd_to_date(current_jd),
                "end_date": jd_to_date(end_jd),
                "duration_years": duration_years
            })
            current_jd = end_jd
    return pratyantardashas

def calculate_antardashas(mahadasha_planet, mahadasha_start_jd, mahadasha_duration, birth_jd=None, elapsed_time=0):
    """Calculate Antardasha periods, starting from birth date for the first Mahadasha."""
    antardashas = []
    total_cycle = 120.0
    start_idx = PLANET_ORDER.index(mahadasha_planet)
    current_jd = mahadasha_start_jd

    antardasha_durations = [(PLANET_DURATIONS[PLANET_ORDER[(start_idx + i) % 9]] * mahadasha_duration) / total_cycle for i in range(9)]

    if birth_jd is not None and elapsed_time > 0:
        # Find the active Antardasha at birth
        cumulative_duration = 0
        for i, duration in enumerate(antardasha_durations):
            cumulative_duration += duration
            if cumulative_duration > elapsed_time:
                start_antardasha_idx = i
                time_already_elapsed = elapsed_time - (cumulative_duration - duration)
                remaining_in_antardasha = duration - time_already_elapsed
                break
        else:
            start_antardasha_idx = 0
            time_already_elapsed = 0
            remaining_in_antardasha = antardasha_durations[0]

        # Start from the active Antardasha at birth
        for i in range(start_antardasha_idx, 9):
            antardasha_planet = PLANET_ORDER[(start_idx + i) % 9]
            duration_years = antardasha_durations[i] if i > start_antardasha_idx else remaining_in_antardasha
            end_jd = current_jd + (duration_years * VIMSHOTTARI_YEAR_DAYS)
            pratyantardashas = raman_pratyantar_dasha(
                mahadasha_planet, antardasha_planet, current_jd, antardasha_durations[i],
                birth_jd if i == start_antardasha_idx else None,
                time_already_elapsed if i == start_antardasha_idx else 0
            )
            antardashas.append({
                "planet": antardasha_planet,
                "start_date": jd_to_date(current_jd),
                "end_date": jd_to_date(end_jd),
                "duration_years": duration_years,
                "pratyantardashas": pratyantardashas
            })
            current_jd = end_jd
    else:
        # Full sequence for subsequent Mahadashas
        for i in range(9):
            antardasha_planet = PLANET_ORDER[(start_idx + i) % 9]
            duration_years = antardasha_durations[i]
            end_jd = current_jd + (duration_years * VIMSHOTTARI_YEAR_DAYS)
            pratyantardashas = raman_pratyantar_dasha(mahadasha_planet, antardasha_planet, current_jd, duration_years)
            antardashas.append({
                "planet": antardasha_planet,
                "start_date": jd_to_date(current_jd),
                "end_date": jd_to_date(end_jd),
                "duration_years": duration_years,
                "pratyantardashas": pratyantardashas
            })
            current_jd = end_jd
    return antardashas

def calculate_prataythar_raman_periods(birth_jd, remaining_time, starting_planet, elapsed_time):
    """Calculate Mahadasha periods starting from the birth date."""
    mahadasha_sequence = []
    current_planet_idx = PLANET_ORDER.index(starting_planet)
    current_jd = birth_jd  # Start directly at birth

    for i in range(9):
        current_planet = PLANET_ORDER[(current_planet_idx + i) % 9]
        duration_years = remaining_time if i == 0 else PLANET_DURATIONS[current_planet]
        end_jd = current_jd + (duration_years * VIMSHOTTARI_YEAR_DAYS)
        antardashas = calculate_antardashas(
            current_planet, current_jd, PLANET_DURATIONS[current_planet],
            birth_jd if i == 0 else None, elapsed_time if i == 0 else 0
        )
        mahadasha_sequence.append({
            "planet": current_planet,
            "start_date": jd_to_date(current_jd),
            "end_date": jd_to_date(end_jd),
            "duration_years": duration_years,
            "antardashas": antardashas
        })
        current_jd = end_jd
    return mahadasha_sequence
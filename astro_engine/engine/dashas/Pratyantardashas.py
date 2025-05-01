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

# Fixed order of planets for Mahadasha, Antardasha, and Pratyantardasha sequence
PLANET_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]

def get_julian_day(date_str, time_str, tz_offset):
    """Convert local birth date and time to Julian Day in Universal Time (UT)."""
    local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    ut_dt = local_dt - timedelta(hours=tz_offset)
    hour_decimal = ut_dt.hour + (ut_dt.minute / 60.0) + (ut_dt.second / 3600.0)
    return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_decimal, swe.GREG_CAL)

def calculate_moon_sidereal_position(jd):
    """Calculate the Moon's sidereal longitude using Lahiri Ayanamsa."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)  # Set Lahiri Ayanamsa
    moon_tropical = swe.calc_ut(jd, swe.MOON)[0][0]  # Tropical longitude
    ayanamsa = swe.get_ayanamsa_ut(jd)  # Get Lahiri Ayanamsa for the date
    moon_sidereal = (moon_tropical - ayanamsa) % 360  # Sidereal longitude normalized to 0–360
    return moon_sidereal

def get_nakshatra_and_lord(moon_longitude):
    """Determine the nakshatra, its ruling planet, and start longitude."""
    for nakshatra, start, lord in NAKSHATRAS:
        if start <= moon_longitude < start + 13.333:
            return nakshatra, lord, start
    # Handle edge case for Revati or longitude wrap-around
    if moon_longitude >= 346.666 or moon_longitude < 0:
        return "Revati", "Mercury", 346.666
    return None, None, None

def calculate_dasha_balance(moon_longitude, nakshatra_start, lord):
    """Calculate the remaining balance and elapsed time of the starting Mahadasha."""
    nakshatra_span = 13.333  # Each nakshatra spans 13°20' (13.333 degrees)
    degrees_in_nakshatra = moon_longitude - nakshatra_start
    if degrees_in_nakshatra < 0:
        degrees_in_nakshatra += 360  # Handle wrap-around
    fraction_elapsed = degrees_in_nakshatra / nakshatra_span
    mahadasha_duration = PLANET_DURATIONS[lord]
    elapsed_time = mahadasha_duration * fraction_elapsed
    remaining_time = mahadasha_duration - elapsed_time
    return remaining_time, mahadasha_duration, elapsed_time

def calculate_pratyantardashas(antardasha_planet, antardasha_duration_years, start_date, antardasha_end_date):
    """Calculate Pratyantardashas for a given Antardasha with precise start and end dates."""
    pratyantardashas = []
    pd_start_date = start_date
    start_idx = PLANET_ORDER.index(antardasha_planet)
    
    for i in range(9):
        pd_planet = PLANET_ORDER[(start_idx + i) % 9]
        pd_duration_years = (antardasha_duration_years * PLANET_DURATIONS[pd_planet]) / 120
        pd_duration_days = pd_duration_years * 365.25
        pd_end_date = pd_start_date + timedelta(days=pd_duration_days)
        
        if i == 8:  # Adjust the last Pratyantardasha to match Antardasha end date
            pd_end_date = antardasha_end_date
        
        pratyantardashas.append({
            'planet': pd_planet,
            'start_date': pd_start_date.strftime("%Y-%m-%d"),
            'end_date': pd_end_date.strftime("%Y-%m-%d")
        })
        pd_start_date = pd_end_date
    
    return pratyantardashas

def calculate_antardashas(mahadasha_planet, mahadasha_duration, start_date, elapsed_time=0):
    """Calculate Antardashas for a given Mahadasha with nested Pratyantardashas."""
    antardashas = []
    current_date = datetime.strptime(start_date, "%Y-%m-%d")
    total_cycle = 120  # Total Vimshottari cycle in years
    start_idx = PLANET_ORDER.index(mahadasha_planet)
    
    # Calculate all Antardasha durations
    antardasha_durations = []
    for i in range(9):
        antardasha_planet = PLANET_ORDER[(start_idx + i) % 9]
        duration = (mahadasha_duration * PLANET_DURATIONS[antardasha_planet]) / total_cycle
        antardasha_durations.append(duration)
    
    # Determine the starting Antardasha based on elapsed time
    cumulative_duration = 0
    for i in range(9):
        cumulative_duration += antardasha_durations[i]
        if cumulative_duration > elapsed_time:
            start_antardasha_idx = i
            time_already_elapsed = elapsed_time - (cumulative_duration - antardasha_durations[i])
            remaining_in_antardasha = antardasha_durations[i] - time_already_elapsed
            break
    
    # Generate Antardasha periods with Pratyantardashas
    for i in range(start_antardasha_idx, 9):
        antardasha_planet = PLANET_ORDER[(start_idx + i) % 9]
        if i == start_antardasha_idx:
            duration = remaining_in_antardasha
        else:
            duration = antardasha_durations[i]
        end_date = current_date + timedelta(days=duration * 365.25)
        
        # Calculate Pratyantardashas for this Antardasha
        pratyantardashas = calculate_pratyantardashas(antardasha_planet, duration, current_date, end_date)
        
        antardashas.append({
            "planet": antardasha_planet,
            "start_date": current_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "duration_years": round(duration, 4),
            "pratyantardashas": pratyantardashas
        })
        current_date = end_date
    
    return antardashas

def calculate_mahadasha_periods(birth_date, remaining_time, starting_planet, elapsed_time):
    """Calculate Mahadasha periods with their Antardashas and Pratyantardashas."""
    mahadasha_sequence = []
    current_planet_idx = PLANET_ORDER.index(starting_planet)
    current_date = datetime.strptime(birth_date, "%Y-%m-%d")
    
    for i in range(9):  # Calculate for all 9 planets
        current_planet = PLANET_ORDER[current_planet_idx]
        mahadasha_duration = PLANET_DURATIONS[current_planet]
        if i == 0:
            # Starting Mahadasha with balance
            duration = remaining_time
            antardashas = calculate_antardashas(current_planet, mahadasha_duration, birth_date, elapsed_time)
        else:
            # Full Mahadasha
            duration = mahadasha_duration
            antardashas = calculate_antardashas(current_planet, duration, current_date.strftime("%Y-%m-%d"))
        
        end_date = current_date + timedelta(days=duration * 365.25)
        mahadasha_sequence.append({
            "planet": current_planet,
            "start_date": current_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "duration_years": round(duration, 4),
            "antardashas": antardashas
        })
        current_date = end_date
        current_planet_idx = (current_planet_idx + 1) % 9
    
    return mahadasha_sequence
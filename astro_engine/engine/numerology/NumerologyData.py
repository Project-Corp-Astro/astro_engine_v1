# calculations.py
import swisseph as swe
from datetime import datetime

# Chaldean numerology chart
chaldean_chart = {
    'a': 1, 'i': 1, 'j': 1, 'q': 1, 'y': 1,
    'b': 2, 'k': 2, 'r': 2,
    'c': 3, 'g': 3, 'l': 3, 's': 3,
    'd': 4, 'm': 4, 't': 4,
    'e': 5, 'h': 5, 'n': 5, 'x': 5,
    'u': 6, 'v': 6, 'w': 6,
    'o': 7, 'z': 7,
    'f': 8, 'p': 8
}

# Business-focused interpretations for root numbers
interpretations = {
    1: "Leadership, innovation, and independence. Ideal for pioneering ventures.",
    2: "Partnership, cooperation, and diplomacy. Good for collaborative businesses.",
    3: "Creativity, communication, and growth. Suitable for artistic or expressive enterprises.",
    4: "Stability, structure, and hard work. Best for businesses requiring discipline and organization.",
    5: "Change, adaptability, and freedom. Ideal for dynamic, fast-paced industries.",
    6: "Harmony, service, and responsibility. Good for caregiving or community-oriented businesses.",
    7: "Analysis, introspection, and wisdom. Suitable for research or knowledge-based ventures.",
    8: "Power, wealth, and material success. Ideal for businesses focused on financial growth.",
    9: "Humanitarianism, completion, and global vision. Best for charitable or socially responsible enterprises.",
    11: "Intuition, inspiration, and enlightenment. Ideal for visionary or spiritually oriented businesses.",
    22: "Master builder, practical idealism, and large-scale achievement. Suitable for ambitious, impactful projects.",
    33: "Master teacher, compassion, and healing. Good for businesses focused on education or healing."
}

# Ruling planets for each number
ruling_planets = {
    1: "Sun",
    2: "Moon",
    3: "Jupiter",
    4: "Rahu/Uranus",
    5: "Mercury",
    6: "Venus",
    7: "Ketu/Neptune",
    8: "Saturn",
    9: "Mars",
    11: "Moon (or Uranus)",
    22: "Jupiter (or Pluto)",
    33: "Jupiter (or Neptune)"
}

def calculate_chaldean_numbers(name):
    """
    Calculate the compound and root numbers for a name using Chaldean numerology.
    Only alphabetic characters are processed.
    
    Args:
        name (str): The business name.
    
    Returns:
        dict: Contains 'compound_number' and 'root_number'.
    """
    name_lower = name.lower()
    total = 0
    for char in name_lower:
        if char in chaldean_chart:
            total += chaldean_chart[char]
    compound_number = total
    if total in [11, 22, 33]:
        root_number = total
    else:
        while total > 9:
            total = sum(int(digit) for digit in str(total))
        root_number = total
    return {"compound_number": compound_number, "root_number": root_number}

def calculate_date_numerology(date_str):
    """
    Calculate the numerological value of a date in 'YYYY-MM-DD' format.
    
    Args:
        date_str (str): The date string.
    
    Returns:
        int or None: The numerological value, or None if invalid.
    """
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        digits = [int(char) for char in date_str if char.isdigit()]
        total = sum(digits)
        while total > 9 and total not in [11, 22, 33]:
            total = sum(int(digit) for digit in str(total))
        return total
    except ValueError:
        return None

def get_sun_sign(date_str):
    """
    Calculate the Sun's zodiac sign for a given date using pyswisseph.
    Assumes 12:00 UT for simplicity.
    
    Args:
        date_str (str): Date in 'YYYY-MM-DD' format.
    
    Returns:
        str or None: The Sun's sign, or None if calculation fails.
    """
    try:
        year, month, day = map(int, date_str.split('-'))
        jd = swe.julday(year, month, day, 12.0)
        sun_pos, _ = swe.calc_ut(jd, swe.SUN)
        longitude = sun_pos[0]
        sign_index = int(longitude / 30)
        signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                 "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        return signs[sign_index]
    except Exception:
        return None

def calculate_numerology(data):
    """
    Calculate numerology data for a business name and optional founding date.
    
    Args:
        data (dict): Contains 'name' and optional 'founding_date'.
    
    Returns:
        dict: Contains numerology calculations and interpretations.
    """
    name = data['name']
    if not isinstance(name, str):
        raise ValueError("'name' must be a string")

    # Calculate numbers for the name
    numbers = calculate_chaldean_numbers(name)
    compound_number = numbers['compound_number']
    root_number = numbers['root_number']
    interpretation = interpretations.get(root_number, "No interpretation available.")
    ruling_planet = ruling_planets.get(root_number, "Unknown")

    # Base response
    response = {
        "original_name": name,
        "compound_number": compound_number,
        "root_number": root_number,
        "ruling_planet": ruling_planet,
        "interpretation": interpretation
    }

    # Handle optional founding_date
    if 'founding_date' in data:
        founding_date = data['founding_date']
        date_numerology = calculate_date_numerology(founding_date)
        sun_sign = get_sun_sign(founding_date)
        if date_numerology is not None and sun_sign is not None:
            date_ruling_planet = ruling_planets.get(date_numerology, "Unknown")
            response["date_numerology"] = date_numerology
            response["date_ruling_planet"] = date_ruling_planet
            response["sun_sign"] = sun_sign
            # Compatibility message
            if root_number == date_numerology:
                compatibility = f"Harmonious match: both the business name and founding date reduce to {root_number}, ruled by {ruling_planet}."
            elif ruling_planet == date_ruling_planet:
                compatibility = f"Aligned energies: both the business name and founding date are influenced by {ruling_planet}."
            else:
                compatibility = f"Diverse influences: the business name is ruled by {ruling_planet}, while the founding date is ruled by {date_ruling_planet}. Consider how these energies interact."
            response["compatibility"] = compatibility
        else:
            response["date_error"] = "Invalid founding_date format (use 'YYYY-MM-DD') or calculation error."

    return response
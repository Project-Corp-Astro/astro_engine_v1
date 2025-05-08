import datetime

# Fixed Lo Shu Grid layout
LO_SHU_LAYOUT = [
    [4, 9, 2],
    [3, 5, 7],
    [8, 1, 6]
]

# Arrow patterns and their interpretations
ARROWS = {
    "Top Row": {"numbers": [4, 9, 2], "interpretation": "You possess the Arrow of Planning, indicating exceptional organizational skills and a strategic mindset."},
    "Middle Row": {"numbers": [3, 5, 7], "interpretation": "You have the Arrow of Activity, reflecting a vibrant, energetic, and dynamic personality."},
    "Bottom Row": {"numbers": [8, 1, 6], "interpretation": "The Arrow of Practicality is yours, showcasing a grounded, practical approach to life."},
    "Left Column": {"numbers": [4, 3, 8], "interpretation": "The Arrow of Intellect highlights your strong analytical abilities and intellectual prowess."},
    "Middle Column": {"numbers": [9, 5, 1], "interpretation": "With the Arrow of Spirituality, you exhibit deep spiritual insight and philosophical understanding."},
    "Right Column": {"numbers": [2, 7, 6], "interpretation": "The Arrow of Willpower signifies your remarkable determination and resilience."},
    "Main Diagonal": {"numbers": [4, 5, 6], "interpretation": "The Arrow of Determination marks you as a focused and persistent individual."},
    "Secondary Diagonal": {"numbers": [2, 5, 8], "interpretation": "You carry the Arrow of Sensitivity, revealing a highly empathetic and emotionally attuned nature."}
}

# Vedic astrology planet associations for numbers 1-9
PLANET_ASSOCIATIONS = {
    1: "Sun - Leadership, vitality",
    2: "Moon - Emotions, intuition",
    3: "Jupiter - Wisdom, expansion",
    4: "Rahu - Ambition, material desires",
    5: "Mercury - Communication, intellect",
    6: "Venus - Love, beauty",
    7: "Ketu - Spirituality, detachment",
    8: "Saturn - Discipline, challenges",
    9: "Mars - Energy, courage"
}

# Interpretations for each number (1-9) with Vedic astrology insights
NUMBER_INTERPRETATIONS = {
    1: f"You excel in communication and embrace independence, influenced by the Water element. Associated with the {PLANET_ASSOCIATIONS[1]}, radiating authority and life force.",
    2: f"Your intuition and nurturing qualities shine, guided by the Earth element. Linked to the {PLANET_ASSOCIATIONS[2]}, fostering emotional depth and psychic sensitivity.",
    3: f"Creativity and a drive for growth define you, rooted in the Wood element. Connected to {PLANET_ASSOCIATIONS[3]}, blessing you with knowledge and prosperity.",
    4: f"You bring stability and organization to all you do, supported by the Wood element. Associated with {PLANET_ASSOCIATIONS[4]}, fueling ambition and worldly success.",
    5: f"Adaptability and a love for freedom are your strengths, tied to the Earth element. Linked to {PLANET_ASSOCIATIONS[5]}, sharpening your wit and versatility.",
    6: f"Responsibility and caregiving come naturally to you, shaped by the Metal element. Connected to {PLANET_ASSOCIATIONS[6]}, enhancing charm and harmonious relationships.",
    7: f"Spirituality and introspection are key aspects of your character, linked to the Metal element. Associated with {PLANET_ASSOCIATIONS[7]}, guiding you toward liberation and inner peace.",
    8: f"Abundance and power flow through you, driven by the Earth element. Linked to {PLANET_ASSOCIATIONS[8]}, teaching resilience through life’s trials.",
    9: f"Passion and ambition fuel your journey, ignited by the Fire element. Connected to {PLANET_ASSOCIATIONS[9]}, igniting courage and transformative energy."
}

# Interpretation for missing numbers
MISSING_NUMBER_INTERPRETATION = "These absent numbers indicate karmic lessons or areas of growth, where the planetary energies are less active, urging you to seek balance."

def calculate_primary_number(birth_date):
    """Calculate the Primary Number (Life Path Number) from the birth date."""
    date_str = birth_date.replace("-", "")
    total = sum(int(d) for d in date_str)
    while total > 9:
        total = sum(int(d) for d in str(total))
    return total

def calculate_destiny_number(birth_date):
    """Calculate the Destiny Number from the birth date (same as Primary Number for now)."""
    return calculate_primary_number(birth_date)

def calculate_kua_number(birth_year, gender):
    """Calculate the Kua Number based on birth year and gender."""
    year_str = birth_year[-2:]  # Last two digits of the birth year
    total = sum(int(d) for d in year_str)
    while total > 9:
        total = sum(int(d) for d in str(total))
    if gender.lower() == "male":
        kua = (10 - total) % 9 or 9
    else:
        kua = (total + 5) % 9 or 9
    return kua

def calculate_lo_shu_grid(birth_date, gender):
    """
    Calculate the Lo Shu Grid numerology based on a birth date and gender.
    Returns a dictionary with grid frequencies, present numbers, missing numbers, present arrows, and interpretations.
    """
    try:
        # Parse and validate the birth date
        date_obj = datetime.datetime.strptime(birth_date, "%Y-%m-%d")
        date_str = date_obj.strftime("%Y%m%d")
        
        # Extract digits as a list of integers
        digits = [int(d) for d in date_str]
        
        # Calculate frequency of digits 0-9
        frequency = [digits.count(i) for i in range(10)]
        
        # Map frequencies to the 3x3 grid
        grid = [
            [
                f"{LO_SHU_LAYOUT[row][col]}:{frequency[LO_SHU_LAYOUT[row][col]]}"
                for col in range(3)
            ]
            for row in range(3)
        ]
        
        # Present numbers (frequency > 0 for 1-9)
        present_numbers = [str(num) for num in range(1, 10) if frequency[num] > 0]
        
        # Missing numbers (frequency = 0 for 1-9)
        missing_numbers = [str(num) for num in range(1, 10) if frequency[num] == 0]
        
        # Check for present arrows
        present_arrows = [
            {
                "name": name,
                "interpretation": ARROWS[name]["interpretation"]
            }
            for name, arrow in ARROWS.items()
            if all(frequency[num] > 0 for num in arrow["numbers"])
        ]
        
        # Calculate Primary, Destiny, and Kua Numbers
        primary_number = calculate_primary_number(birth_date)
        destiny_number = calculate_destiny_number(birth_date)
        birth_year = birth_date.split("-")[0]
        kua_number = calculate_kua_number(birth_year, gender)
        
        # Generate interpretations
        interpretations = {
            "present_numbers": [
                {"number": num, "interpretation": NUMBER_INTERPRETATIONS[int(num)]}
                for num in present_numbers
            ],
            "missing_numbers": {
                "numbers": missing_numbers,
                "interpretation": MISSING_NUMBER_INTERPRETATION
            },
            "present_arrows": present_arrows,
            "primary_number": f"Your Primary Number is {primary_number}, governed by {PLANET_ASSOCIATIONS[primary_number]}. This is your soul’s guiding force, illuminating your life’s purpose in the Vedic cosmic order.",
            "destiny_number": f"Your Destiny Number is {destiny_number}, ruled by {PLANET_ASSOCIATIONS[destiny_number]}. This number shapes your fate, reflecting the karmic path you are destined to walk.",
            "kua_number": f"Your Kua Number is {kua_number}, aligning your personal energy with the universal flow. In Vedic terms, it harmonizes your earthly existence with celestial influences."
        }
        
        # Prepare the response
        result = {
            "grid": grid,
            "present_numbers": present_numbers,
            "missing_numbers": missing_numbers,
            "present_arrows": [arrow["name"] for arrow in present_arrows],
            "primary_number": primary_number,
            "destiny_number": destiny_number,
            "kua_number": kua_number,
            "interpretations": interpretations
        }
        return result
    
    except ValueError:
        return {"error": "Invalid birth_date format. Please use 'YYYY-MM-DD'."}
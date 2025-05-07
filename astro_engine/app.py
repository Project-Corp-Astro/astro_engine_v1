# C:\Users\prave\Documents\Astro_Engine\astro_engine\app.py
from datetime import datetime
import logging
from venv import logger
from flask import Flask, request, jsonify
from flask_cors import CORS
import swisseph as swe

from astro_engine.engine.ashatakavargha.Binnastakavargha import astro_utils_calculate_ascendant, astro_utils_calculate_bhinnashtakavarga, astro_utils_calculate_planet_positions, astro_utils_format_dms, astro_utils_get_julian_day, astro_utils_get_sign_index, astro_utils_validate_totals
from astro_engine.engine.ashatakavargha.Sarvasthakavargha import astro_utils_calculate_positions, astro_utils_calculate_sarvashtakavarga, astro_utils_map_to_houses
from astro_engine.engine.lagnaCharts.ArudhaLagna import LORDS, SWE_PLANETS, ZODIAC_SIGNS, calculate_planet_data, get_arudha_lagna
from astro_engine.engine.lagnaCharts.KPLagna import PLANETS, convert_to_julian_day, determine_significators, fetch_house_cusps, fetch_planet_positions, identify_nakshatra, identify_sign, identify_sub_lord, map_planets_to_houses



app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
logging.basicConfig(level=logging.DEBUG)


# from astro_engine.engine.ashatakavargha.Binnastakavargha import bv_calculate_ascendant, bv_calculate_ayanamsa, bv_calculate_bhinnashtakavarga_matrix, bv_calculate_sidereal_longitude, bv_format_dms, bv_get_julian_day, bv_get_sign_index, bv_validate_totals

# from astro_engine.engine.ashatakavargha.Binnastakavargha import bv_calculate_ascendant, bv_calculate_ayanamsa, bv_calculate_bhinnashtakavarga_matrix, bv_calculate_sidereal_longitude, bv_format_dms, bv_get_julian_day, bv_get_sign_index, bv_validate_totals
from astro_engine.engine.dashas.AntarDasha import calculate_dasha_balance, calculate_mahadasha_periods, calculate_moon_sidereal_position, get_nakshatra_and_lord
from astro_engine.engine.dashas.Pratyantardashas import calculate_dasha_balance, calculate_mahadasha_periods, calculate_moon_sidereal_position, get_nakshatra_and_lord
from astro_engine.engine.dashas.Sookashama import calculate_dasha_balance, calculate_mahadasha_periods, calculate_moon_sidereal_position, get_nakshatra_and_lord
from astro_engine.engine.divisionalCharts.AkshavedamshaD45 import calculate_d45_chart, format_dms
from astro_engine.engine.divisionalCharts.SaptavimshamshaD27 import SIGN_NAMES, calculate_d1_positions, calculate_d27_houses, calculate_d27_positions
from astro_engine.engine.divisionalCharts.ShashtiamshaD60 import calculate_d60_chart
from astro_engine.engine.divisionalCharts.VimshamshaD20 import calculate_d20_chart
from astro_engine.engine.natalCharts.SudharashanaChakara import calculate_sidereal_positions, generate_chart, get_sign
from astro_engine.engine.natalCharts.SunChart import assign_planets_to_houses, calculate_planetary_positions, calculate_whole_sign_cusps, validate_input
from astro_engine.engine.natalCharts.MoonChart import assign_planets_to_houses, calculate_whole_sign_cusps, format_dms, get_julian_day
from .engine.natalCharts.natal import calculate_natal_chart
from .engine.natalCharts.transit import calculate_transit_chart
from .engine.divisionalCharts.ChathruthamshaD4 import calculate_d4_chart
from .engine.divisionalCharts.ChaturvimshamshaD24 import calculate_d24_chart
from .engine.divisionalCharts.DashamshaD10 import calculate_d10_chart
from .engine.divisionalCharts.DreshkanaD3 import  PLANET_NAMES, calculate_d3_chart, get_julian_day
from .engine.divisionalCharts.DwadashamshaD12 import  calculate_d12_chart
from .engine.divisionalCharts.HoraD2 import  SIGNS, calculate_d2_chart
from .engine.divisionalCharts.KvedamshaD40 import  calculate_d40_chart
from .engine.divisionalCharts.NavamshaD9 import  calculate_navamsa_chart
from .engine.divisionalCharts.SaptamshaD7 import  calculate_d7_chart
from .engine.divisionalCharts.ShodasmasD16 import  calculate_d16_chart
from .engine.lagnaCharts.Sripathi import  calculate_ascendant, get_planet_data
from .engine.numerology.SynatryChart import  calculate_synastry
from .engine.numerology.CompositeChart import  calculate_composite_chart, validate_person_data 
from .engine.numerology.ProgressChart import  calculate_progressed_chart
from .engine.numerology.NumerologyData import  calculate_numerology

# Set Swiss Ephemeris path
swe.set_ephe_path('astro_engine/ephe')



app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


# *********************************************************************************************************
# ***********************************  Divisional Charts ********************************************
# *********************************************************************************************************


# Natal Chart
@app.route('/natal', methods=['POST'])
def natal_chart():
    try:
        birth_data = request.get_json()
        if not birth_data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in birth_data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        latitude = float(birth_data['latitude'])
        longitude = float(birth_data['longitude'])
        timezone_offset = float(birth_data['timezone_offset'])
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            return jsonify({"error": "Invalid latitude or longitude"}), 400

        response = calculate_natal_chart(birth_data)
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


# Transit or Gochar Chart 
@app.route('/transit', methods=['POST'])
def transit_chart():
    """
    API endpoint to calculate the transit chart based on birth details and current time.
    
    Method: POST
    Input: JSON object with user_name, birth_date, birth_time, latitude, longitude, timezone_offset.
    Output: JSON object containing the transit chart data.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        # Calculate transit chart using the function from calculations.py
        response = calculate_transit_chart(data)
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


# Sun Chart 
@app.route('/calculate_sun', methods=['POST'])
def calculate_sun_chart():
    """
    API endpoint to calculate Sun Chart (sidereal) with Whole Sign house system.
    Input JSON Format:
    {
        "user_name": "Anusha kayakokula",
        "birth_date": "1998-10-15",
        "birth_time": "10:40:30",
        "latitude": "17.3850",
        "longitude": "78.4867",
        "timezone_offset": 5.5
    }
    Returns:
        JSON response with Surya Lagna, house cusps, planetary positions with retrograde status, and metadata
    """
    try:
        # Parse and validate input
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        validate_input(data)
        
        # Extract input data
        user_name = data.get('user_name', 'Unknown')
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        # Calculate Julian Day
        jd = get_julian_day(birth_date, birth_time, tz_offset)

        # Calculate planetary positions with retrograde status
        planetary_positions = calculate_planetary_positions(jd)

        # Sun's position (Surya Lagna)
        sun_longitude = planetary_positions['Sun'][0]
        sun_sign_index = int(sun_longitude // 30)
        sun_sign = SIGNS[sun_sign_index]
        sun_degree = sun_longitude % 30

        # Calculate house cusps for Sun Chart (Whole Sign)
        house_cusps = calculate_whole_sign_cusps(sun_longitude)

        # Assign planets to houses in Sun Chart
        house_assignments = assign_planets_to_houses(planetary_positions, sun_sign_index)

        # Prepare house cusps data
        house_data = [
            {
                "house": i + 1,
                "cusp": format_dms(house_cusps[i]),
                "sign": SIGNS[(sun_sign_index + i) % 12]
            }
            for i in range(12)
        ]

        # Prepare planetary positions data with retrograde status
        planetary_data = [
            {
                "planet": planet,
                "longitude": format_dms(longitude),
                "sign": SIGNS[int(longitude // 30)],
                "retrograde": retrograde,
                "house": house_assignments[planet]
            }
            for planet, (longitude, retrograde) in planetary_positions.items()
        ]

        # Construct response
        response = {
            "user_name": user_name,
            "surya_lagna": {
                "longitude": format_dms(sun_longitude),
                "sign": sun_sign,
                "degree": format_dms(sun_degree)
            },
            "house_cusps": house_data,
            "planetary_positions": planetary_data,
            "metadata": {
                "ayanamsa": "Lahiri",
                "house_system": "Whole Sign",
                "calculation_time": datetime.utcnow().isoformat(),
                "input": {
                    "birth_date": birth_date,
                    "birth_time": birth_time,
                    "latitude": latitude,
                    "longitude": longitude,
                    "timezone_offset": tz_offset
                }
            }
        }
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation failed: {str(e)}"}), 500


# Moon Chart 
@app.route('/calculate_moon', methods=['POST'])
def calculate_moon_chart():
    """
    API endpoint to calculate Moon Chart (sidereal) with Whole Sign house system.
    Input JSON Format:
    {
        "user_name": "Anusha kayakokula",
        "birth_date": "1998-10-15",
        "birth_time": "10:40:30",
        "latitude": "17.3850",
        "longitude": "78.4867",
        "timezone_offset": 5.5
    }
    Returns:
        JSON response with Chandra Lagna, house cusps, planetary positions, and metadata
    """
    try:
        # Parse and validate input
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        validate_input(data)
        
        # Extract input data
        user_name = data.get('user_name', 'Unknown')
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        # Calculate Julian Day
        jd = get_julian_day(birth_date, birth_time, tz_offset)

        # Calculate planetary positions with retrograde status
        planetary_positions = calculate_planetary_positions(jd)

        # Moon's position (Chandra Lagna)
        moon_longitude = planetary_positions['Moon'][0]
        moon_sign_index = int(moon_longitude // 30)
        moon_sign = SIGNS[moon_sign_index]
        moon_degree = moon_longitude % 30

        # Calculate house cusps for Moon Chart (Whole Sign)
        house_cusps = calculate_whole_sign_cusps(moon_longitude)

        # Assign planets to houses in Moon Chart
        house_assignments = assign_planets_to_houses(planetary_positions, moon_sign_index)

        # Prepare house cusps data
        house_data = [
            {
                "house": i + 1,
                "cusp": format_dms(house_cusps[i]),
                "sign": SIGNS[(moon_sign_index + i) % 12]
            }
            for i in range(12)
        ]

        # Prepare planetary positions data with retrograde status
        planetary_data = [
            {
                "planet": planet,
                "longitude": format_dms(longitude),
                "sign": SIGNS[int(longitude // 30)],
                "retrograde": retrograde,
                "house": house_assignments[planet]
            }
            for planet, (longitude, retrograde) in planetary_positions.items()
        ]

        # Construct response
        response = {
            "user_name": user_name,
            "chandra_lagna": {
                "longitude": format_dms(moon_longitude),
                "sign": moon_sign,
                "degree": format_dms(moon_degree)
            },
            "house_cusps": house_data,
            "planetary_positions": planetary_data,
            "metadata": {
                "ayanamsa": "Lahiri",
                "house_system": "Whole Sign",
                "calculation_time": datetime.utcnow().isoformat(),
                "input": {
                    "birth_date": birth_date,
                    "birth_time": birth_time,
                    "latitude": latitude,
                    "longitude": longitude,
                    "timezone_offset": tz_offset
                }
            }
        }
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation failed: {str(e)}"}), 500



# Sudharashana Chakara 
@app.route('/calculate_sudarshan_chakra', methods=['POST'])
def calculate_sudarshan_chakra():
    """
    Flask endpoint to calculate the Sudarshan Chakra based on birth details.
    
    Expected JSON Input:
    {
        "user_name": "Anusha kayakokula",
        "birth_date": "1998-10-15",
        "birth_time": "10:40:30",
        "latitude": "17.3850",
        "longitude": "78.4867",
        "timezone_offset": 5.5
    }
    
    Returns:
        JSON response with Sudarshan Chakra details or error message
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        user_name = data.get('user_name', 'Unknown')
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        # Calculate Julian Day
        jd_birth = get_julian_day(birth_date, birth_time, tz_offset)

        # Calculate sidereal positions
        positions = calculate_sidereal_positions(jd_birth, latitude, longitude)

        # Determine reference sign indices
        asc_sign, _ = get_sign(positions["Ascendant"])
        moon_sign, _ = get_sign(positions["Moon"])
        sun_sign, _ = get_sign(positions["Sun"])
        asc_sign_idx = SIGNS.index(asc_sign)
        moon_sign_idx = SIGNS.index(moon_sign)
        sun_sign_idx = SIGNS.index(sun_sign)

        # Generate the three charts
        lagna_chart = generate_chart(positions, asc_sign_idx)
        chandra_chart = generate_chart(positions, moon_sign_idx)
        surya_chart = generate_chart(positions, sun_sign_idx)

        # Construct the Sudarshan Chakra response
        response = {
            "user_name": user_name,
            "sudarshan_chakra": {
                "lagna_chart": lagna_chart,
                "chandra_chart": chandra_chart,
                "surya_chart": surya_chart
            }
        }
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input format: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500



# Hora (D-2)
@app.route('/calculate_d2', methods=['POST'])
def calculate_d2():
    """
    Flask API endpoint to calculate the Hora (D2) chart.

    Input (JSON):
    - birth_date (str): 'YYYY-MM-DD'
    - birth_time (str): 'HH:MM:SS'
    - latitude (float): Birth latitude
    - longitude (float): Birth longitude
    - timezone_offset (float): Offset from UTC in hours

    Output (JSON):
    - D2 ascendant, planetary positions, house signs, and metadata
    """
    try:
        # Parse JSON request
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Validate required fields
        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        # Calculate D2 chart using the function from calculations.py
        response = calculate_d2_chart(data)
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500



# Dreshkana (D-3)
@app.route('/calculate_d3', methods=['POST'])
def calculate_d3_chart_endpoint():
    """
    API endpoint to calculate D3 chart with retrograde status.

    Method: POST
    Input: JSON object with birth_date, birth_time, latitude, longitude, timezone_offset.
    Output: JSON object containing the D3 chart data.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required fields"}), 400

        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        jd = get_julian_day(birth_date, birth_time, tz_offset)
        d3_data = calculate_d3_chart(jd, latitude, longitude)

        response = {
            "ascendant": d3_data['Ascendant'],
            "planets": {planet: d3_data[planet] for planet in PLANET_NAMES}
        }
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error in D3 chart calculation: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


# Chaturthamsha (D-4)
@app.route('/calculate_d4', methods=['POST'])
def calculate_d4():
    """
    API endpoint to calculate the Chaturthamsha (D4) chart.
    
    Method: POST
    Input: JSON object with birth_date, birth_time, latitude, longitude, timezone_offset.
    Output: JSON object containing the D4 chart data.
    """
    try:
        # Get JSON data
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Validate required fields
        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        # Calculate D4 chart using the function from calculations.py
        response = calculate_d4_chart(data)
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


# Saptamsha (D-7)
@app.route('/calculate_d7', methods=['POST'])
def calculate_d7_chart_endpoint():
    """API endpoint to calculate D7 chart from birth details."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Required fields (user_name is optional)
        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required fields"}), 400

        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        # Calculate Julian Day and D7 chart
        jd = get_julian_day(birth_date, birth_time, tz_offset)
        d7_data = calculate_d7_chart(jd, latitude, longitude)

        # Prepare response
        response = {
            "ascendant": d7_data['Ascendant'],
            "planets": {planet: d7_data[planet] for planet in PLANET_NAMES}
        }
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error in D7 calculation: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


# Dashamsha (D-10)
@app.route('/calculate_d10', methods=['POST'])
def calculate_d10():
    """
    Flask API endpoint to calculate the Dashamsha (D10) chart accurately.

    Input (JSON):
    - birth_date (str): 'YYYY-MM-DD'
    - birth_time (str): 'HH:MM:SS'
    - latitude (float): Birth latitude
    - longitude (float): Birth longitude
    - timezone_offset (float): Offset from UTC in hours

    Output (JSON):
    - Planetary positions, ascendant with conjunctions, house signs, and metadata
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        # Calculate D10 chart using the function from calculations.py
        response = calculate_d10_chart(data)
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


# Dwadashamsha (D-12)
@app.route('/calculate_d12', methods=['POST'])
def calculate_d12():
    """
    Flask API endpoint to calculate the Dwadasamsa (D12) chart.

    Input (JSON):
    - birth_date (str): 'YYYY-MM-DD'
    - birth_time (str): 'HH:MM:SS'
    - latitude (float): Birth latitude
    - longitude (float): Birth longitude
    - timezone_offset (float): Offset from UTC in hours

    Output (JSON):
    - D12 ascendant, planetary positions, house signs, and metadata
    """
    try:
        # Parse JSON request
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Validate required fields
        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        # Calculate D12 chart using the function from calculations.py
        response = calculate_d12_chart(data)
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


# Shodashamsha (D-16)
@app.route('/calculate_d16', methods=['POST'])
def calculate_d16():
    """
    API endpoint to calculate the Shodasamsa (D16) chart.
    
    Method: POST
    Input: JSON object with birth_date, birth_time, latitude, longitude, timezone_offset, enforce_opposition (optional).
    Output: JSON object containing the D16 chart data.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required fields"}), 400

        # Calculate D16 chart using the function from calculations.py
        response = calculate_d16_chart(data)
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500



# Vimshamsha (D-20)
@app.route('/calculate_d20', methods=['POST'])
def calculate_d20():
    """
    API endpoint to calculate the D20 (Vimsamsa) chart.
    
    Expects JSON input:
    {
        "birth_date": "YYYY-MM-DD",
        "birth_time": "HH:MM:SS",
        "latitude": float,
        "longitude": float,
        "timezone_offset": float,
        "user_name": str (optional)
    }
    
    Returns:
        JSON response with D20 chart details or error message
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        # Extract input data
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])
        user_name = data.get('user_name', 'Unknown')

        # Calculate D20 chart data
        chart_data = calculate_d20_chart(birth_date, birth_time, latitude, longitude, tz_offset)

        # Construct full response with metadata
        response = {
            "user_name": user_name,
            **chart_data,
            "metadata": {
                "ayanamsa": "Lahiri",
                "chart_type": "Vimsamsa (D20)",
                "house_system": "Whole Sign",
                "calculation_time": datetime.utcnow().isoformat()
            }
        }
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input format: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


# Chaturvimshamsha (D-24)
@app.route('/calculate_d24', methods=['POST'])
def calculate_d24():
    """
    API endpoint to calculate the Chaturvimshamsha (D24) chart.
    
    Method: POST
    Input: JSON object with birth_date, birth_time, latitude, longitude, timezone_offset.
    Output: JSON object containing the D24 chart data.
    """
    try:
        # Get JSON data
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Validate required fields
        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        # Calculate D24 chart using the function from calculations.py
        response = calculate_d24_chart(data)
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


# Saptavimshamsha (D-27)
@app.route('/calculate_d27', methods=['POST'])
def calculate_d27_chart():
    """Calculate D27 chart from birth details."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        user_name = data.get('user_name', 'Unknown')
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        jd = get_julian_day(birth_date, birth_time, tz_offset)
        d1_positions = calculate_d1_positions(jd, latitude, longitude)
        d27_positions = calculate_d27_positions(d1_positions)
        d27_asc_sign = d27_positions['Ascendant']
        d27_houses = calculate_d27_houses(d27_asc_sign, d27_positions)

        response = {
            "user_name": user_name,
            "d27_chart": {
                "positions": {planet: SIGN_NAMES[sign - 1] for planet, sign in d27_positions.items()},
                "houses": d27_houses
            }
        }
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500



# Khavedamsha (D-40)
@app.route('/calculate_d40', methods=['POST'])
def calculate_d40():
    """
    API endpoint to calculate the D40 chart.
    
    Method: POST
    Input: JSON object with birth_date, birth_time, latitude, longitude, timezone_offset.
    Output: JSON object containing the D40 chart data.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Extract required fields
        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        # Calculate D40 chart using the function from calculations.py
        response = calculate_d40_chart(birth_date, birth_time, latitude, longitude, tz_offset)
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500



# Akshavedamsha (D-45)
@app.route('/calculate_d45', methods=['POST'])
def calculate_d45():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        # Calculate Julian Day
        jd_ut = get_julian_day(birth_date, birth_time, tz_offset)

        # Calculate D45 chart
        chart_data = calculate_d45_chart(jd_ut, latitude, longitude)

        # Prepare response
        response = {
            "user_name": data.get('user_name', 'Unknown'),
            **chart_data,
            "metadata": {
                "ayanamsa": "Lahiri",
                "chart_type": "Akshavedamsa (D45)",
                "house_system": "Whole Sign",
                "calculation_time": datetime.utcnow().isoformat()
            }
        }
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input format: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


# Shashtiamsha (D-60)
@app.route('/calculate_d60', methods=['POST'])
def calculate_d60():
    """
    API endpoint to calculate the D60 (Shashtiamsha) chart.
    
    Expected Input (JSON):
    {
        "user_name": "Anusha kayakokula",
        "birth_date": "1998-10-15",
        "birth_time": "10:40:30",
        "latitude": "17.3850",
        "longitude": "78.4867",
        "timezone_offset": 5.5
    }
    
    Returns:
        JSON: D60 chart details including ascendant, planetary positions, house signs, and metadata.
    """
    try:
        # Parse input JSON
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Validate required fields
        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])
        user_name = data.get('user_name', 'Unknown')

        # Calculate Julian Day
        jd_ut = get_julian_day(birth_date, birth_time, tz_offset)

        # Calculate D60 chart data
        chart_data = calculate_d60_chart(jd_ut, latitude, longitude)

        # Construct response
        response = {
            "user_name": user_name,
            **chart_data,
            "metadata": {
                "ayanamsa": "Lahiri",
                "chart_type": "Shashtiamsha (D60)",
                "house_system": "Whole Sign",
                "calculation_time": datetime.utcnow().isoformat()
            }
        }
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route('/navamsa', methods=['POST'])
def navamsa_chart():
    """
    Flask API endpoint to calculate the Navamsa (D9) chart.

    Input (JSON):
    - birth_date (str): 'YYYY-MM-DD'
    - birth_time (str): 'HH:MM:SS'
    - latitude (float): Birth latitude
    - longitude (float): Birth longitude
    - timezone_offset (float): Offset from UTC in hours

    Output (JSON):
    - Planetary positions, ascendant, and metadata
    """
    try:
        # Parse JSON request
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Validate required fields
        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        # Calculate D9 chart using the function from calculations.py
        response = calculate_navamsa_chart(data)
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500






# *********************************************************************************************************
# **************************************  Lagna Charts ****************************************************
# *********************************************************************************************************


# Sripathi Bhava 
@app.route('/calculate_sripathi_bhava', methods=['POST'])
def calculate_sripathi_bhava():
    """Compute the Sripathi Bhava Chart and return JSON output."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required_fields):
            return jsonify({"error": "Missing required parameters"}), 400

        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        logger.debug(f"Input: Date={birth_date}, Time={birth_time}, Lat={latitude}, Lon={longitude}, TZ Offset={tz_offset}")

        jd_ut = get_julian_day(birth_date, birth_time, tz_offset)
        asc_lon, asc_sign_index, cusps = calculate_ascendant(jd_ut, latitude, longitude)
        asc_sign = SIGNS[asc_sign_index]
        asc_degrees = asc_lon % 30

        natal_positions = get_planet_data(jd_ut, asc_lon, cusps)

        response = {
            "ascendant": {
                "sign": asc_sign,
                "degrees": round(asc_degrees, 4)
            },
            "planets": natal_positions
        }
        logger.debug(f"Output JSON: {response}")
        return jsonify(response), 200

    except ValueError as ve:
        logger.error(f"Invalid input format: {str(ve)}")
        return jsonify({"error": f"Invalid input format: {str(ve)}"}), 400
    except Exception as e:
        logger.error(f"Calculation error: {str(e)}")
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500
    

#   KP Bhava

@app.route('/calculate_kp_bhava', methods=['POST'])
def process_kp_bhava():
    """Process birth details to compute KP Bhava Chart."""
    data = request.get_json()
    try:
        user_name = data['user_name']
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        jd = convert_to_julian_day(birth_date, birth_time, tz_offset)
        planet_positions = fetch_planet_positions(jd)
        house_cusps = fetch_house_cusps(jd, latitude, longitude)
        house_assignments = map_planets_to_houses(planet_positions, house_cusps)
        significators = determine_significators(planet_positions, house_cusps)

        planet_details = {}
        for planet in PLANETS:
            pos = planet_positions[planet]
            planet_details[planet] = {
                'longitude': round(pos, 4),
                'sign': identify_sign(pos),
                'nakshatra': identify_nakshatra(pos),
                'sub_lord': identify_sub_lord(pos),
                'house': house_assignments.get(planet, None),
                'retrograde': planet_positions.get(f"{planet}_retro", False)
            }

        cusp_details = []
        for i, cusp in enumerate(house_cusps, 1):
            cusp_details.append({
                'house': i,
                'longitude': round(cusp, 4),
                'sign': identify_sign(cusp),
                'nakshatra': identify_nakshatra(cusp),
                'sub_lord': identify_sub_lord(cusp)
            })

        lagna_longitude = house_cusps[0]
        lagna_sign = identify_sign(lagna_longitude)

        response = {
            'user_name': user_name,
            'lagna_sign': lagna_sign,
            'house_cusps': cusp_details,
            'planetary_positions': planet_details,
            'significators': significators
        }
        return jsonify(response), 200

    except KeyError as e:
        return jsonify({"error": f"Missing input field: {str(e)}"}), 400
    except ValueError as e:
        return jsonify({"error": f"Invalid input value: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation failed: {str(e)}"}), 500


#  Arudha  Lagna :

@app.route('/calculate_arudha_lagna', methods=['POST'])
def calculate_arudha_lagna():
    """Calculate Arudha Lagna chart with retrograde status."""
    try:
        data = request.get_json()
        if not data:
            logging.error("No JSON data provided")
            return jsonify({"error": "No JSON data provided"}), 400

        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(field in data for field in required_fields):
            logging.error("Missing required fields")
            return jsonify({"error": "Missing required fields"}), 400

        user_name = data.get('user_name', 'Unknown')
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        # Calculate Julian Day
        jd = get_julian_day(birth_date, birth_time, tz_offset)

        # Calculate sidereal Ascendant and its sign
        asc_lon = calculate_ascendant(jd, latitude, longitude)
        asc_sign = get_sign(asc_lon)

        # Calculate planetary positions and retrograde status
        planet_data = {}
        for planet, code in zip(PLANETS, SWE_PLANETS):
            if planet == 'Ketu':
                rahu_lon, rahu_retro = calculate_planet_data(jd, swe.MEAN_NODE)
                ketu_lon = (rahu_lon + 180) % 360
                ketu_retro = rahu_retro  # Ketu retrogrades with Rahu
                planet_data[planet] = {'longitude': ketu_lon, 'sign': get_sign(ketu_lon), 'retrograde': ketu_retro}
            else:
                lon, retro = calculate_planet_data(jd, code)
                planet_data[planet] = {'longitude': lon, 'sign': get_sign(lon), 'retrograde': retro}

        # Determine Lagna lord and its sign
        lagna_lord = LORDS[asc_sign]
        lord_sign = planet_data[lagna_lord]['sign']

        # Calculate Arudha Lagna
        al_sign = get_arudha_lagna(asc_sign, lord_sign)

        # Construct AL chart with houses relative to Arudha Lagna
        al_index = ZODIAC_SIGNS.index(al_sign)
        al_houses = {}
        for planet, data in planet_data.items():
            sign = data['sign']
            sign_index = ZODIAC_SIGNS.index(sign)
            house = (sign_index - al_index) % 12 + 1
            al_houses[planet] = {'sign': sign, 'house': house, 'retrograde': data['retrograde']}

        # Construct response
        response = {
            'user_name': user_name,
            'arudha_lagna': al_sign,
            'planets': al_houses,
            'metadata': {
                'ayanamsa': 'Lahiri',
                'calculation_time': datetime.utcnow().isoformat(),
                'input': data
            }
        }
        logging.info(f"Successfully calculated Arudha Lagna for {user_name}")
        return jsonify(response), 200

    except Exception as e:
        logging.error(f"Calculation error: {str(e)}")
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500


#  Bava Lagan
@app.route('/calculate_bhava_lagna', methods=['POST'])
def calculate_bhava_lagna_chart():
    try:
        # Parse and validate input
        data = request.get_json()
        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not data or not all(k in data for k in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        birth_date = data['birth_date']
        birth_time = data['birth_time']
        lat = float(data['latitude'])
        lon = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        # Calculate Julian Day
        birth_jd = get_julian_day(birth_date, birth_time, tz_offset)

        # Calculate sunrise and Sun’s position
        sunrise_jd, sunrise_sun_lon = calculate_sunrise(birth_jd, lat, lon, tz_offset)

        # Calculate Bhava Lagna
        bl_lon = calculate_bhava_lagna(birth_jd, sunrise_jd, sunrise_sun_lon)
        bl_sign, bl_degrees = get_sign_and_degrees(bl_lon)

        # Calculate planetary positions
        positions = {}
        for planet, pid in PLANET_IDS.items():
            if planet == 'Ketu':
                continue
            pos_data = swe.calc_ut(birth_jd, pid, swe.FLG_SIDEREAL | swe.FLG_SPEED)[0]
            lon = pos_data[0] % 360
            sign, degrees = get_sign_and_degrees(lon)
            retrograde = 'R' if pos_data[3] < 0 else ''
            house = calculate_house(sign, bl_sign)
            positions[planet] = {"degrees": round(degrees, 4), "sign": sign, "retrograde": retrograde, "house": house}

        # Calculate Ketu (opposite Rahu)
        rahu_lon = positions['Rahu']['degrees'] + (SIGNS.index(positions['Rahu']['sign']) * 30)
        ketu_lon = (rahu_lon + 180) % 360
        ketu_sign, ketu_degrees = get_sign_and_degrees(ketu_lon)
        positions['Ketu'] = {
            "degrees": round(ketu_degrees, 4), "sign": ketu_sign, "retrograde": "", 
            "house": calculate_house(ketu_sign, bl_sign)
        }

        # Response
        response = {
            "bhava_lagna": {"sign": bl_sign, "degrees": round(bl_degrees, 4)},
            "planets": positions
        }
        return jsonify(response), 200

    except Exception as e:
        logging.error(f"Error in calculation: {str(e)}")
        return jsonify({"error": str(e)}), 500



# *********************************************************************************************************
# ***********************************  Mobile services  Charts ********************************************
# *********************************************************************************************************


@app.route('/synastry', methods=['POST'])
def synastry():
    """
    API endpoint to calculate synastry data for two individuals.
    
    Method: POST
    Input: JSON object with person_a and person_b data containing date, time, lat, lon, tz_offset, and optional name.
    Output: JSON object containing synastry calculations and interpretations.
    """
    data = request.get_json()
    if not data or 'person_a' not in data or 'person_b' not in data:
        return jsonify({'error': 'Both person_a and person_b must be provided'}), 400

    valid_a, error_a = validate_person_data(data['person_a'], 'person_a')
    if not valid_a:
        return jsonify({'error': error_a}), 400
    valid_b, error_b = validate_person_data(data['person_b'], 'person_b')
    if not valid_b:
        return jsonify({'error': error_b}), 400

    try:
        # Calculate synastry chart using the function from calculations.py
        response = calculate_synastry(data)
        return jsonify(response), 200
    except Exception as e:
        logging.error(f"Error in synastry calculation: {str(e)}")
        return jsonify({'error': str(e)}), 400



@app.route('/composite', methods=['POST'])
def composite_chart():
    """
    API endpoint to calculate the composite chart for two individuals.
    
    Method: POST
    Input: JSON object with person_a and person_b data containing date, time, lat, lon, tz_offset, and optional name.
    Output: JSON object containing the composite chart data.
    """
    data = request.get_json()
    if not data or 'person_a' not in data or 'person_b' not in data:
        return jsonify({'error': 'Both person_a and person_b must be provided'}), 400

    valid_a, error_a = validate_person_data(data['person_a'], 'person_a')
    if not valid_a:
        return jsonify({'error': error_a}), 400
    valid_b, error_b = validate_person_data(data['person_b'], 'person_b')
    if not valid_b:
        return jsonify({'error': error_b}), 400

    try:
        # Calculate composite chart using the function from calculations.py
        response = calculate_composite_chart(data)
        return jsonify(response), 200
    except Exception as e:
        logging.error(f"Error in composite chart calculation: {str(e)}")
        return jsonify({'error': str(e)}), 400



@app.route('/progressed', methods=['POST'])
def progressed_chart():
    """
    API endpoint to calculate and return a sidereal progressed chart with interpretations.
    
    Method: POST
    Input: JSON object with birth_date, birth_time, latitude, longitude, tz_offset, age.
    Output: JSON object containing the progressed chart data.
    """
    data = request.get_json()
    
    # Validate input
    required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'tz_offset', 'age']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    try:
        # Calculate progressed chart using the function from calculations.py
        response = calculate_progressed_chart(data)
        return jsonify(response), 200
    except ValueError as e:
        return jsonify({'error': f'Invalid input data: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Calculation failed: {str(e)}'}), 500




@app.route('/numerology', methods=['POST'])
def numerology():
    """
    API endpoint to calculate numerology data for a business name and optional founding date.
    
    Method: POST
    Input: JSON object with 'name' and optional 'founding_date'.
    Output: JSON object containing numerology calculations and interpretations.
    """
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({"error": "Missing 'name' in JSON data"}), 400

        # Calculate numerology data using the function from calculations.py
        response = calculate_numerology(data)
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500



# *********************************************************************************************************
# ***********************************  Vimshottari Dashas ************************************************
# *********************************************************************************************************


#   Vimshottari Mahadasha and Antardashas
@app.route('/calculate_maha_antar_dasha', methods=['POST'])
def calculate_vimshottari_dasha():
    """
    Calculate Vimshottari Mahadasha and Antardashas based on birth details.
    
    Expected JSON Input:
    {
        "user_name": "Anusha kayakokula",
        "birth_date": "1998-10-15",
        "birth_time": "10:40:30",
        "latitude": "17.3850",
        "longitude": "78.4867",
        "timezone_offset": 5.5
    }
    
    Returns:
        JSON response with Mahadasha and Antardasha details.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        user_name = data.get('user_name', 'Unknown')
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        # Step 1: Convert birth date and time to Julian Day in UT
        jd_birth = get_julian_day(birth_date, birth_time, tz_offset)

        # Step 2: Calculate Moon's sidereal position with Lahiri Ayanamsa
        moon_longitude = calculate_moon_sidereal_position(jd_birth)

        # Step 3: Determine Nakshatra and ruling planet
        nakshatra, lord, nakshatra_start = get_nakshatra_and_lord(moon_longitude)
        if not nakshatra:
            return jsonify({"error": "Unable to determine Nakshatra"}), 500

        # Step 4: Calculate remaining Mahadasha time and elapsed time
        remaining_time, mahadasha_duration, elapsed_time = calculate_dasha_balance(moon_longitude, nakshatra_start, lord)

        # Step 5: Calculate Mahadasha periods with Antardashas
        mahadasha_periods = calculate_mahadasha_periods(birth_date, remaining_time, lord, elapsed_time)

        # Step 6: Construct response
        response = {
            "user_name": user_name,
            "nakshatra_at_birth": nakshatra,
            "moon_longitude": round(moon_longitude, 4),
            "mahadashas": mahadasha_periods
        }
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input format: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500


#   Vimshottari Antardasha and Pratyantardashas
@app.route('/calculate_antar_prathythar_dasha', methods=['POST'])
def calculate_vimshottari_Pratyantardashas():
    """
    Calculate Vimshottari Mahadasha, Antardashas, and Pratyantardashas based on birth details.
    
    Expected JSON Input:
    {
        "user_name": "Anusha kayakokula",
        "birth_date": "1998-10-15",
        "birth_time": "10:40:30",
        "latitude": "17.3850",
        "longitude": "78.4867",
        "timezone_offset": 5.5
    }
    
    Returns:
        JSON response with Mahadasha, Antardasha, and Pratyantardasha details.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        user_name = data.get('user_name', 'Unknown')
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        # Step 1: Convert birth date and time to Julian Day in UT
        jd_birth = get_julian_day(birth_date, birth_time, tz_offset)

        # Step 2: Calculate Moon's sidereal position with Lahiri Ayanamsa
        moon_longitude = calculate_moon_sidereal_position(jd_birth)

        # Step 3: Determine Nakshatra and ruling planet
        nakshatra, lord, nakshatra_start = get_nakshatra_and_lord(moon_longitude)
        if not nakshatra:
            return jsonify({"error": "Unable to determine Nakshatra"}), 500

        # Step 4: Calculate remaining Mahadasha time and elapsed time
        remaining_time, mahadasha_duration, elapsed_time = calculate_dasha_balance(moon_longitude, nakshatra_start, lord)

        # Step 5: Calculate Mahadasha periods with Antardashas and Pratyantardashas
        mahadasha_periods = calculate_mahadasha_periods(birth_date, remaining_time, lord, elapsed_time)

        # Step 6: Construct response
        response = {
            "user_name": user_name,
            "nakshatra_at_birth": nakshatra,
            "moon_longitude": round(moon_longitude, 4),
            "mahadashas": mahadasha_periods
        }
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input format: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500


#   Vimshottari Pratyantardasha and Sookshma Dasha
@app.route('/calculate_vimshottari_Sookshama', methods=['POST'])
def calculate_vimshottari_Sookshama():
    """
    Calculate Vimshottari Dasha periods including Sookshma Dashas.
    
    Expected JSON Input:
    {
        "user_name": "Anusha kayakokula",
        "birth_date": "1998-10-15",
        "birth_time": "10:40:30",
        "latitude": "17.3850",
        "longitude": "78.4867",
        "timezone_offset": 5.5
    }
    
    Returns:
        JSON response with Mahadasha, Antardasha, Pratyantardasha, and Sookshma Dasha details.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        user_name = data.get('user_name', 'Unknown')
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        jd_birth = get_julian_day(birth_date, birth_time, tz_offset)
        moon_longitude = calculate_moon_sidereal_position(jd_birth)
        nakshatra, lord, nakshatra_start = get_nakshatra_and_lord(moon_longitude)
        if not nakshatra:
            return jsonify({"error": "Unable to determine Nakshatra"}), 500

        remaining_time, mahadasha_duration, elapsed_time = calculate_dasha_balance(moon_longitude, nakshatra_start, lord)
        mahadasha_periods = calculate_mahadasha_periods(birth_date, remaining_time, lord, elapsed_time)

        response = {
            "user_name": user_name,
            "nakshatra_at_birth": nakshatra,
            "moon_longitude": round(moon_longitude, 4),
            "mahadashas": mahadasha_periods
        }
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input format: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500


# *********************************************************************************************************
# *********************************** Astakavarghas ************************************************
# *********************************************************************************************************


#  Binnastakavargha 
@app.route('/calculate_binnashtakavarga', methods=['POST'])
def ashtakavarga_api_calculate_ashtakavarga():
    """Calculate Ashtakavarga chart from birth details and return JSON with Ascendant details."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        user_name = data.get('user_name', 'Unknown')
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        # Calculate Julian Day
        jd = astro_utils_get_julian_day(birth_date, birth_time, tz_offset)

        # Calculate sidereal Ascendant and its sign
        asc_lon = astro_utils_calculate_ascendant(jd, latitude, longitude)
        asc_sign_index = astro_utils_get_sign_index(asc_lon)
        asc_sign = ZODIAC_SIGNS[asc_sign_index]

        # Calculate planetary positions
        positions = astro_utils_calculate_planet_positions(jd)
        positions['Ascendant'] = {'longitude': asc_lon, 'sign_index': asc_sign_index}

        # Calculate Bhinnashtakavarga
        bhinnashtakavarga = astro_utils_calculate_bhinnashtakavarga(positions)
        astro_utils_validate_totals(bhinnashtakavarga)

        # Format output
        bhinnashtakavarga_output = {
            target: {
                "signs": {ZODIAC_SIGNS[i]: bindus[i] for i in range(12)},
                "total_bindus": sum(bindus)
            } for target, bindus in bhinnashtakavarga.items()
        }

        # Format Ascendant degrees within the sign
        asc_degrees = astro_utils_format_dms(asc_lon % 30)

        # Construct response
        response = {
            'user_name': user_name,
            'ascendant': {
                'degrees': asc_degrees,
                'sign': asc_sign
            },
            'bhinnashtakavarga': bhinnashtakavarga_output,
            'metadata': {
                'ayanamsa': 'Lahiri',
                'calculation_time': datetime.utcnow().isoformat(),
                'input': data
            }
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500



# Sarvathkavargha 


@app.route('/calculate_sarvashtakavarga', methods=['POST'])
def sarvashtakavarga_api_calculate_sarvashtakavarga():
    """Calculate Sarvashtakavarga from birth details."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        user_name = data.get('user_name', 'Unknown')
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        # Calculate Julian Day
        jd = astro_utils_get_julian_day(birth_date, birth_time, tz_offset)

        # Calculate sidereal Ascendant and its sign index
        asc_lon = astro_utils_calculate_ascendant(jd, latitude, longitude)
        asc_sign_index = astro_utils_get_sign_index(asc_lon)

        # Calculate positions of planets and ascendant
        positions = astro_utils_calculate_positions(jd, asc_lon)

        # Calculate Bhinnashtakavarga
        bhinnashtakavarga = astro_utils_calculate_bhinnashtakavarga(positions)

        # Calculate Sarvashtakavarga
        sarvashtakavarga = astro_utils_calculate_sarvashtakavarga(bhinnashtakavarga)

        # Map Sarvashtakavarga to houses
        house_bindus = astro_utils_map_to_houses(sarvashtakavarga, asc_sign_index)

        # Prepare response
        response = {
            'user_name': user_name,
            'sarvashtakavarga': {
                'signs': {SIGNS[i]: sarvashtakavarga[i] for i in range(12)},
                'houses': house_bindus,
                'total_bindus': sum(sarvashtakavarga)
            },
            'metadata': {
                'ayanamsa': 'Lahiri',
                'calculation_time': datetime.utcnow().isoformat(),
                'input': data
            }
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500



if __name__ == "__main__":
    app.run(debug=True)
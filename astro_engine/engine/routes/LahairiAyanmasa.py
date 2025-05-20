from flask import Blueprint, request, jsonify
from datetime import datetime
import logging
from venv import logger


from astro_engine.engine.dashas.AntarDasha import calculate_dasha_antar_balance, calculate_mahadasha_periods, calculate_moon_sidereal_antar_position, get_julian_dasha_day, get_nakshatra_and_antar_lord
from astro_engine.engine.dashas.Pratyantardashas import calculate_Pratythardasha_periods, calculate_moon_praty_sidereal_position, calculate_pratythar_dasha_balance, get_julian_pratyathar_day, get_nakshatra_party_and_lord
from astro_engine.engine.dashas.Sookashama import calculate_moon_sookshma_sidereal_position, calculate_sookshma_dasha_balance, calculate_sookshma_dasha_periods, get_julian_sookshma_day, get_nakshatra_and_lord_sookshma
from astro_engine.engine.divisionalCharts.ChathruthamshaD4 import  get_julian_day, lahairi_Chaturthamsha
from astro_engine.engine.divisionalCharts.ChaturvimshamshaD24 import  lahairi_Chaturvimshamsha
from astro_engine.engine.divisionalCharts.DashamshaD10 import  lahairi_Dashamsha
from astro_engine.engine.divisionalCharts.DreshkanaD3 import PLANET_NAMES, lahairi_drerkhana
from astro_engine.engine.divisionalCharts.DwadashamshaD12 import  lahairi_Dwadashamsha
from astro_engine.engine.divisionalCharts.HoraD2 import lahairi_hora_chart   
from astro_engine.engine.divisionalCharts.KvedamshaD40 import  lahairi_Khavedamsha
from astro_engine.engine.divisionalCharts.NavamshaD9 import  lahairi_navamsha_chart
from astro_engine.engine.divisionalCharts.SaptamshaD7 import  lahairi_saptamsha
from astro_engine.engine.divisionalCharts.ShodasmasD16 import  lahairi_Shodashamsha

from astro_engine.engine.lagnaCharts.ArudhaLagna import lahairi_arudha_lagna
from astro_engine.engine.lagnaCharts.BavaLagna import  lahairi_bava_lagan
from astro_engine.engine.lagnaCharts.EqualLagan import SIGNS,  lahairi_equal_bava
from astro_engine.engine.lagnaCharts.KPLagna import  lahairi_kp_bava
from astro_engine.engine.lagnaCharts.Sripathi import lahairi_sripathi_bava
from astro_engine.engine.natalCharts.natal import lahairi_natal,  longitude_to_sign,     format_dms
from astro_engine.engine.natalCharts.transit import  lahairi_tranist
from astro_engine.engine.numerology.CompositeChart import  lahairi_composite
from astro_engine.engine.numerology.LoShuGridNumerology import calculate_lo_shu_grid
from astro_engine.engine.ashatakavargha.Binnastakavargha import  raman_bhinnashtakavarga
from astro_engine.engine.numerology.NumerologyData import calculate_chaldean_numbers, calculate_date_numerology, get_sun_sign, get_element_from_number, get_sun_sign_element, get_elemental_compatibility, personal_interpretations, business_interpretations, ruling_planets, planet_insights, sun_sign_insights, number_colors, number_gemstones, planet_days
from astro_engine.engine.divisionalCharts.AkshavedamshaD45 import  lahairi_Akshavedamsha
from astro_engine.engine.divisionalCharts.ShashtiamshaD60 import  lahairi_Shashtiamsha
from astro_engine.engine.divisionalCharts.VimshamshaD20 import  lahairi_Vimshamsha
from astro_engine.engine.natalCharts.SudharashanaChakara import calculate_sidereal_positions, generate_chart, get_sign
from astro_engine.engine.natalCharts.SunChart import  lahrir_sun_chart,  validate_input_sun
from astro_engine.engine.natalCharts.MoonChart import  lahairi_moon_chart, validate_input
from astro_engine.engine.numerology.ProgressChart import  lahairi_progress
from astro_engine.engine.numerology.SynatryChart import analyze_house_overlays, calculate_aspects,  evaluate_nodal_connections, interpret_synastry, lahairi_synastry, validate_person_data


bp = Blueprint('bp_routes', __name__)

# Natal Chart
@bp.route('/lahairi/natal', methods=['POST'])
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
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            return jsonify({"error": "Invalid latitude or longitude"}), 400

        # Calculate chart data
        chart_data = lahairi_natal(birth_data)

        # Format planetary positions
        planetary_positions_json = {}
        for planet, data in chart_data['planet_positions'].items():
            sign, sign_deg = longitude_to_sign(data['lon'])
            dms = format_dms(sign_deg)
            house = chart_data['planet_houses'][planet]
            planetary_positions_json[planet] = {
                "sign": sign,
                "degrees": dms,
                "retrograde": data['retro'],
                "house": house,
                "nakshatra": data['nakshatra'],
                "pada": data['pada']
            }

        # Format ascendant
        asc_sign, asc_deg = longitude_to_sign(chart_data['ascendant']['lon'])
        asc_dms = format_dms(asc_deg)
        ascendant_json = {
            "sign": asc_sign,
            "degrees": asc_dms,
            "nakshatra": chart_data['ascendant']['nakshatra'],
            "pada": chart_data['ascendant']['pada']
        }

        # Format house signs
        house_signs_json = {f"House {i+1}": {"sign": house["sign"], "start_longitude": format_dms(house["start_longitude"])}
                           for i, house in enumerate(chart_data['house_signs'])}

        # Construct response
        response = {
            "user_name": birth_data['user_name'],
            "birth_details": {
                "birth_date": birth_data['birth_date'],
                "birth_time": birth_data['birth_time'],
                "latitude": latitude,
                "longitude": longitude,
                "timezone_offset": float(birth_data['timezone_offset'])
            },
            "planetary_positions": planetary_positions_json,
            "ascendant": ascendant_json,
            "house_signs": house_signs_json,
            "notes": {
                "ayanamsa": "Lahiri",
                "ayanamsa_value": f"{chart_data['ayanamsa_value']:.6f}",
                "chart_type": "Rasi",
                "house_system": "Whole Sign"
            }
        }
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500



# Transit or Gochar Chart
@bp.route('/lahairi/transit', methods=['POST'])
def transit_chart():
    try:
        # Get JSON data from request
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Required fields for natal calculations
        required = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        # Call the calculation function
        response = lahairi_tranist(data)
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500



# Sun Chart

@bp.route('/lahairi/calculate_sun_chart', methods=['POST'])
def calculate_sun_chart():
    """
    API endpoint to calculate Sun Chart (sidereal) with Whole Sign house system.
    """
    try:
        # Parse and validate input
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        validate_input_sun(data)
        
        # Call the calculation function
        response = lahrir_sun_chart(data)
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation failed: {str(e)}"}), 500



# Moon Chart

@bp.route('/lahairi/calculate_moon_chart', methods=['POST'])
def calculate_moon_chart():
    """
    API endpoint to calculate Moon Chart (sidereal) with Whole Sign house system.
    """
    try:
        # Parse and validate input
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        validate_input(data)
        
        # Call the calculation function
        response = lahairi_moon_chart(data)
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation failed: {str(e)}"}), 500



# Sudarshan Chakra
@bp.route('/calculate_sudarshan_chakra', methods=['POST'])
def calculate_sudarshan_chakra():
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
        positions = calculate_sidereal_positions(jd_birth, latitude, longitude)
        asc_sign, _ = get_sign(positions["Ascendant"])
        moon_sign, _ = get_sign(positions["Moon"])
        sun_sign, _ = get_sign(positions["Sun"])
        asc_sign_idx = SIGNS.index(asc_sign)
        moon_sign_idx = SIGNS.index(moon_sign)
        sun_sign_idx = SIGNS.index(sun_sign)
        lagna_chart = generate_chart(positions, asc_sign_idx)
        chandra_chart = generate_chart(positions, moon_sign_idx)
        surya_chart = generate_chart(positions, sun_sign_idx)

        response = {
            "user_name": user_name,
            "sudarshan_chakra": {"lagna_chart": lagna_chart, "chandra_chart": chandra_chart, "surya_chart": surya_chart}
        }
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input format: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500



# Hora (D-2)

@bp.route('/lahairi/calculate_d2_hora', methods=['POST'])
def calculate_d2_hora():
    """API endpoint to calculate the D2 Hora chart."""
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

        # Call the calculation function
        result = lahairi_hora_chart(birth_date, birth_time, latitude, longitude, tz_offset)
        response = {
            'user_name': user_name,
            'd2_hora_chart': result,
            'metadata': {
                'ayanamsa': 'Lahiri',
                'house_system': 'Whole Sign',
                'calculation_time': datetime.utcnow().isoformat(),
                'input': data
            }
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500


# Dreshkana (D-3)

@bp.route('/lahairi/calculate_d3', methods=['POST'])
def calculate_d3_chart_endpoint():
    """API endpoint to calculate D3 chart with retrograde status, nakshatras, and padas."""
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

        d3_data = lahairi_drerkhana(birth_date, birth_time, latitude, longitude, tz_offset)
        return jsonify(d3_data), 200

    except Exception as e:
        logger.error(f"Error in D3 chart calculation: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500



# Chaturthamsha (D-4)
@bp.route('/lahairi/calculate_d4', methods=['POST'])
def calculate_d4():
    """API endpoint to calculate the Chaturthamsha (D4) chart."""
    try:
        # Get JSON data
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Validate required fields
        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        # Call the calculation function
        response = lahairi_Chaturthamsha(data)
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500




# Saptamsha (D-7)
@bp.route('/lahairi/calculate_d7_chart', methods=['POST'])
def calculate_d7_chart_endpoint():
    """API endpoint to calculate D7 chart from birth details."""
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

        # Calculate D7 chart using lahairi_saptamsha
        d7_data = lahairi_saptamsha(birth_date, birth_time, latitude, longitude, tz_offset)

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

@bp.route('/lahairi/calculate_d10', methods=['POST'])
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
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
    if not all(key in data for key in required):
        return jsonify({"error": "Missing required parameters"}), 400

    response = lahairi_Dashamsha(data)
    return jsonify(response)



# Dwadashamsha (D-12)
@bp.route('/lahairi/calculate_d12', methods=['POST'])
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
    - D12 ascendant, planetary positions with retrograde, nakshatras, padas, house signs, and metadata
    """
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
        timezone_offset = float(data['timezone_offset'])

        # Call the calculation function
        response = lahairi_Dwadashamsha(birth_date, birth_time, latitude, longitude, timezone_offset)
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


# Shodashamsha (D-16)

@bp.route('/lahairi/calculate_d16', methods=['POST'])
def calculate_d16():
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
        enforce_opposition = data.get('enforce_opposition', False)

        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180) or not (-12 <= tz_offset <= 14):
            return jsonify({"error": "Invalid geographic or timezone data"}), 400

        # Call the calculation function
        response = lahairi_Shodashamsha(birth_date, birth_time, latitude, longitude, tz_offset, enforce_opposition)
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500



# Vimshamsha (D-20)
@bp.route('/lahairi/calculate_d20', methods=['POST'])
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

        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])
        user_name = data.get('user_name', 'Unknown')

        # Call the calculation function
        response = lahairi_Vimshamsha(birth_date, birth_time, latitude, longitude, tz_offset, user_name)
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input format: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500




# Chaturvimshamsha (D-24)

@bp.route('/lahairi/calculate_d24', methods=['POST'])
def calculate_d24():
    """API endpoint to calculate D24 chart."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        birth_date = data['birth_date']  # e.g., '1990-01-01'
        birth_time = data['birth_time']  # e.g., '12:00:00'
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])  # e.g., 5.5 for IST

        # Call the calculation function
        response = lahairi_Chaturvimshamsha(birth_date, birth_time, latitude, longitude, tz_offset)
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500



# Saptavimshamsha (D-27)
# @bp.route('/calculate_d27', methods=['POST'])
# def calculate_d27_chart():
#     try:
#         data = request.get_json()
#         if not data:
#             return jsonify({"error": "No JSON data provided"}), 400

#         required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
#         if not all(field in data for field in required_fields):
#             return jsonify({"error": "Missing required fields"}), 400

#         user_name = data.get('user_name', 'Unknown')
#         birth_date = data['birth_date']
#         birth_time = data['birth_time']
#         latitude = float(data['latitude'])
#         longitude = float(data['longitude'])
#         tz_offset = float(data['timezone_offset'])

#         jd = get_julian_day(birth_date, birth_time, tz_offset)
#         d1_positions = calculate_d1_positions(jd, latitude, longitude)
#         d27_positions = calculate_d27_positions(d1_positions)
#         d27_asc_sign = d27_positions['Ascendant']
#         d27_houses = calculate_d27_houses(d27_asc_sign, d27_positions)

#         response = {
#             "user_name": user_name,
#             "d27_chart": {"positions": {planet: SIGN_NAMES[sign - 1] for planet, sign in d27_positions.items()}, "houses": d27_houses}
#         }
#         return jsonify(response), 200

#     except ValueError as ve:
#         return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
#     except Exception as e:
#         return jsonify({"error": f"Calculation error: {str(e)}"}), 500




# Khavedamsha (D-40)
@bp.route('/lahairi/calculate_d40', methods=['POST'])
def calculate_d40():
    """API endpoint to calculate the D40 chart."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Extract input data
        birth_date = data['birth_date']  # e.g., '1990-01-01'
        birth_time = data['birth_time']  # e.g., '12:00:00'
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])  # e.g., 5.5 for IST

        # Call the calculation function
        response = lahairi_Khavedamsha(birth_date, birth_time, latitude, longitude, tz_offset)
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500





# Akshavedamsha (D-45)
@bp.route('/lahairi/calculate_d45', methods=['POST'])
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
        user_name = data.get('user_name', 'Unknown')

        # Call the calculation function
        response = lahairi_Akshavedamsha(birth_date, birth_time, latitude, longitude, tz_offset, user_name)
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input format: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


# Shashtiamsha (D-60)

@bp.route('/lahairi/calculate_d60', methods=['POST'])
def calculate_d60():
    """API endpoint to calculate the D60 chart."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required fields"}), 400

        # Extract input data
        user_name = data['user_name']
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        # Calculate D60 chart using lahairi_Shashtiamsha
        response = lahairi_Shashtiamsha(birth_date, birth_time, latitude, longitude, tz_offset, user_name)
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Navamsa Chart D9
@bp.route('/lahairi/navamsa', methods=['POST'])
def navamsa_chart():
    """API endpoint to calculate Navamsa (D9) chart with retrograde, nakshatras, and padas."""
    try:
        # Get JSON data from request
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Check for required parameters
        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        # Call the calculation function
        response = lahairi_navamsha_chart(data)
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500




# Sripathi Bhava
@bp.route('/lahairi/calculate_sripathi_bhava', methods=['POST'])
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

        # Call the calculation function
        response = lahairi_sripathi_bava(birth_date, birth_time, latitude, longitude, tz_offset)
        logger.debug(f"Output JSON: {response}")
        return jsonify(response), 200

    except ValueError as ve:
        logger.error(f"Invalid input format: {str(ve)}")
        return jsonify({"error": f"Invalid input format: {str(ve)}"}), 400
    except Exception as e:
        logger.error(f"Calculation error: {str(e)}")
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500




# KP Bhava
@bp.route('/lahairi/calculate_kp_bhava', methods=['POST'])
def calculate_kp_bhava():
    """API endpoint to calculate KP Bhava chart."""
    data = request.get_json()
    try:
        # Extract and validate input
        user_name = data['user_name']
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        # Call the calculation function
        result = lahairi_kp_bava(birth_date, birth_time, latitude, longitude, tz_offset, user_name)
        return jsonify(result), 200

    except KeyError as e:
        return jsonify({"error": f"Missing input field: {str(e)}"}), 400
    except ValueError as e:
        return jsonify({"error": f"Invalid input value: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation failed: {str(e)}"}), 500




# Equal Bhava Lagna
# @bp.route('/calculate_equal_bhava_lagna', methods=['POST'])
# def bava_calculate_endpoint():
#     try:
#         data = request.get_json()
#         if not data:
#             return jsonify({"error": "No JSON data provided"}), 400

#         required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
#         if not all(key in data for key in required_fields):
#             return jsonify({"error": "Missing required parameters"}), 400

#         user_name = data.get('user_name', 'Unknown')
#         birth_date = data['birth_date']
#         birth_time = data['birth_time']
#         latitude = float(data['latitude'])
#         longitude = float(data['longitude'])
#         tz_offset = float(data['timezone_offset'])

#         jd = bava_get_julian_day(birth_date, birth_time, tz_offset)
#         ascendant = bava_calculate_ascendant(jd, latitude, longitude)
#         ascendant_sign_index = int(ascendant // 30)
#         planetary_positions = bava_get_planet_positions(jd)
#         cusps_degrees = bava_calculate_equal_bhava_cusps(ascendant)
#         cusps_formatted = [bava_format_dms(cusp) for cusp in cusps_degrees]
#         house_data = [
#             {"house": i + 1, "cusp": cusps_formatted[i], "sign": SIGNS[int(cusps_degrees[i] // 30)]}
#             for i in range(12)
#         ]
#         house_assignments = bava_assign_planets_to_houses(planetary_positions, ascendant_sign_index)
#         planetary_data = [
#             {"planet": planet, "longitude": bava_format_dms(longitude), "sign": SIGNS[int(longitude // 30)], "retrograde": retrograde, "house": house_assignments[planet]}
#             for planet, (longitude, retrograde) in planetary_positions.items()
#         ]

#         response = {
#             "user_name": user_name,
#             "ascendant": {"longitude": bava_format_dms(ascendant), "sign": SIGNS[ascendant_sign_index]},
#             "planetary_positions": planetary_data,
#             "house_cusps": house_data,
#             "metadata": {"ayanamsa": "Lahiri", "house_system": "Equal Bhava (Whole Sign based)", "calculation_time": datetime.utcnow().isoformat(), "input": data}
#         }
#         return jsonify(response), 200

#     except ValueError as ve:
#         return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
#     except Exception as e:
#         return jsonify({"error": f"Calculation failed: {str(e)}"}), 500



@bp.route('/lahairi/calculate_equal_bhava_lagna', methods=['POST'])
def calculate_equal_bhava_lagna():
    """API endpoint to calculate Equal Bhava Lagna, house cusps, and planetary positions."""
    try:
        # Parse and validate JSON input
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required_fields):
            return jsonify({"error": "Missing required parameters"}), 400

        # Extract input data
        user_name = data.get('user_name', 'Unknown')
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        # Call the calculation function
        response = lahairi_equal_bava(birth_date, birth_time, latitude, longitude, tz_offset)
        response["user_name"] = user_name
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation failed: {str(e)}"}), 500

# Bhava Lagna
@bp.route('/lahairi/calculate_bhava_lagna', methods=['POST'])
def calculate_bhava_lagna():
    try:
        data = request.get_json()
        user_name = data['user_name']
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        timezone_offset = float(data['timezone_offset'])

        response = lahairi_bava_lagan(birth_date, birth_time, latitude, longitude, timezone_offset)
        response["user_name"] = user_name
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"Calculation failed: {str(e)}"}), 500



# Arudha lagna

@bp.route('/lahairi/calculate_arudha_lagna', methods=['POST'])
def calculate_arudha_lagna():
    """API endpoint to calculate Arudha Lagna chart with retrograde, nakshatras, and padas."""
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

        # Call the calculation function
        result = lahairi_arudha_lagna(birth_date, birth_time, latitude, longitude, tz_offset)
        response = {
            'user_name': user_name,
            'arudha_lagna': result['arudha_lagna'],
            'planets': result['planets'],
            'metadata': {
                'ayanamsa': 'Lahiri',
                'calculation_time': datetime.utcnow().isoformat(),
                'input': data
            }
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500




# Synastry

@bp.route('/lahairi/synastry', methods=['POST'])
def synastry():
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
        # Calculate chart data for both persons
        chart_a = lahairi_synastry(data['person_a'])
        chart_b = lahairi_synastry(data['person_b'])

        # Prepare positions with ascendant for aspects
        pos_a_with_asc = {**chart_a['positions'], 'Ascendant': chart_a['ascendant']}
        pos_b_with_asc = {**chart_b['positions'], 'Ascendant': chart_b['ascendant']}

        # Synastry analysis
        aspects = calculate_aspects(pos_a_with_asc, pos_b_with_asc)
        overlays_a_in_b = analyze_house_overlays(chart_a['positions'], chart_b['asc_sign_idx'])
        overlays_b_in_a = analyze_house_overlays(chart_b['positions'], chart_a['asc_sign_idx'])
        nodal_a = evaluate_nodal_connections(chart_a['positions'], chart_b['positions'])
        nodal_b = evaluate_nodal_connections(chart_b['positions'], chart_a['positions'])
        interpretation = interpret_synastry(aspects, overlays_a_in_b, overlays_b_in_a, nodal_a, nodal_b)

        # Response
        response = {
            'person_a': {
                'name': chart_a['name'],
                'birth_details': data['person_a'],
                'ascendant': {
                    'sign': chart_a['ascendant']['sign'],
                    'degree': chart_a['ascendant']['degree']
                },
                'planets': {k: {**v, 'house': chart_a['houses'][k]} for k, v in chart_a['positions'].items()}
            },
            'person_b': {
                'name': chart_b['name'],
                'birth_details': data['person_b'],
                'ascendant': {
                    'sign': chart_b['ascendant']['sign'],
                    'degree': chart_b['ascendant']['degree']
                },
                'planets': {k: {**v, 'house': chart_b['houses'][k]} for k, v in chart_b['positions'].items()}
            },
            'synastry': {
                'aspects': aspects,
                'house_overlays': {'a_in_b': overlays_a_in_b, 'b_in_a': overlays_b_in_a},
                'nodal_connections': {'person_a': nodal_a, 'person_b': nodal_b},
                'interpretation': interpretation
            }
        }
        return jsonify(response), 200
    except Exception as e:
        logging.error(f"Error in synastry calculation: {str(e)}")
        return jsonify({'error': str(e)}), 400







# Composite Chart

@bp.route('/lahairi/composite', methods=['POST'])
def composite_chart():
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
        # Extract names
        name_a = data['person_a'].get('name', 'Person A')
        name_b = data['person_b'].get('name', 'Person B')

        # Calculate composite chart
        result = lahairi_composite(data['person_a'], data['person_b'])

        # Construct response
        response = {
            'person_a': {
                'name': name_a,
                'natal': result['natal_a']
            },
            'person_b': {
                'name': name_b,
                'natal': result['natal_b']
            },
            'composite': result['composite']
        }
        return jsonify(response), 200
    except Exception as e:
        logging.error(f"Error in composite chart calculation: {str(e)}")
        return jsonify({'error': str(e)}), 400




# Progressed Chart

@bp.route('/lahairi/progressed', methods=['POST'])
def progressed_chart():
    """API endpoint to calculate the progressed chart."""
    data = request.get_json()
    
    # Validate input
    required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset', 'age']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    try:
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        timezone_offset = float(data['timezone_offset'])
        age = float(data['age'])
        
        # Calculate progressed chart data using lahairi_composite
        result = lahairi_progress(birth_date, birth_time, latitude, longitude, timezone_offset, age)
        
        # Construct response
        response = {
            'progressed_planets': result['prog_positions'],
            'progressed_ascendant': result['prog_asc'],
            'progressed_midheaven': result['prog_mc'],
            'house_cusps': result['house_cusps'],
            'interpretations': result['interpretations']
        }
        return jsonify(response), 200
    
    except ValueError as e:
        return jsonify({'error': f'Invalid input data: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Calculation failed: {str(e)}'}), 500





# Chaldean Numerology
@bp.route('/lahairi/chaldean_numerology', methods=['POST'])
def numerology():
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({"error": "Missing 'name' in JSON data"}), 400
        name = data['name']
        if not isinstance(name, str):
            return jsonify({"error": "'name' must be a string"}), 400

        numbers = calculate_chaldean_numbers(name)
        compound_number = numbers['compound_number']
        root_number = numbers['root_number']
        element = get_element_from_number(root_number)
        personal_interpretation = personal_interpretations.get(root_number, "No interpretation available.")
        ruling_planet = ruling_planets.get(root_number, "Unknown")
        insight = planet_insights.get(ruling_planet, {"positive": "N/A", "challenge": "N/A", "business_tip": "N/A"})
        colors = number_colors.get(root_number, [])
        gemstone = number_gemstones.get(root_number, "N/A")
        day = planet_days.get(ruling_planet, "N/A")

        response = {
            "original_name": name,
            "compound_number": compound_number,
            "root_number": root_number,
            "element": element,
            "ruling_planet": ruling_planet,
            "personal_interpretation": personal_interpretation,
            "astrological_insight": {"positive": insight["positive"], "challenge": insight["challenge"]},
            "recommendations": {"colors": colors, "gemstone": gemstone, "auspicious_day": day}
        }

        if 'tagline' in data and isinstance(data['tagline'], str):
            tagline = data['tagline']
            tagline_numbers = calculate_chaldean_numbers(tagline)
            tagline_compound = tagline_numbers['compound_number']
            tagline_root = tagline_numbers['root_number']
            tagline_element = get_element_from_number(tagline_root)
            business_interpretation = business_interpretations.get(tagline_root, "No interpretation available.")
            tagline_planet = ruling_planets.get(tagline_root, "Unknown")
            tagline_insight = planet_insights.get(tagline_planet, {"positive": "N/A", "challenge": "N/A", "business_tip": "N/A"})
            compatibility = get_elemental_compatibility(element, tagline_element)
            response["business_tagline"] = {
                "original": tagline,
                "compound_number": tagline_compound,
                "root_number": tagline_root,
                "element": tagline_element,
                "ruling_planet": tagline_planet,
                "business_interpretation": business_interpretation,
                "astrological_insight": {"positive": tagline_insight["positive"], "challenge": tagline_insight["challenge"], "business_tip": tagline_insight["business_tip"]},
                "compatibility_with_personal": f"Personal ({element}) vs. Business ({tagline_element}): {compatibility}",
                "recommendations": {"colors": number_colors.get(tagline_root, []), "gemstone": number_gemstones.get(tagline_root, "N/A"), "auspicious_day": planet_days.get(tagline_planet, "N/A")}
            }

        if 'founding_date' in data:
            founding_date = data['founding_date']
            date_numerology = calculate_date_numerology(founding_date)
            sun_sign = get_sun_sign(founding_date)
            if date_numerology is not None and sun_sign is not None:
                date_element = get_element_from_number(date_numerology)
                sun_sign_element = get_sun_sign_element(sun_sign)
                numerology_compatibility = get_elemental_compatibility(response["business_tagline"]["element"] if 'business_tagline' in response else element, date_element)
                sun_sign_influence = f"Sun in {sun_sign} ({sun_sign_element}): {sun_sign_insights.get(sun_sign, 'N/A')}"
                response["founding_date"] = {
                    "date": founding_date,
                    "numerology": date_numerology,
                    "element": date_element,
                    "sun_sign": sun_sign,
                    "sun_sign_element": sun_sign_element,
                    "compatibility": f"Founding ({date_element}) vs. Reference ({response['business_tagline']['element'] if 'business_tagline' in response else element}): {numerology_compatibility}",
                    "sun_sign_influence": sun_sign_influence
                }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Lo Shu Grid Numerology
@bp.route('/lahairi/lo_shu_grid_numerology', methods=['POST'])
def lo_shu():
    data = request.get_json()
    birth_date = data.get('birth_date')
    gender = data.get('gender')
    
    if not birth_date or not gender:
        return jsonify({"error": "Missing birth_date or gender"}), 400
    
    if gender.lower() not in ["male", "female"]:
        return jsonify({"error": "Gender must be 'male' or 'female'"}), 400
    
    result = calculate_lo_shu_grid(birth_date, gender)
    
    if "error" in result:
        return jsonify(result), 400
    
    return jsonify(result)

# Vimshottari Mahadasha and Antardashas


@bp.route('/lahairi/calculate_antar_dasha', methods=['POST'])
def calculate_vimshottari_antar_dasha():
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
        jd_birth = get_julian_dasha_day(birth_date, birth_time, tz_offset)

        # Step 2: Calculate Moon's sidereal position with Lahiri Ayanamsa
        moon_longitude = calculate_moon_sidereal_antar_position(jd_birth)

        # Step 3: Determine Nakshatra and ruling planet
        nakshatra, lord, nakshatra_start = get_nakshatra_and_antar_lord(moon_longitude)
        if not nakshatra:
            return jsonify({"error": "Unable to determine Nakshatra"}), 500

        # Step 4: Calculate remaining Mahadasha time and elapsed time
        remaining_time, mahadasha_duration, elapsed_time = calculate_dasha_antar_balance(moon_longitude, nakshatra_start, lord)

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




# # Vimshottari Antardasha and Pratyantardashas
@bp.route('/lahairi/calculate_maha_antar_pratyantar_dasha', methods=['POST'])
def calculate_vimshottari_pratyantar_dasha():
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

        jd_birth = get_julian_pratyathar_day(birth_date, birth_time, tz_offset)
        moon_longitude = calculate_moon_praty_sidereal_position(jd_birth)
        nakshatra, lord, nakshatra_start = get_nakshatra_party_and_lord(moon_longitude)
        if not nakshatra:
            return jsonify({"error": "Unable to determine Nakshatra"}), 500

        remaining_time, mahadasha_duration, elapsed_time = calculate_pratythar_dasha_balance(moon_longitude, nakshatra_start, lord)
        mahadasha_periods = calculate_Pratythardasha_periods(jd_birth, remaining_time, lord, elapsed_time)

        response = {
            "user_name": user_name,
            "nakshatra_at_birth": nakshatra,
            "moon_longitude": moon_longitude,
            "mahadashas": mahadasha_periods
        }
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input format: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500




# # Vimshottari Pratyantardasha and Sookshma Dasha


@bp.route('/lahairi/calculate_antar_pratyantar_sookshma_dasha', methods=['POST'])
def calculate_vimshottari_sookshma_dasha():
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

        jd_birth = get_julian_sookshma_day(birth_date, birth_time, tz_offset)
        moon_longitude = calculate_moon_sookshma_sidereal_position(jd_birth)
        nakshatra, lord, nakshatra_start = get_nakshatra_and_lord_sookshma(moon_longitude)
        if not nakshatra:
            return jsonify({"error": "Unable to determine Nakshatra"}), 500

        remaining_time, mahadasha_duration, elapsed_time = calculate_sookshma_dasha_balance(moon_longitude, nakshatra_start, lord)
        mahadasha_periods = calculate_sookshma_dasha_periods(birth_date, remaining_time, lord, elapsed_time)

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




# Binnashtakavarga
# @bp.route('/lahairi/calculate_binnashtakavarga', methods=['POST'])
# def ashtakavarga_api_calculate_ashtakavarga():
#     try:
#         data = request.get_json()
#         if not data:
#             return jsonify({"error": "No JSON data provided"}), 400

#         required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
#         if not all(field in data for field in required_fields):
#             return jsonify({"error": "Missing required fields"}), 400

#         user_name = data.get('user_name', 'Unknown')
#         birth_date = data['birth_date']
#         birth_time = data['birth_time']
#         latitude = float(data['latitude'])
#         longitude = float(data['longitude'])
#         tz_offset = float(data['timezone_offset'])

#         jd = astro_binna_get_julian_day(birth_date, birth_time, tz_offset)
#         asc_lon = astro_binna_calculate_ascendant(jd, latitude, longitude)
#         asc_sign_index = astro_binna_get_sign_index(asc_lon)
#         asc_sign = ZODIAC_SIGNS[asc_sign_index]
#         positions = astro_utils_calculate_planet_positions(jd)
#         positions['Ascendant'] = {'longitude': asc_lon, 'sign_index': asc_sign_index}
#         bhinnashtakavarga = astro_utils_calculate_bhinnashtakavarga(positions)
#         astro_utils_validate_totals(bhinnashtakavarga)

#         bhinnashtakavarga_output = {
#             target: {"signs": {ZODIAC_SIGNS[i]: bindus[i] for i in range(12)}, "total_bindus": sum(bindus)}
#             for target, bindus in bhinnashtakavarga.items()
#         }
#         asc_degrees = astro_utils_format_dms(asc_lon % 30)

#         response = {
#             'user_name': user_name,
#             'ascendant': {'degrees': asc_degrees, 'sign': asc_sign},
#             'bhinnashtakavarga': bhinnashtakavarga_output,
#             'metadata': {'ayanamsa': 'Lahiri', 'calculation_time': datetime.utcnow().isoformat(), 'input': data}
#         }
#         return jsonify(response), 200

#     except Exception as e:
#         return jsonify({"error": f"Calculation error: {str(e)}"}), 500


@bp.route('/lahairi/calculate_binnatakvarga', methods=['POST'])
def calculate_ashtakvarga():
    """API endpoint to calculate Bhinnashtakavarga based on birth details."""
    try:
        # Get JSON data from request
        data = request.get_json()
        if not data:
            logger.error("No JSON data provided in request")
            return jsonify({"error": "No JSON data provided"}), 400

        # Validate required fields
        required = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            missing = [key for key in required if key not in data]
            logger.error(f"Missing required parameters: {missing}")
            return jsonify({"error": f"Missing required parameters: {missing}"}), 400

        # Extract and validate input data
        user_name = data['user_name']
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            logger.error(f"Invalid coordinates: latitude={latitude}, longitude={longitude}")
            return jsonify({"error": "Invalid latitude or longitude"}), 400

        # Calculate astrological data
        result = raman_bhinnashtakavarga(birth_date, birth_time, latitude, longitude, tz_offset)
        
        # Ensure planetary_positions exists in result
        if 'planetary_positions' not in result or not result['planetary_positions']:
            logger.error("planetary_positions missing or empty in calculation result")
            return jsonify({"error": "Failed to calculate planetary positions"}), 500

        # Construct response
        response = {
            "user_name": user_name,
            "birth_details": {
                "birth_date": birth_date,
                "birth_time": birth_time,
                "latitude": latitude,
                "longitude": longitude,
                "timezone_offset": tz_offset
            },
            "planetary_positions": result["planetary_positions"],
            "ascendant": result["ascendant"],
            "bhinnashtakavarga": result["bhinnashtakavarga"],
            "notes": {
                "ayanamsa": "Raman",
                "ayanamsa_value": f"{result['ayanamsa']:.6f}",
                "chart_type": "Rasi",
                "house_system": "Whole Sign"
            }
        }
        logger.info("Successfully calculated Bhinnashtakavarga")
        return jsonify(response), 200

    except ValueError as ve:
        logger.error(f"ValueError occurred: {str(ve)}")
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500




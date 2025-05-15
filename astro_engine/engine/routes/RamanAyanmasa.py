
from flask import Blueprint, request, jsonify
from datetime import datetime
import logging
from venv import logger

from astro_engine.engine.ashatakavargha.RamanBinnastakvargha import raman_binnastakavargha
from astro_engine.engine.lagnaCharts.MoonRaman import raman_moon_chart
from astro_engine.engine.lagnaCharts.RamanBavaLagna import raman_bava_lagna
from astro_engine.engine.lagnaCharts.RamanKpLagna import raman_kp_lagna
from astro_engine.engine.lagnaCharts.SunRaman import raman_sun
from astro_engine.engine.natalCharts.RamanChakara import raman_sudarshan_chakra
from astro_engine.engine.natalCharts.RamanNatal import raman_natal
from astro_engine.engine.ramanDivisionals.AkshavedamshaD45 import raman_akshavedamsha
from astro_engine.engine.ramanDivisionals.ChaturthamshaD4 import raman_chaturthamsha
from astro_engine.engine.ramanDivisionals.ChaturvimshamshaD24 import raman_chaturvimshamsha
from astro_engine.engine.ramanDivisionals.DashamshaD10 import raman_dashamsha
from astro_engine.engine.ramanDivisionals.DreshkanaD3 import raman_dreshkana
from astro_engine.engine.ramanDivisionals.DwadashamshaD12 import raman_dwadashamsha
from astro_engine.engine.ramanDivisionals.KhavedamshaD40 import raman_khavedamsha
from astro_engine.engine.ramanDivisionals.SaptamshaD7 import raman_saptamsha
from astro_engine.engine.ramanDivisionals.ShashtiamshaD60 import raman_shashtiamsha
from astro_engine.engine.ramanDivisionals.ShodashamshaD16 import raman_shodasamsa
from astro_engine.engine.ramanDivisionals.VimshamshaD20 import raman_vimsamsa





rl = Blueprint('rl_routes', __name__)


#   Natal Chart 
@rl.route('/raman/natal', methods=['POST'])
def raman_natal_endpoint():
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

        # Call the calculation function
        response = raman_natal(birth_data)
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500




#  Moon Chart 
@rl.route('/raman/calculate_moon_chart', methods=['POST'])
def calculate_moon_chart():
    try:
        # Get JSON data from request
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Call the calculation function
        response = raman_moon_chart(data)
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation failed: {str(e)}"}), 500



# Sun Chart :

@rl.route('/raman/calculate_sun_chart', methods=['POST'])
def calculate_sun_chart():
    """
    API endpoint to calculate Sun Chart (sidereal) with Whole Sign house system.
    """
    try:
        # Parse input
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Call the calculation function
        response = raman_sun(data)
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation failed: {str(e)}"}), 500



# Sudharasha Chakara 

@rl.route('/raman/calculate_sudarshan_chakra', methods=['POST'])
def calculate_sudarshan_chakra():
    """
    Flask endpoint to calculate the Sudarshan Chakra based on birth details.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        # Extract and validate input
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])
        user_name = data.get('user_name', 'Unknown')

        # Basic validation for latitude and longitude
        if not (-90 <= latitude <= 90):
            return jsonify({"error": "Latitude must be between -90 and 90 degrees"}), 400
        if not (-180 <= longitude <= 180):
            return jsonify({"error": "Longitude must be between -180 and 180 degrees"}), 400

        # Call the calculation function
        result = raman_sudarshan_chakra(birth_date, birth_time, latitude, longitude, tz_offset, user_name)
        return jsonify(result), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input format: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500





#**************************************************************************************************************
#***********************************    Divisonal Charts        ***********************************************
#**************************************************************************************************************



#  Hora D2 :




# Dreshkana D3

@rl.route('/raman/calculate_d3_chart', methods=['POST'])
def calculate_d3_chart_endpoint():
    """API endpoint to calculate D3 chart with retrograde status and nakshatras."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required fields"}), 400

        # Call the calculation function
        response = raman_dreshkana(data)
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


#  Chaturthamsha-D4
@rl.route('/raman/calculate_d4', methods=['POST'])
def calculate_d4_raman():
    """API endpoint to calculate the Chaturthamsha (D4) chart."""
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
        response = raman_chaturthamsha(data)
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500




# Saptamsha D7 
@rl.route('/raman/calculate_d7_chart', methods=['POST'])
def calculate_d7_chart_endpoint():
    """API endpoint to calculate D7 chart from birth details."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required fields"}), 400

        response = raman_saptamsha(data)
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


# Dashamsha D10

@rl.route('/raman/calculate_d10', methods=['POST'])
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

        response = raman_dashamsha(data)
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500



# Dwadashamsha D12

@rl.route('/raman/calculate_d12', methods=['POST'])
def calculate_d12():
    """
    Flask API endpoint to calculate the complete Dwadasamsa (D12) chart.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        # Call the calculation function
        response = raman_dwadashamsha(data)
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


#  Shodashamsha D16
@rl.route('/raman/calculate_d16', methods=['POST'])
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
        enforce_opposition = data.get('enforce_opposition', False)  # Default to False

        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180) or not (-12 <= tz_offset <= 14):
            return jsonify({"error": "Invalid geographic or timezone data"}), 400

        response = raman_shodasamsa(birth_date, birth_time, latitude, longitude, tz_offset, enforce_opposition)
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


#  Vimshamsha D20
@rl.route('/raman/calculate_d20', methods=['POST'])
def calculate_d20():
    """
    API endpoint to calculate the D20 (Vimsamsa) chart.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        # Call the calculation function
        response = raman_vimsamsa(data)
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input format: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


#  Chaturvimshamsha D24

@rl.route('/raman/calculate_d24', methods=['POST'])
def calculate_d24():
    """API endpoint to calculate D24 chart."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Call the calculation function
        response = raman_chaturvimshamsha(data)
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500



#  Khavedamsha D40
@rl.route('/raman/calculate_d40', methods=['POST'])
def calculate_d40():
    """API endpoint to calculate the D40 chart."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Call the calculation function
        response = raman_khavedamsha(data)
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


#  Akshavedamsha D45

@rl.route('/raman/calculate_d45', methods=['POST'])
def calculate_d45():
    """API endpoint to calculate D45 chart."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        # Call the calculation function
        response = raman_akshavedamsha(data)
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input format: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500




#  Shashtiamsha D60

@rl.route('/raman/calculate_d60', methods=['POST'])
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
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        response = raman_shashtiamsha(data)
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500






#**************************************************************************************************************
#***********************************    Lagna Charts        ***********************************************
#**************************************************************************************************************

#  Bava Lagna 

@rl.route('/raman/calculate_bhava_lagna', methods=['POST'])
def calculate_bhava_lagna():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        required = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400
        response = raman_bava_lagna(
            data['birth_date'],
            data['birth_time'],
            float(data['latitude']),
            float(data['longitude']),
            float(data['timezone_offset']),
            data['user_name']
        )
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": f"Calculation failed: {str(e)}"}), 500



#  KP Bava Lagna 

@rl.route('/raman/calculate_kp_bhava', methods=['POST'])
def calculate_kp_bhava_endpoint():
    """Calculate KP Bhava Chart from birth details."""
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
        calculation_result = raman_kp_lagna(birth_date, birth_time, latitude, longitude, tz_offset)

        # Construct response with user_name
        response = {
            'user_name': user_name,
            **calculation_result
        }
        return jsonify(response), 200

    except KeyError as e:
        return jsonify({"error": f"Missing input field: {str(e)}"}), 400
    except ValueError as e:
        return jsonify({"error": f"Invalid input value: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation failed: {str(e)}"}), 500
    






# #  Binnastakavargha 
# @rl.route('/raman/calculate_binnashtakvarga', methods=['POST'])
# def calculate_ashtakvarga():
#     """API endpoint to calculate Bhinnashtakavarga based on birth details."""
#     try:
#         data = request.get_json()
#         if not data:
#             return jsonify({"error": "No JSON data provided"}), 400

#         required = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
#         if not all(key in data for key in required):
#             return jsonify({"error": "Missing required parameters"}), 400

#         user_name = data['user_name']
#         birth_date = data['birth_date']
#         birth_time = data['birth_time']
#         latitude = float(data['latitude'])
#         longitude = float(data['longitude'])
#         tz_offset = float(data['timezone_offset'])

#         if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
#             return jsonify({"error": "Invalid latitude or longitude"}), 400

#         # Call the calculation function
#         response = raman_binnastakavargha(user_name, birth_date, birth_time, latitude, longitude, tz_offset)
#         return jsonify(response), 200

#     except ValueError as ve:
#         return jsonify({"error": str(ve)}), 400
#     except Exception as e:
#         return jsonify({"error": f"An error occurred: {str(e)}"}), 500






# API Endpoint
@rl.route('/calculate_ashtakvarga', methods=['POST'])
def calculate_ashtakvarga():
    """API endpoint to calculate Bhinnashtakavarga based on birth details."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        user_name = data['user_name']
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            return jsonify({"error": "Invalid latitude or longitude"}), 400

        # Call the calculation function
        calculation_result = raman_binnastakavargha(birth_date, birth_time, latitude, longitude, tz_offset)

        # Construct the response
        response = {
            "user_name": user_name,
            "birth_details": {
                "birth_date": birth_date,
                "birth_time": birth_time,
                "latitude": latitude,
                "longitude": longitude,
                "timezone_offset": tz_offset
            },
            **calculation_result
        }
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


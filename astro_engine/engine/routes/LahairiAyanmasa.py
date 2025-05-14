from flask import Blueprint, request, jsonify
from datetime import datetime
import logging
from venv import logger


from astro_engine.engine.divisionalCharts.ChathruthamshaD4 import calculate_d4_chart
from astro_engine.engine.divisionalCharts.ChaturvimshamshaD24 import calculate_d24_chart
from astro_engine.engine.divisionalCharts.DashamshaD10 import calculate_d10_chart
from astro_engine.engine.divisionalCharts.DreshkanaD3 import PLANET_NAMES, calculate_ascendant, calculate_d3_chart
from astro_engine.engine.divisionalCharts.DwadashamshaD12 import calculate_d12_chart
from astro_engine.engine.divisionalCharts.HoraD2 import calculate_d2_chart
from astro_engine.engine.divisionalCharts.KvedamshaD40 import calculate_d40_chart
from astro_engine.engine.divisionalCharts.NavamshaD9 import calculate_navamsa_chart
from astro_engine.engine.divisionalCharts.SaptamshaD7 import calculate_d7_chart
from astro_engine.engine.divisionalCharts.ShodasmasD16 import calculate_d16_chart

from astro_engine.engine.lagnaCharts.BavaLagna import bava_calculate_bhava_lagna
from astro_engine.engine.lagnaCharts.EqualLagan import SIGNS, bava_assign_planets_to_houses, bava_calculate_ascendant, bava_calculate_equal_bhava_cusps, bava_format_dms, bava_get_julian_day, bava_get_planet_positions
from astro_engine.engine.lagnaCharts.KPLagna import PLANETS, convert_to_julian_day, determine_significators, fetch_house_cusps, fetch_planet_positions, identify_nakshatra, identify_sign, identify_sub_lord, map_planets_to_houses
from astro_engine.engine.lagnaCharts.Sripathi import get_planet_data
from astro_engine.engine.natalCharts.natal import lahiri_natal
from astro_engine.engine.natalCharts.transit import calculate_transit_chart
from astro_engine.engine.numerology.CompositeChart import calculate_composite_chart
from astro_engine.engine.numerology.LoShuGridNumerology import calculate_lo_shu_grid
from astro_engine.engine.ashatakavargha.Binnastakavargha import ZODIAC_SIGNS, astro_binna_calculate_ascendant, astro_binna_get_julian_day, astro_binna_get_sign_index, astro_utils_calculate_bhinnashtakavarga, astro_utils_calculate_planet_positions, astro_utils_format_dms, astro_utils_validate_totals
from astro_engine.engine.numerology.NumerologyData import calculate_chaldean_numbers, calculate_date_numerology, get_sun_sign, get_element_from_number, get_sun_sign_element, get_elemental_compatibility, personal_interpretations, business_interpretations, ruling_planets, planet_insights, sun_sign_insights, number_colors, number_gemstones, planet_days
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
from astro_engine.engine.numerology.ProgressChart import calculate_progressed_chart
from astro_engine.engine.numerology.SynatryChart import calculate_synastry, validate_person_data


bp = Blueprint('bp_routes', __name__)

# Natal Chart
# @bp.route('/natal', methods=['POST'])
# def natal_chart():
#     try:
#         birth_data = request.get_json()
#         if not birth_data:
#             return jsonify({"error": "No JSON data provided"}), 400

#         required = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
#         if not all(key in birth_data for key in required):
#             return jsonify({"error": "Missing required parameters"}), 400

#         latitude = float(birth_data['latitude'])
#         longitude = float(birth_data['longitude'])
#         timezone_offset = float(birth_data['timezone_offset'])
#         if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
#             return jsonify({"error": "Invalid latitude or longitude"}), 400

#         response = calculate_natal_chart(birth_data)
#         return jsonify(response)

#     except ValueError as ve:
#         return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
#     except Exception as e:
#         return jsonify({"error": f"An error occurred: {str(e)}"}), 500



@bp.route('/lahairi_natal', methods=['POST'])
def lahairi_natal_endpoint():
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
        response = lahiri_natal(birth_data)
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500




# Transit or Gochar Chart
@bp.route('/transit', methods=['POST'])
def transit_chart():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        response = calculate_transit_chart(data)
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Sun Chart
@bp.route('/calculate_sun', methods=['POST'])
def calculate_sun_chart():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        validate_input(data)
        
        user_name = data.get('user_name', 'Unknown')
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        jd = get_julian_day(birth_date, birth_time, tz_offset)
        planetary_positions = calculate_planetary_positions(jd)
        sun_longitude = planetary_positions['Sun'][0]
        sun_sign_index = int(sun_longitude // 30)
        sun_sign = SIGNS[sun_sign_index]
        sun_degree = sun_longitude % 30
        house_cusps = calculate_whole_sign_cusps(sun_longitude)
        house_assignments = assign_planets_to_houses(planetary_positions, sun_sign_index)

        house_data = [
            {"house": i + 1, "cusp": format_dms(house_cusps[i]), "sign": SIGNS[(sun_sign_index + i) % 12]}
            for i in range(12)
        ]
        planetary_data = [
            {"planet": planet, "longitude": format_dms(longitude), "sign": SIGNS[int(longitude // 30)], "retrograde": retrograde, "house": house_assignments[planet]}
            for planet, (longitude, retrograde) in planetary_positions.items()
        ]

        response = {
            "user_name": user_name,
            "surya_lagna": {"longitude": format_dms(sun_longitude), "sign": sun_sign, "degree": format_dms(sun_degree)},
            "house_cusps": house_data,
            "planetary_positions": planetary_data,
            "metadata": {"ayanamsa": "Lahiri", "house_system": "Whole Sign", "calculation_time": datetime.utcnow().isoformat(), "input": data}
        }
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation failed: {str(e)}"}), 500

# Moon Chart
@bp.route('/calculate_moon', methods=['POST'])
def calculate_moon_chart():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        validate_input(data)
        
        user_name = data.get('user_name', 'Unknown')
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        jd = get_julian_day(birth_date, birth_time, tz_offset)
        planetary_positions = calculate_planetary_positions(jd)
        moon_longitude = planetary_positions['Moon'][0]
        moon_sign_index = int(moon_longitude // 30)
        moon_sign = SIGNS[moon_sign_index]
        moon_degree = moon_longitude % 30
        house_cusps = calculate_whole_sign_cusps(moon_longitude)
        house_assignments = assign_planets_to_houses(planetary_positions, moon_sign_index)

        house_data = [
            {"house": i + 1, "cusp": format_dms(house_cusps[i]), "sign": SIGNS[(moon_sign_index + i) % 12]}
            for i in range(12)
        ]
        planetary_data = [
            {"planet": planet, "longitude": format_dms(longitude), "sign": SIGNS[int(longitude // 30)], "retrograde": retrograde, "house": house_assignments[planet]}
            for planet, (longitude, retrograde) in planetary_positions.items()
        ]

        response = {
            "user_name": user_name,
            "chandra_lagna": {"longitude": format_dms(moon_longitude), "sign": moon_sign, "degree": format_dms(moon_degree)},
            "house_cusps": house_data,
            "planetary_positions": planetary_data,
            "metadata": {"ayanamsa": "Lahiri", "house_system": "Whole Sign", "calculation_time": datetime.utcnow().isoformat(), "input": data}
        }
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
@bp.route('/calculate_d2', methods=['POST'])
def calculate_d2():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        response = calculate_d2_chart(data)
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# Dreshkana (D-3)
@bp.route('/calculate_d3', methods=['POST'])
def calculate_d3_chart_endpoint():
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
@bp.route('/calculate_d4', methods=['POST'])
def calculate_d4():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        response = calculate_d4_chart(data)
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


# Saptamsha (D-7)
@bp.route('/calculate_d7', methods=['POST'])
def calculate_d7_chart_endpoint():
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
        d7_data = calculate_d7_chart(jd, latitude, longitude)

        response = {
            "ascendant": d7_data['Ascendant'],
            "planets": {planet: d7_data[planet] for planet in PLANET_NAMES}
        }
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error in D7 calculation: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# Dashamsha (D-10)
@bp.route('/calculate_d10', methods=['POST'])
def calculate_d10():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        response = calculate_d10_chart(data)
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Dwadashamsha (D-12)
@bp.route('/calculate_d12', methods=['POST'])
def calculate_d12():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        response = calculate_d12_chart(data)
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Shodashamsha (D-16)
@bp.route('/calculate_d16', methods=['POST'])
def calculate_d16():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required fields"}), 400

        response = calculate_d16_chart(data)
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# Vimshamsha (D-20)
@bp.route('/calculate_d20', methods=['POST'])
def calculate_d20():
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

        chart_data = calculate_d20_chart(birth_date, birth_time, latitude, longitude, tz_offset)
        response = {
            "user_name": user_name,
            **chart_data,
            "metadata": {"ayanamsa": "Lahiri", "chart_type": "Vimsamsa (D20)", "house_system": "Whole Sign", "calculation_time": datetime.utcnow().isoformat()}
        }
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input format: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# Chaturvimshamsha (D-24)
@bp.route('/calculate_d24', methods=['POST'])
def calculate_d24():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        response = calculate_d24_chart(data)
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# Saptavimshamsha (D-27)
@bp.route('/calculate_d27', methods=['POST'])
def calculate_d27_chart():
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
            "d27_chart": {"positions": {planet: SIGN_NAMES[sign - 1] for planet, sign in d27_positions.items()}, "houses": d27_houses}
        }
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500

# Khavedamsha (D-40)
@bp.route('/calculate_d40', methods=['POST'])
def calculate_d40():
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

        response = calculate_d40_chart(birth_date, birth_time, latitude, longitude, tz_offset)
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# Akshavedamsha (D-45)
@bp.route('/calculate_d45', methods=['POST'])
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

        jd_ut = get_julian_day(birth_date, birth_time, tz_offset)
        chart_data = calculate_d45_chart(jd_ut, latitude, longitude)
        response = {
            "user_name": data.get('user_name', 'Unknown'),
            **chart_data,
            "metadata": {"ayanamsa": "Lahiri", "chart_type": "Akshavedamsa (D45)", "house_system": "Whole Sign", "calculation_time": datetime.utcnow().isoformat()}
        }
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input format: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# Shashtiamsha (D-60)
@bp.route('/calculate_d60', methods=['POST'])
def calculate_d60():
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

        jd_ut = get_julian_day(birth_date, birth_time, tz_offset)
        chart_data = calculate_d60_chart(jd_ut, latitude, longitude)
        response = {
            "user_name": user_name,
            **chart_data,
            "metadata": {"ayanamsa": "Lahiri", "chart_type": "Shashtiamsha (D60)", "house_system": "Whole Sign", "calculation_time": datetime.utcnow().isoformat()}
        }
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# Navamsa Chart
@bp.route('/navamsa', methods=['POST'])
def navamsa_chart():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required):
            return jsonify({"error": "Missing required parameters"}), 400

        response = calculate_navamsa_chart(data)
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Sripathi Bhava
@bp.route('/calculate_sripathi_bhava', methods=['POST'])
def calculate_sripathi_bhava():
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
            "ascendant": {"sign": asc_sign, "degrees": round(asc_degrees, 4)},
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

# KP Bhava
@bp.route('/calculate_kp_bhava', methods=['POST'])
def process_kp_bhava():
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

        cusp_details = [
            {'house': i, 'longitude': round(cusp, 4), 'sign': identify_sign(cusp), 'nakshatra': identify_nakshatra(cusp), 'sub_lord': identify_sub_lord(cusp)}
            for i, cusp in enumerate(house_cusps, 1)
        ]

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

# Equal Bhava Lagna
@bp.route('/calculate_equal_bhava_lagna', methods=['POST'])
def bava_calculate_endpoint():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(key in data for key in required_fields):
            return jsonify({"error": "Missing required parameters"}), 400

        user_name = data.get('user_name', 'Unknown')
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        jd = bava_get_julian_day(birth_date, birth_time, tz_offset)
        ascendant = bava_calculate_ascendant(jd, latitude, longitude)
        ascendant_sign_index = int(ascendant // 30)
        planetary_positions = bava_get_planet_positions(jd)
        cusps_degrees = bava_calculate_equal_bhava_cusps(ascendant)
        cusps_formatted = [bava_format_dms(cusp) for cusp in cusps_degrees]
        house_data = [
            {"house": i + 1, "cusp": cusps_formatted[i], "sign": SIGNS[int(cusps_degrees[i] // 30)]}
            for i in range(12)
        ]
        house_assignments = bava_assign_planets_to_houses(planetary_positions, ascendant_sign_index)
        planetary_data = [
            {"planet": planet, "longitude": bava_format_dms(longitude), "sign": SIGNS[int(longitude // 30)], "retrograde": retrograde, "house": house_assignments[planet]}
            for planet, (longitude, retrograde) in planetary_positions.items()
        ]

        response = {
            "user_name": user_name,
            "ascendant": {"longitude": bava_format_dms(ascendant), "sign": SIGNS[ascendant_sign_index]},
            "planetary_positions": planetary_data,
            "house_cusps": house_data,
            "metadata": {"ayanamsa": "Lahiri", "house_system": "Equal Bhava (Whole Sign based)", "calculation_time": datetime.utcnow().isoformat(), "input": data}
        }
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation failed: {str(e)}"}), 500

# Bhava Lagna
@bp.route('/calculate_bhava_lagna', methods=['POST'])
def calculate_bhava_lagna_route():
    try:
        data = request.get_json()
        user_name = data['user_name']
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        timezone_offset = float(data['timezone_offset'])

        result = bava_calculate_bhava_lagna(birth_date, birth_time, latitude, longitude, timezone_offset)
        response = {
            "user_name": user_name,
            "result": result,
            "metadata": {"ayanamsa": "Lahiri", "house_system": "Whole Sign", "calculation_time": datetime.utcnow().isoformat()}
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"Calculation failed: {str(e)}"}), 500

# Synastry
@bp.route('/synastry', methods=['POST'])
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
        response = calculate_synastry(data)
        return jsonify(response), 200
    except Exception as e:
        logging.error(f"Error in synastry calculation: {str(e)}")
        return jsonify({'error': str(e)}), 400

# Composite Chart
@bp.route('/composite', methods=['POST'])
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
        response = calculate_composite_chart(data)
        return jsonify(response), 200
    except Exception as e:
        logging.error(f"Error in composite chart calculation: {str(e)}")
        return jsonify({'error': str(e)}), 400

# Progressed Chart
@bp.route('/progressed', methods=['POST'])
def progressed_chart():
    data = request.get_json()
    required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude', 'tz_offset', 'age']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    try:
        response = calculate_progressed_chart(data)
        return jsonify(response), 200
    except ValueError as e:
        return jsonify({'error': f'Invalid input data: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Calculation failed: {str(e)}'}), 500

# Chaldean Numerology
@bp.route('/chaldean_numerology', methods=['POST'])
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
@bp.route('/lo_shu_grid_numerology', methods=['POST'])
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
@bp.route('/calculate_maha_antar_dasha', methods=['POST'])
def calculate_vimshottari_dasha():
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

# Vimshottari Antardasha and Pratyantardashas
@bp.route('/calculate_antar_prathythar_dasha', methods=['POST'])
def calculate_vimshottari_Pratyantardashas():
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

# Vimshottari Pratyantardasha and Sookshma Dasha
@bp.route('/calculate_vimshottari_Sookshama', methods=['POST'])
def calculate_vimshottari_Sookshama():
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

# Binnashtakavarga
@bp.route('/calculate_binnashtakavarga', methods=['POST'])
def ashtakavarga_api_calculate_ashtakavarga():
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

        jd = astro_binna_get_julian_day(birth_date, birth_time, tz_offset)
        asc_lon = astro_binna_calculate_ascendant(jd, latitude, longitude)
        asc_sign_index = astro_binna_get_sign_index(asc_lon)
        asc_sign = ZODIAC_SIGNS[asc_sign_index]
        positions = astro_utils_calculate_planet_positions(jd)
        positions['Ascendant'] = {'longitude': asc_lon, 'sign_index': asc_sign_index}
        bhinnashtakavarga = astro_utils_calculate_bhinnashtakavarga(positions)
        astro_utils_validate_totals(bhinnashtakavarga)

        bhinnashtakavarga_output = {
            target: {"signs": {ZODIAC_SIGNS[i]: bindus[i] for i in range(12)}, "total_bindus": sum(bindus)}
            for target, bindus in bhinnashtakavarga.items()
        }
        asc_degrees = astro_utils_format_dms(asc_lon % 30)

        response = {
            'user_name': user_name,
            'ascendant': {'degrees': asc_degrees, 'sign': asc_sign},
            'bhinnashtakavarga': bhinnashtakavarga_output,
            'metadata': {'ayanamsa': 'Lahiri', 'calculation_time': datetime.utcnow().isoformat(), 'input': data}
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"Calculation error: {str(e)}"}), 500







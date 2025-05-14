
from flask import Blueprint, request, jsonify
from datetime import datetime
import logging
from venv import logger

from astro_engine.engine.kpSystem.charts.BhavaHouses import calculate_bhava_houses_details
from astro_engine.engine.kpSystem.charts.CupsalChart import ZODIAC_SIGNS, cupsal_assign_nakshatra_and_lords, cupsal_assign_planet_to_house, cupsal_calculate_ascendant_and_cusps, cupsal_calculate_kp_new_ayanamsa, cupsal_calculate_planet_positions, cupsal_calculate_significators, cupsal_format_dms, cupsal_get_julian_day
from astro_engine.engine.kpSystem.charts.RulingPlanets import ruling_calculate_ascendant_and_cusps, ruling_calculate_balance_of_dasha, ruling_calculate_fortuna, ruling_calculate_jd, ruling_calculate_planet_positions, ruling_check_rahu_ketu, ruling_compile_core_rp, ruling_get_day_lord, ruling_get_details
from astro_engine.engine.kpSystem.charts.SignificatorHouse import calculate_planets_significations




kp = Blueprint('kp_routes', __name__)



# KP Planets and Cusps
@kp.route('/calculate_kp_planets_cusps', methods=['POST'])
def calculate_kp_planets_cusps():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        required_fields = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        user_name = data['user_name']
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        tz_offset = float(data['timezone_offset'])

        jd = cupsal_get_julian_day(birth_date, birth_time, tz_offset)
        kp_new_ayanamsa = cupsal_calculate_kp_new_ayanamsa(jd)
        ascendant, house_cusps = cupsal_calculate_ascendant_and_cusps(jd, latitude, longitude, kp_new_ayanamsa)
        planets = cupsal_calculate_planet_positions(jd, kp_new_ayanamsa)

        planet_details = {
            planet: {
                "longitude": cupsal_format_dms(lon),
                "sign": ZODIAC_SIGNS[int(lon // 30)],
                "nakshatra": cupsal_assign_nakshatra_and_lords(lon)[0],
                "star_lord": cupsal_assign_nakshatra_and_lords(lon)[1],
                "sub_lord": cupsal_assign_nakshatra_and_lords(lon)[2],
                "house": cupsal_assign_planet_to_house(lon, house_cusps)
            }
            for planet, lon in planets.items()
        }
        cusp_details = {
            str(i + 1): {
                "longitude": cupsal_format_dms(cusp),
                "sign": ZODIAC_SIGNS[int(cusp // 30)],
                "nakshatra": cupsal_assign_nakshatra_and_lords(cusp)[0],
                "star_lord": cupsal_assign_nakshatra_and_lords(cusp)[1],
                "sub_lord": cupsal_assign_nakshatra_and_lords(cusp)[2]
            }
            for i, cusp in enumerate(house_cusps)
        }
        significators = cupsal_calculate_significators(planets, house_cusps)

        response = {
            "user_name": user_name,
            "ascendant": {"longitude": cupsal_format_dms(ascendant), "sign": ZODIAC_SIGNS[int(ascendant // 30)]},
            "house_cusps": cusp_details,
            "planets": planet_details,
            "significators": significators,
            "metadata": {"ayanamsa": "KP New", "house_system": "Placidus", "calculation_time": datetime.utcnow().isoformat(), "input": data}
        }
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Calculation failed: {str(e)}"}), 500
    




# Ruling Planets
@kp.route('/calculate_ruling_planets', methods=['POST'])
def calculate_ruling_planets():
    try:
        data = request.get_json()
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        timezone_offset = float(data['timezone_offset'])

        jd, utc_dt = ruling_calculate_jd(birth_date, birth_time, timezone_offset)
        ascendant, cusps = ruling_calculate_ascendant_and_cusps(jd, latitude, longitude)
        sun_pos, moon_pos, rahu_pos, ketu_pos = ruling_calculate_planet_positions(jd)
        day_lord = ruling_get_day_lord(utc_dt)
        lagna_sign, lagna_rashi_lord, lagna_nakshatra, lagna_star_lord, lagna_sub_lord = ruling_get_details(ascendant)
        moon_sign, moon_rashi_lord, moon_nakshatra, moon_star_lord, moon_sub_lord = ruling_get_details(moon_pos)
        lagna_details = {'rashi_lord': lagna_rashi_lord, 'star_lord': lagna_star_lord, 'sub_lord': lagna_sub_lord}
        moon_details = {'rashi_lord': moon_rashi_lord, 'star_lord': moon_star_lord, 'sub_lord': moon_sub_lord}
        core_rp = ruling_compile_core_rp(lagna_details, moon_details, day_lord)
        core_rp = ruling_check_rahu_ketu(rahu_pos, ketu_pos, core_rp)
        fortuna = ruling_calculate_fortuna(ascendant, moon_pos, sun_pos)
        dasha_lord, balance_years = ruling_calculate_balance_of_dasha(moon_pos, moon_star_lord)

        response = {
            "ruling_planets": list(core_rp),
            "details": {
                "day_lord": day_lord,
                "lagna_lord": lagna_rashi_lord,
                "lagna_nakshatra_lord": lagna_star_lord,
                "lagna_sub_lord": lagna_sub_lord,
                "moon_rashi_lord": moon_rashi_lord,
                "moon_nakshatra_lord": moon_star_lord,
                "moon_sub_lord": moon_sub_lord,
                "fortuna": round(fortuna, 4),
                "balance_of_dasha": {"dasha_lord": dasha_lord, "balance_years": round(balance_years, 4)}
            }
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400




# Bhava Details
@kp.route('/calculate_bhava_details', methods=['POST'])
def calculate_bhava_details():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        required_fields = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        user_name = data['user_name']
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        timezone_offset = float(data['timezone_offset'])

        bhava_details = calculate_bhava_houses_details(birth_date, birth_time, latitude, longitude, timezone_offset)
        response = {
            'user_name': user_name,
            'bhava_details': bhava_details
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400






# House Significations
@kp.route('/calculate_significations', methods=['POST'])
def calculate_significations():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        required_fields = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        user_name = data['user_name']
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        timezone_offset = float(data['timezone_offset'])

        significators = calculate_planets_significations(birth_date, birth_time, latitude, longitude, timezone_offset)
        response = {
            'user_name': user_name,
            'house_significations': significators
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400
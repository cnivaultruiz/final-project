import json
import math
from collections import defaultdict
from flask import Flask, abort, request
from flask_basicauth import BasicAuth
from flask_swagger_ui import get_swaggerui_blueprint
import pymysql
import os


app = Flask(__name__)
app.config.from_file("flask_config_himalaya.json", load=json.load)
auth = BasicAuth(app)

swaggerui_blueprint = get_swaggerui_blueprint(
    base_url='/docs',
    api_url='/static/himalayaapi.yaml',
)
app.register_blueprint(swaggerui_blueprint)

MAX_PAGE_SIZE = 100

def remove_null_fields(obj):
    return {k:v for k, v in obj.items() if v is not None}

@app.route('/')
def home():
    return {
        "message": "Welcome to the Himalaya API. Use /docs to access the Swagger documentation.",
        "overview": "The Himalaya API provides access to information about Himalayan peaks and expeditions.",
        "details": "This API allows users to retrieve details about various peaks and expeditions, including the ability to filter results based on specific criteria such as height or year.",
    }, 200

@app.route("/peaks")
@auth.required
def peaks():
     #URL Parameters
    page = int(request.args.get('page', 0))
    page_size = int(request.args.get('page_size', MAX_PAGE_SIZE))
    page_size = min(page_size, MAX_PAGE_SIZE)
    include_details = bool(int(request.args.get('include_details',0)))
    height_min = request.args.get('height_min', 0)


    db_conn = pymysql.connect(host="localhost", user="root",password= os.getenv('my_SQL_pw'), database="himalaya",
                              cursorclass=pymysql.cursors.DictCursor)
    # Get the peaks
    with db_conn.cursor() as cursor:
        query = """
                SELECT 
                    peak_name,
                    peak_id,
                    height_metres
                FROM peaks
            """
        if height_min is not None:
                query += " WHERE height_metres >= %s"
                params = (height_min, page_size, page * page_size)
        else:
                params = (page_size, page * page_size)

        # Add order, limit, and offset
        query += " ORDER BY peak_id LIMIT %s OFFSET %s"
        cursor.execute(query, params)
        peaks = cursor.fetchall()
    
    if include_details:
        with db_conn.cursor() as cursor:
            #placeholder = ','.join(['%s'] * len(peak_id))
            query = """
                    SELECT
                    peak_name,
                    peak_id,
                    height_metres,
                    peak_alternative_name,
                    first_ascent_year,
                    first_ascent_country
                    FROM peaks """
            if height_min is not None:
                query += " WHERE height_metres >= %s"
                params = (height_min, page_size, page * page_size)
            else:
                params = (page_size, page * page_size)

            # Add order, limit, and offset
            query += " ORDER BY peak_id LIMIT %s OFFSET %s"
            cursor.execute(query, params)
            peaks = cursor.fetchall()


    with db_conn.cursor() as cursor:
            if height_min:
                cursor.execute("SELECT COUNT(*) AS total FROM peaks WHERE height_metres >= %s", (height_min,))
            else:
                cursor.execute("SELECT COUNT(*) AS total FROM peaks")
            total = cursor.fetchone()
            last_page = math.ceil(total['total'] / page_size)


    db_conn.close()
    return {
        
        'peaks': peaks,
        'next_page': f'/peaks?page={page+1}&page_size={page_size}&include_details={int(include_details)}&height_min={int(height_min)}',
        'last_page': f'/peaks?page={last_page}&page_size={page_size}&include_details={int(include_details)}&height_min={int(height_min)}',
    }

@app.route("/peaks/<peak_id>")
@auth.required
def peak(peak_id):
    db_conn = pymysql.connect(host="localhost", user="root",password= os.getenv('my_SQL_pw'), database="himalaya",
                              cursorclass=pymysql.cursors.DictCursor)

    with db_conn.cursor() as cursor:
        cursor.execute("""
            SELECT 
            p.peak_name,
            p.peak_id,
            p.height_metres,
            p.peak_alternative_name,
            p.first_ascent_year,
            p.first_ascent_country,
            avg(m.age) as age_mean,
            sum(m.died) as nb_died,
            sum(m.success) as nb_success,
            sum(m.success)/count(m.success) *100 as tx_success,
            sum(m.oxygen_used)/count(m.oxygen_used) *100 as tx_oxygen_used            
            FROM peaks p
            left join members m on p.peak_id = m.peak_id
            WHERE p.peak_id=%s
            group by p.peak_name, p.peak_id, p.height_metres, p.peak_alternative_name, p.first_ascent_year, p.first_ascent_country
            ORDER BY peak_id 
             """, (peak_id, ))
        peak = cursor.fetchone()
        if not peak:
            abort(404,description="Peak not found")
        peak = remove_null_fields(peak)

        cursor.execute("""
                    SELECT 
                    harmonized_agency_name,
                    count(distinct expedition_id) as nb_expedition,
                    sum(is_success)/count(distinct expedition_id) as success_rate
                    FROM himalaya.expedition
                    WHERE peak_id = %s and harmonized_agency_name != 'Unknown'
                    GROUP BY harmonized_agency_name
                    ORDER BY nb_expedition desc
                    LIMIT 1
                """, (peak_id,))
        best_agency = cursor.fetchone()
        if best_agency:
            peak['best_agency'] = {
                'name': best_agency['harmonized_agency_name'],
                'nb_expeditions': best_agency['nb_expedition'],
                'success_rate': round(best_agency['success_rate'], 2)
            }
        else:
            peak['best_agency'] = None
    
    with db_conn.cursor() as cursor:
        cursor.execute("SELECT * FROM members WHERE peak_id=%s AND success=1", (peak_id, ))
        citizenship = cursor.fetchall()
    peak['zcitizenship_sucess'] = [pk['citizenship'] for pk in citizenship]
    


    db_conn.close()
    return peak


@app.route("/expeditions")
@auth.required
def expeditions():
     #URL Parameters
    page = int(request.args.get('page', 0))
    page_size = int(request.args.get('page_size', MAX_PAGE_SIZE))
    page_size = min(page_size, MAX_PAGE_SIZE)
    year = request.args.get('year')

    db_conn = pymysql.connect(host="localhost", user="root",password= os.getenv('my_SQL_pw'), database="himalaya",
                              cursorclass=pymysql.cursors.DictCursor)
    # Get the expedition
    query = """
        SELECT 
            expedition_id,
            peak_name,
            year,
            season
        FROM expedition
    """
    params = []

    # Add year filter if specified
    if year:
        query += " WHERE year = %s"
        params.append(year)

    # Add order, limit, and offset
    query += " ORDER BY expedition_id LIMIT %s OFFSET %s"
    params.extend([page_size, page * page_size])

    # Get the expeditions
    with db_conn.cursor() as cursor:
        cursor.execute(query, params)
        expeditions = cursor.fetchall()


    with db_conn.cursor() as cursor:
            if year:
                cursor.execute("SELECT COUNT(*) AS total FROM expedition WHERE year = %s", (year,))
            else:
                cursor.execute("SELECT COUNT(*) AS total FROM expedition")
            total = cursor.fetchone()
            last_page = math.ceil(total['total'] / page_size)


    db_conn.close()
    return {
        '1-next_page': f'/expeditions?page={page+1}&page_size={page_size}&year={year}',
        '2-last_page': f'/expeditions?page={last_page}&page_size={page_size}&year={year}',
        '3-expedition': expeditions,
    }
        
@app.route("/expeditions/<expedition_id>")
@auth.required
def expedition(expedition_id):
    db_conn = pymysql.connect(host="localhost", user="root",password= os.getenv('my_SQL_pw'), database="himalaya",
                              cursorclass=pymysql.cursors.DictCursor)

    with db_conn.cursor() as cursor:
        cursor.execute("SELECT * FROM expedition WHERE expedition_id=%s" ,(expedition_id, ))
        expedition = cursor.fetchone()
        if not expedition:
            abort(404,description="expedition not found")
        expedition = remove_null_fields(expedition)

    db_conn.close()
    return expedition

@app.route("/statistics")
@auth.required
def global_statistics():
    start_year = request.args.get('start_year', type=int)
    end_year = request.args.get('end_year', type=int)

    db_conn = pymysql.connect(host="localhost", user="root", password=os.getenv('my_SQL_pw'), database="himalaya",
                                cursorclass=pymysql.cursors.DictCursor)
        
    stats = {}
    
    with db_conn.cursor() as cursor:
        # Nombre total de pics
        cursor.execute("SELECT COUNT(*) as total_peaks FROM peaks")
        stats['total_peaks'] = cursor.fetchone()['total_peaks']
        
        # Hauteur moyenne des pics
        cursor.execute("SELECT AVG(height_metres) as avg_height FROM peaks")
        stats['average_peak_height'] = round(cursor.fetchone()['avg_height'], 2)
        
        # Nombre total d'expéditions
        if start_year and end_year :
            cursor.execute("SELECT COUNT(*) as total_expeditions FROM expedition WHERE year BETWEEN %s AND %s",(start_year, end_year ))
        else :
             cursor.execute("SELECT COUNT(*) as total_expeditions FROM expedition")
        stats['total_expeditions'] = cursor.fetchone()['total_expeditions']
        
        # Taux de réussite global
        if start_year and end_year :
            cursor.execute("""
                SELECT 
                    SUM(success) as total_success,
                    COUNT(*) as total_attempts,
                    (SUM(success) / COUNT(*)) * 100 as success_rate
                FROM members
                WHERE year BETWEEN %s AND %s
            """,(start_year, end_year ))
        else : 
             cursor.execute("""
                SELECT 
                    SUM(success) as total_success,
                    COUNT(*) as total_attempts,
                    (SUM(success) / COUNT(*)) * 100 as success_rate
                FROM members
                """)
        result = cursor.fetchone()
        stats['total_climbers'] = result['total_attempts']
        stats['total_summits'] = result['total_success']
        stats['global_success_rate'] = round(result['success_rate'], 2)
        
        # Pic le plus gravi
        if start_year and end_year :
            cursor.execute("""
                SELECT p.peak_name, COUNT(*) as expedition_count
                FROM expedition e
                JOIN peaks p ON e.peak_id = p.peak_id
                WHERE e.year between %s and %s
                GROUP BY p.peak_name
                ORDER BY expedition_count DESC
                LIMIT 1
            """,(start_year, end_year ))
        else : 
            cursor.execute("""
                SELECT p.peak_name, COUNT(*) as expedition_count
                FROM expedition e
                JOIN peaks p ON e.peak_id = p.peak_id
                GROUP BY p.peak_name
                ORDER BY expedition_count DESC
                LIMIT 1
            """)
        most_climbed = cursor.fetchone()
        stats['most_climbed_peak'] = {
            'name': most_climbed['peak_name'],
            'expeditions': most_climbed['expedition_count']
        }
        
        # Année avec le plus d'expéditions
        if start_year and end_year :
            cursor.execute("""
                SELECT year, COUNT(*) as expedition_count
                FROM expedition
                WHERE year between %s and %s
                GROUP BY year
                ORDER BY expedition_count DESC
                LIMIT 1
            """,(start_year, end_year ))
        else : 
            cursor.execute("""
                SELECT year, COUNT(*) as expedition_count
                FROM expedition
                GROUP BY year
                ORDER BY expedition_count DESC
                LIMIT 1
            """)
        busiest_year = cursor.fetchone()
        stats['busiest_year'] = {
            'year': busiest_year['year'],
            'expeditions': busiest_year['expedition_count']
        }

        # agences les plus experimentées : 
        if start_year and end_year :
            cursor.execute("""
                SELECT 
                harmonized_agency_name,
                count(distinct expedition_id) as nb_expedition,
                sum(is_success)/count(distinct expedition_id)  as success_rate
                FROM himalaya.expedition
                WHERE year between %s and %s and harmonized_agency_name != 'Unknown'
                GROUP BY harmonized_agency_name
                ORDER BY nb_expedition desc
                LIMIT 1
            """,(start_year, end_year ))
        else : 
            cursor.execute("""
                                SELECT 
                harmonized_agency_name,
                count(distinct expedition_id) as nb_expedition,
                sum(is_success)/count(distinct expedition_id)  as success_rate
                FROM himalaya.expedition
                WHERE harmonized_agency_name != 'Unknown'
                GROUP BY harmonized_agency_name
                ORDER BY nb_expedition desc
                LIMIT 1
            """)
        best_agency = cursor.fetchone()
        stats['best_agency'] = {
            'name': best_agency['harmonized_agency_name'],
            'nb_expeditions': best_agency['nb_expedition'],
            'success_rate': best_agency['success_rate']
        }

        db_conn.close()
        return {
            '0- param': f'/statistics?start_year={start_year}&end_year={end_year}',
            '1- stats' : stats
        }
             
                       
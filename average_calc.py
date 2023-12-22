import os
import psycopg2
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
DBHOST = os.getenv("DBHOST")
DBUSER = os.getenv("DBUSER")
DBNAME = os.getenv("DBNAME")
DBPASSWORD = os.getenv("DBPASSWORD")

conn = psycopg2.connect(dbname=DBNAME, user=DBUSER, password=DBPASSWORD, host=DBHOST)


def calculate_daily_averages_and_prune():
    cur = conn.cursor()

    cur.execute("SELECT DISTINCT device_id FROM historical_data")
    device_ids = [row[0] for row in cur.fetchall()]

    for device_id in device_ids:
        one_day_ago = datetime.now() - timedelta(days=1)
        cur.execute(
            """
            SELECT AVG(temp) as avg_temp, AVG(soil_hum) as avg_soil_hum, 
                   AVG(air_hum) as avg_air_hum, AVG(light) as avg_light
            FROM historical_data
            WHERE device_id = %s AND created_at >= %s
        """,
            (device_id, one_day_ago),
        )

        result = cur.fetchone()

        if result:
            cur.execute(
                """
                INSERT INTO daily_averages (device_id, avg_temp, avg_soil_hum, avg_air_hum, avg_light, date)
                VALUES (%s, %s, %s, %s, %s, CURRENT_DATE)
            """,
                (device_id, result[0], result[1], result[2], result[3]),
            )

    seven_days_ago = (datetime.now() - timedelta(days=7)).date()

    cur.execute("DELETE FROM historical_data")
    cur.execute("DELETE FROM daily_averages WHERE date < %s", (seven_days_ago,))

    conn.commit()
    cur.close()


calculate_daily_averages_and_prune()
conn.close()

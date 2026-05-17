import os
import mysql.connector
from mysql.connector import pooling
from dotenv import load_dotenv

# Pakia vigezo kutoka kwenye faili la mazingira ya kazi
# Kama unatumia faili maalum la malipo.env, badilisha kuwa load_dotenv("malipo.env")
load_dotenv()

# Caching/Uwekaji wa taarifa za seva ya MySQL kutoka kwenye .env
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "ramadhana_db")
DB_PORT = os.getenv("DB_PORT", "3306")

# Kutengeneza Connection Pool (Muhimu sana kwa Hosting kama Hostinger/Cloudnet)
# Hii inasaidia website isife watumiaji wengi wakifungua akaunti au kuangalia miamala kwa pamoja
try:
    db_pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="rama_pool",
        pool_size=10,  # Idadi ya connection zinazoweza kufanya kazi kwa pamoja
        pool_reset_mode='array',
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=int(DB_PORT)
    )
    print("Database Connection Pool imetengenezwa kwa mafanikio!")
except mysql.connector.Error as err:
    print(f"Kosa kubwa la kutengeneza Pool: {err}")
    db_pool = None

def get_db_connection():
    """
    Kazi ya kurudisha connection moja kutoka kwenye pool ya database.
    Kila unapomaliza kuitumia kwenye Flask (kama kwenye callback au login),
    hakikisha unaita conn.close() ili irudi kwenye pool.
    """
    if db_pool:
        try:
            return db_pool.get_connection()
        except mysql.connector.Error as err:
            print(f"Imeshindwa kuchukua connection kutoka kwenye pool: {err}")
    
    # Njia ya dharura kama pool imefeli kabisa kutengenezwa
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=int(DB_PORT)
    )

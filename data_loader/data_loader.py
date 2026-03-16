import json
import argparse
import sys
import os
from datetime import datetime
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_batch

text = "Load data from JSON file into TimescaleDB database"

parser = argparse.ArgumentParser(description=text)
parser._action_groups.pop()
required = parser.add_argument_group('required arguments')
optional = parser.add_argument_group('optional arguments')

required.add_argument("file_json", help="Input file in json format with the data to be uploaded to the database")
required.add_argument("database", help="Database name to be used to upload the data, with the option -c or --create is created it")
required.add_argument("user", help="Database user, this user is specified in the config file docker-compose.yml")
required.add_argument("password", help="Database password for the user specified in the config file docker-compose.yml")
required.add_argument("host", help="Database host (default: localhost)")
required.add_argument("table", help="Table name to be used to upload the data, if it does not exist it is created")
optional.add_argument("-c", "--create", action='store_true', help="with this option the database is created if it does not exist, this argument is optional")

args = parser.parse_args()

def create_connection(dbname, user, password, host, autocommit=False):
    """Create a PostgreSQL connection"""
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host
        )
        if autocommit:
            # Needed for operations like CREATE DATABASE that cannot run inside a transaction block
            conn.autocommit = True
        return conn
    except psycopg2.Error as e:
        print(f"Unable to connect to database '{dbname}': {e}")
        sys.exit(1)

def check_database_exists(conn, database_name):
    """Check if a database exists"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT datname FROM pg_catalog.pg_database WHERE datname = %s", (database_name,))
        return cursor.fetchone() is not None
    except psycopg2.Error as e:
        print(f"Error checking database existence: {e}")
        return False

def create_database(conn, database_name):
    """Create a database"""
    try:
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database_name)))
        print(f"Database '{database_name}' created")
        return True
    except psycopg2.Error as e:
        if "already exists" in str(e):
            print(f"Database '{database_name}' already exists")
            return True
        else:
            print(f"Error creating database: {e}")
            return False

def check_table_exists(conn, table_name):
    """Check if a table exists"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_type = 'BASE TABLE' 
            AND table_schema = 'public'
            AND table_name = %s
        """, (table_name,))
        return cursor.fetchone() is not None
    except psycopg2.Error as e:
        print(f"Error checking table existence: {e}")
        return False

def create_table(conn, table_name):
    """Create the trucks table"""
    try:
        cursor = conn.cursor()
        create_table_query = sql.SQL("""
            CREATE TABLE {} (
                id SERIAL PRIMARY KEY,
                time DOUBLE PRECISION,
                departureTime TIMESTAMP,
                arrivalTime TIMESTAMP,
                dayOfWeek VARCHAR(10),
                plate VARCHAR(10),
                time_short TIME,
                prediction DOUBLE PRECISION
            )
        """).format(sql.Identifier(table_name))
        
        cursor.execute(create_table_query)
        conn.commit()
        print(f"Table '{table_name}' created")
        return True
    except psycopg2.Error as e:
        print(f"Error creating table: {e}")
        return False

def parse_time_short(arrival_time):
    """Parse arrival time to time_short format (HH:MM:SS)"""
    try:
        if 'T' in arrival_time:
            time_part = arrival_time.split('T')[1]
        else:
            time_part = arrival_time.split(' ')[1]
        
        parts = time_part.split(':')
        if len(parts) >= 2:
            hours = parts[0]
            minutes = parts[1]
            seconds = parts[2] if len(parts) > 2 else '00'
            return f"{hours}:{minutes}:{seconds}"
        return "00:00:00"
    except Exception as e:
        print(f"Error parsing time: {e}")
        return "00:00:00"

def calculate_time_duration(arrival_time, departure_time):
    """Calculate time difference in seconds"""
    try:
        # Replace 'Z' with '+00:00' to handle UTC timezone format explicitly
        arrival_dt = datetime.fromisoformat(arrival_time.replace('Z', '+00:00'))
        departure_dt = datetime.fromisoformat(departure_time.replace('Z', '+00:00'))
        return (departure_dt - arrival_dt).total_seconds()
    except Exception as e:
        print(f"Error calculating time duration: {e}")
        return 0

def load_json_data(file_path):
    """Load and sort JSON data"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            print("ERROR: JSON file must contain an array of objects")
            sys.exit(1)
        
        # Sort data by 'time' (duration) if available, or keep order. default 0 handles missing key.
        data.sort(key=lambda x: x.get('time', 0))
        return data
    except json.JSONDecodeError as e:
        print(f"ERROR in input file. It is not in valid JSON format: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

def insert_data(conn, table_name, data):
    """Insert data into the table"""
    try:
        cursor = conn.cursor()
        
        insert_query = sql.SQL("""
            INSERT INTO {} (time, departureTime, arrivalTime, dayOfWeek, plate, time_short)
            VALUES (%s, %s, %s, %s, %s, %s)
        """).format(sql.Identifier(table_name))
        
        batch_data = []
        print("Inserting data into database...")
        
        for item in data:
            time_short = parse_time_short(item['arrivalTime'])
            # Calculate duration in seconds
            hours = calculate_time_duration(item['arrivalTime'], item['departureTime'])
            
            # Format timestamps for SQL compatibility (removing T separator)
            departure_time = item['departureTime'].replace('T', ' ')
            arrival_time = item['arrivalTime'].replace('T', ' ')
            
            batch_data.append((
                hours,
                departure_time,
                arrival_time,
                item['dayOfWeek'],
                item['plate'],
                time_short
            ))
        
        execute_batch(cursor, insert_query, batch_data)
        conn.commit()
        print(f"Successfully inserted {len(data)} records into '{table_name}'")
        return True
    except psycopg2.Error as e:
        print(f"Error inserting data: {e}")
        conn.rollback()
        return False

def main():
    # Check if input file exists
    if not os.path.exists(args.file_json):
        print(f"ERROR: Input file '{args.file_json}' does not exist")
        sys.exit(1)
    
    # 1. Connect to 'postgres' (default DB) to perform administrative tasks (CREATE DATABASE)
    # First connect to default database for database operations
    default_conn = create_connection("postgres", args.user, args.password, args.host, autocommit=True)
    
    if args.create:
        print("Creating database...")
        if not create_database(default_conn, args.database):
            print("ERROR: Failed to create database")
            sys.exit(1)
    
    # 2. Verify target database exists before proceeding
    # Check if database exists
    if not check_database_exists(default_conn, args.database):
        print(f"ERROR: Database '{args.database}' does not exist")
        default_conn.close()
        sys.exit(1)
    
    default_conn.close()
    
    # 3. Connect to the actual target database
    # Now connect to the target database
    conn = create_connection(args.database, args.user, args.password, args.host)
    
    # 4. Ensure the schema (table) exists
    # Check and create table if needed
    if not check_table_exists(conn, args.table):
        print("Creating table...")
        if not create_table(conn, args.table):
            print("ERROR: Failed to create table")
            conn.close()
            sys.exit(1)
    
    # 5. Load JSON and insert data into the table
    # Load and insert data
    data = load_json_data(args.file_json)
    if not insert_data(conn, args.table, data):
        print("ERROR: Failed to insert data")
        conn.close()
        sys.exit(1)
    
    conn.close()
    print("Data loading completed successfully")

if __name__ == "__main__":
    main()
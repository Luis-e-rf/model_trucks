import json
import collections
import psycopg2
import argparse
import sys

text = "The program extracts data from the database and writes it to a json file.\n"

parser = argparse.ArgumentParser(description=text)
parser._action_groups.pop()
required = parser.add_argument_group('required arguments')
optional = parser.add_argument_group('optional arguments')
required.add_argument("-db", "--database", required=True,
                      nargs=1, help="Database name to consult")
required.add_argument("-u", "--user", required=True, nargs=1,
                      help="User name to connect to the database, this user is specified in the config file docker-compose.yml")
required.add_argument("-p", "--password", required=True, nargs=1,
                      help="Password to connect to the database for the user specified in the config file docker-compose.yml")
required.add_argument("-host", required=True, nargs=1,
                      help="Host to connect to the database")
required.add_argument("-t", "--table", required=True,
                      nargs=1, help="Table name to consult")
optional.add_argument(
    "-o", "--output", nargs='?', help="Output Json File optional parameter, if not specified, the default name is output.json", default="output.json")
args = parser.parse_args()

conn_string = "dbname=" + args.database[0] + " user=" + args.user[0] + \
    " password=" + args.password[0] + " host=" + args.host[0]
try:
    conn = psycopg2.connect(conn_string)
except psycopg2.Error as e:
    print('Unable to connect!\n%s' % e)
    sys.exit(1)
else:
    print("Connection to database successful")
    cursor = conn.cursor()

    print("Extracting data table %s" % args.table[0])
    try:
        cursor.execute("SELECT * FROM %s" % args.table[0])
    except psycopg2.Error as e:
        print('The table does not exist!\n%s' % e)
        sys.exit(1)
    else:
        rows = cursor.fetchall()

        # Convert query to objects of key-value pairs
        objects_list = []
        for row in rows:
            d = collections.OrderedDict()
            d["id"] = row[0]
            d["time"] = row[1]
            d["departureTime"] = row[2]
            d["arrivalTime"] = row[3]
            d["dayOfWeek"] = row[4]
            d["plate"] = row[5]
            d["prediction"] = row[7]
            objects_list.append(d)

        j = json.dumps(objects_list, default=str, indent=7)

        with open(args.output, "w") as f:
            f.write(j)

        print("Data extracted and written to file %s" % args.output)

        conn.close()

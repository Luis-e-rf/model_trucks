# Data extract

<!-- TOC depthfrom:2 -->

- [Description](#description)
- [Requirements](#requirements)
- [Usage](#usage)
- [Example](#example)

<!-- /TOC -->

## Description

The script extracts the data from the database and saves it to a .json file. json file headers are already set.

You can specify through the command line the name of the database, the table and the name of the output file.

## Requirements

Packages required to run the code can be installed as follows:

```
pip install -r requirement.txt
```

## Usage

```
usage: data_extract.py [-h] -db DATABASE -u USER -p PASSWORD -host HOST -t TABLE [-o [OUTPUT]]

The program extracts data from the database and writes it to a json file.

required arguments:
  -db DATABASE, --database DATABASE
                        Database name to consult
  -u USER, --user USER  User name to connect to the database, this user is specified in the config
                        file docker-compose.yml
  -p PASSWORD, --password PASSWORD
                        Password to connect to the database for the user specified in the config
                        file docker-compose.yml
  -host HOST            Host to connect to the database
  -t TABLE, --table TABLE
                        Table name to consult

optional arguments:
  -o [OUTPUT], --output [OUTPUT]
                        Output Json File optional parameter, if not specified, the default name is
                        output.json
```

## Example

Case 1: Extract data from a database and save it to a json file named output_data.json

```
$ python3 data_extract.py -db test_db -u postgres -p password -host localhost -t test_table -o output_data.json
```

Case 2: Extract data from a database and save it to a json file with the default name output.json

```
$ python3 data_extract.py -db test_db -u postgres -p password -host localhost -t test_table
```

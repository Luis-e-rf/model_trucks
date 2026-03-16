# Data loader

<!-- TOC depthfrom:2 -->

- [Requirements](#requirements)
  - [Dependencies](#dependencies)
- [Usage](#usage)
- [Example](#example)

<!-- /TOC -->

## Requirements

### Dependencies

The script requires the following Python libraries:

- `psycopg2-binary`

Run the following command to install the dependencies:

```bash
pip install -r requirements.txt
```

## Usage

```
usage: data_loader.py [-h] [-c] file_json database user password host table

Load data from JSON file into TimescaleDB database

required arguments:
  file_json          Input file in json format with the data to be uploaded
                     to the database
  database           Database name to be used to upload the data, with the
                     option -c or --create is created it
  user               Database user, this user is specified in the config
                     file docker-compose.yml
  password           Database password for the user specified in the config
                     file docker-compose.yml
  host               Database host (default: localhost)
  table              Table name to be used to upload the data, if it does not
                     exist it is created

optional arguments:
  -c, --create       with this option the database is created if it does not
                     exist, this argument is optional
```

## Example

Case 1: Create a database and upload data to it

```
$ python data_loader.py ../data/base_01000_01.json test_db postgres password localhost test_table -c
```

Case 2: Upload data to an existing database

```
$ python data_loader.py ../data/base_01000_01.json test_db postgres password localhost test_table
```

# Data loader

<!-- TOC depthfrom:2 -->

- [Requirements](#requirements)
  - [Dependencies](#dependencies)
- [Usage](#usage)
- [Example](#example)

<!-- /TOC -->

## Requirements

### Dependencies

Run the following commands to install the dependencies:

```
npm install pg
```

```
npm install fs
```

```
npm install pgtools
```

```
npm install commander
```

```
npm install semver
```

```
npm install yargs-parser
```

## Usage

```
Usage: data_loader [options] <file_json> <database> <user> <password> <host> <table>

Arguments:
  file_json     Input file in json format with the data to be uploaded to the database
  database      Database name to be used to upload the data, with the option -c or --create is created it
  user          Database user, this user is specified in the config file docker-compose.yml
  password      Database password for the user specified in the config file docker-compose.yml
  host          Database host (default: localhost)
  table         Table name to be used to upload the data, if it does not exist it is created

Options:
  -c, --create  with this option the database is created if it does not exist, this argument is optional
  -h, --help    display help for command
```

## Example

Case 1: Create a database and upload data to it

```
$ node data_loader.js ../data/base_01000_01.json test_db postgres password localhost test_table -c
```

Case 2: Upload data to an existing database

```
$ node data_loader.js ../data/base_01000_01.json test_db postgres password localhost test_table
```

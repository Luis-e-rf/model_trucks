const pg = require('pg');
var pgtools = require("pgtools");
var fs = require('fs');
var program = require('commander');
const path = require('path');
const resultados = []
const databases = []
const promises = []
const promise_database = []

// Definir parámetros y descripción del contenido del parámetro.
program
  .argument('<file_json>', 'Input file in json format with the data to be uploaded to the database')
  .argument('<database>', 'Database name to be used to upload the data, with the option -c or --create is created it')
  .argument('<user>', 'Database user, this user is specified in the config file docker-compose.yml')
  .argument('<password>', 'Database password for the user specified in the config file docker-compose.yml')
  .argument('<host>', 'Database host (default: localhost)')
  .option('-c, --create', 'with this option the database is created if it does not exist, this argument is optional')
  .argument('<table>', 'Table name to be used to upload the data, if it does not exist it is created')

program.parse(process.argv);

const options = program.args.concat(program.opts())


const connectionData = {
  database: options[1],
  user: options[2],
  password: options[3],
  host: options[4],
}
const config_create = {
  user: options[2],
  password: options[3],
  host: options[4]
};


const cliente = new pg.Client(connectionData);
const cliente_create = new pg.Client(config_create);

async function createDatabase(database) {
  return new Promise((resolve, reject) => {
    pgtools.createdb(config_create, database, (err) => {
      if (err) {
        console.log("¡The database is going to be deleted and created again.!")
        resolve()
      }
      else {
        console.log('Database created')
        resolve()
      }
    })
  })
}

async function deleteDatabase(database) {
  return new Promise((resolve, reject) => {
    pgtools.dropdb(config_create, database, (err) => {
      if (err) {
        console.log("Error deleting database\n\n" + err)
        process.exit()
      } else {
        console.log('Database deleted')
        resolve()
      }
    })
  })
}

async function checkDatabase(database) {
  cliente.connect(err => {
    const query_database = `SELECT datname FROM pg_catalog.pg_database;`
    promise_database.push(cliente.query(query_database).then(result => {
      result.rows.map(row => {
        databases.push(row.datname)
      })
    }).catch(() => {
      if (!databases.includes(database)) {
        console.log('ERROR: Database with this properties not exists')
        process.exit()
      }
    }))
  })
}

async function createTable(file) {
  const query_table = `SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE' AND table_schema = 'public'`;
  cliente.query(query_table).then(result => {
    result.rows.map(row => {
      resultados.push(row.table_name)
    })
    if (!resultados.includes(options[5])) {
      console.log('Creating table...')
      const query_create = `CREATE TABLE ${options[5]}(id SERIAL, time DOUBLE PRECISION, departureTime TIMESTAMP, arrivalTime TIMESTAMP,dayOfWeek VARCHAR(10), plate VARCHAR(10), time_short TIME, prediction DOUBLE PRECISION)`;
      cliente.query(query_create)
        .catch(err => {
          console.log(err)
        })
    }
    dataUploadToTimeScale(file)
  })
}

async function dataUploadToTimeScale(file) {
  FILE_NAME = file;
  let filename = fs.readFileSync(FILE_NAME)
  try {
    let parse_json = JSON.parse(filename)
    sort(parse_json, 'time')



    //console.log(parse_json)
    console.log('Inserting data into database...')
    for (var item in parse_json) {
      var time_short = parse_json[item].arrivalTime.split('T')[1].split(':')
      if (time_short[2] == undefined) {
        time_short[2] = '00'
      }
      var time_short_string = time_short[0] + ':' + time_short[1] + ':' + time_short[2]
      var hours = (Date.parse(parse_json[item].departureTime) - Date.parse(parse_json[item].arrivalTime)) / (1000)
      const query = `INSERT INTO ${options[5]}(id, time, departureTime, arrivalTime, dayOfWeek, plate, time_short) VALUES(DEFAULT, ${hours}, '${(parse_json[item].departureTime).replace("T", " ")}', '${(parse_json[item].arrivalTime).replace("T", " ")}', '${parse_json[item].dayOfWeek}', '${parse_json[item].plate}', '${time_short_string}')`;
      promises.push(cliente.query(query).then(() => {
      }))
    }
    Promise.all(promises).then(() => {
      process.exit()
    })
  }
  catch {
    console.log('ERROR in input file. It is not in JSON format.')
    process.exit()
  }
}

function sort(json, key) {
  json.sort(function (a, b) {
    return a[key] > b[key];
  });
}

if (options.length === 7) {
  if (options[6].create) {
    async function create() {
      console.log('Creating database...')
      await createDatabase(options[1])
      if (createDatabase[options[1]] === undefined) {
        await deleteDatabase(options[1])
        await createDatabase(options[1])
      }
      await checkDatabase(options[1])
      await createTable(options[0])
    }
    if (fs.existsSync(options[0])) {
      cliente_create.connect(err => {
        if (err) {
          if (err.message.includes('password authentication failed')) {
            console.log('ERROR: The user or password is wrong')
            process.exit()
          }
          if (err.code === 'ENOTFOUND') {
            console.log('ERROR: The host is wrong')
            process.exit()
          }
        }
        else {
          create()
        }
      })
    } else {
      console.log('ERROR: Input file ' + options[0] + ' is not a file')
      process.exit()
    }
  } else {
    if (fs.existsSync(options[0])) {
      checkDatabase(options[1])
      cliente.connect(err => {
        if (err) {
          if (err.message.includes('password authentication failed')) {
            console.log('ERROR: The user or password is wrong')
            process.exit()
          }
          if (err.code === 'ENOTFOUND') {
            console.log('ERROR: The host is wrong')
            process.exit()
          }
        }
        else {
          Promise.all(promise_database).then(() => {
            createTable(options[0])
          })
        }
      })
    } else {
      console.log('ERROR: Input file ' + options[0] + ' is not a file')
      process.exit()
    }
  }
}
else {
  console.log('Usage: node data-upload.js <-c> <file.json> <database> <user> <password> <localhost> <table>\n\n<-c> optional argument for create database \n <file.json>: Name of the json format file with the data to load in TimeScale \n<database>: PostgreSQL database name \n<user>: User associated with the database \n<password>: Database password \n<localhost>: Host\n<table>: Table name in the database or name of the table to create')
}
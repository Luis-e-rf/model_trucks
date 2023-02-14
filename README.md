# Truck turnaround time

<!-- TOC depthfrom:2 -->

- [Configuration file docker-compose.yml](#configuration-file-docker-composeyml)
- [Usage](#usage)
- [Example](#example)

<!-- /TOC -->

## Configuration file docker-compose.yml

The archive docker-compose.yml is a configuration file for the docker-compose tool.

The services are:

- `timescaledb`: The database service.
- `grafana`: The service to show the dashboards.

## Usage

Run the following command to start the application:

`docker-compose up -d`

Then you should access the `data_loader` folder where you will find the readme that will indicate the Node JS dependencies that you must install and then run the `data_loader.js` program, in this step you will create a database with the Timescale service and insert some training data.

Then access the grafana service by copying the following url in the browser:

`http://localhost:3000/`

Once you access the address, you must enter the user `admin` and the password `admin`.

Immediately a screen appears to change the password of the `admin` user, this step is optional although it is recommended to do it since when you close the session and re-enter it will ask you again to change the password for a more secure one, then the screen of setting:

![New Password](/config_images/new-password-grafana.png)

Immediately afterwards a message appears A new password can then be set for the `admin` user.

Once this step has been executed, the grafana application can be accessed, and we proceed to create the connection with the database. In the menu on the left, we find the configuration icon and access the `Data sources` option, then click on ` Add data source` .

In the window that appears in the SQL section we select the `PostgreSQL` option.

A new window appears with the necessary fields for the connection, we will configure them as follows:

```
Host: timescaledb:5432
Database: <Database name>
User: postgres
Password: <Se encuentra en el archivo docker-compose.yml cuando levantamos el servicio de dbtimescale> by default: password
TLS/SSL Mode: disable

PostgreSQL details
Version: 12+
TimescaleDB: <prender esta casilla>
```

And after this we click `Save & Test` and we would have correctly configured the connection to the database with grafana.

After this we will access the `data_extract` folder, initially the `readme` file must be read to install some Python libraries that will be used to execute the `data_extract.py` program, this program must be executed `twice` to obtain two JSON files that will be used as data training and evaluation for the next step.

Then access the `c4_5` folder in which initially, as in the previous steps, the readme file should be read, once read and having all the necessary libraries installed, we will execute the program `algoritm_c4_5.py`, which depending on the size of the data will take a few minutes . If everything has been executed well, in this step the data that we extracted in JSON format with the `data_extract.py` program was used and used so that the model learns from this information and allows to generate `predictions` of the time of permanence of the vehicles, once the algorithm generates the predictions, these are loaded automatically to the database that we created with the `data_loader.js` program, all this while the algorithm is running, finally, when the execution is finished, the program generates a file in JSON format with the predictions obtained and other vehicle information.

Finally, we access the `dashboard` folder and we will follow the steps detailed in the readme file to import the dashboard in `JSON` format to grafana, which will be synchronized with the database that we have created and will allow you to view the information with different graphs.

## Example

1. Open the terminal and run the following commands:

```
1. run docker-compose up -d
2. access the data_loader folder and run the dependencies to install the Node JS libraries
3. run the data_loader.js program to create the database and insert the training data
4. access the data_extract folder and run the dependencies to install the Python libraries
5. run the data_extract.py program to extract the data and generate the JSON files
6. access the c4_5 folder and run the dependencies to install the Python libraries
7. run the algoritm_c4_5.py program to generate the predictions.
```

Follow the steps as shown in the image below.

![terminal_example](/config_images/terminal_example.png)

2. Configure the database connection in the grafana application.

```
1.  Open in the browser: http://localhost:3000/
2.  enter the user admin and the password admin
3.  Create the connection with the database as described in the previous section.
4.  access the dashboard folder from the grafana application and import the dashboard in JSON format.
```

If everything has been executed correctly, you will see the last window as shown in the image below. and then click on the `Import` button.

![dashboard](/config_images/import_grafana.png)

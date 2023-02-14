# Algoritmo C4.5

<!-- TOC depthfrom:2 -->

- [Description](#description)
- [Requirements](#requirements)
- [Usage](#usage)
- [Example](#example)

<!-- /TOC -->

## Description

The C4.5 algorithm is a machine learning algorithm that is based on creating a decision tree that fits the characteristics of the input data.

The algorithm calculates the results, write the data in a JSON file and then upload the predictions to the database.

## Requirements

Packages required to run the code can be installed as follows:

```
pip install -r requirements.txt
```

## Usage

```
usage: algoritm_c4_5.py [-h] -i_tra INPUT_TRAINING -i_tst INPUT_TESTING -db DATABASE -u USER -p PASSWORD -host HOST -t TABLE [TABLE ...] [-o [OUTPUT]]
                        [-cr [{squared_error,friedman_mse,absolute_error,poisson}]] [-sp [{best,random}]] [-md [MAX_DEPTH]] [-mss [MIN_SAMPLES_SPLIT]] [-msl [MIN_SAMPLES_LEAF]]
                        [-mwfl [{0.0,0.1,0.2,0.30000000000000004,0.4,0.5}]] [-mf [MAX_FEATURES]] [-rs [RANDOM_STATE]] [-mln [MAX_LEAF_NODES]] [-mid [MIN_IMPURITY_DECREASE]]
                        [-var [{arrivalTime,departureTime,dayOfWeek}]]

The program predicts the estimated time of a vehicle based on the data of JSON file, the model is trained and the results are stored in the database and in a JSON file

required arguments:
  -i_tra INPUT_TRAINING, --input_training INPUT_TRAINING
                        JSON file with the data to be used for the model training.
  -i_tst INPUT_TESTING, --input_testing INPUT_TESTING
                        JSON file with the data to be used for the model testing or evaluation.
  -db DATABASE, --database DATABASE
                        Database name to upload the estimated time or prediction
  -u USER, --user USER  User name to connect to the database, this user is specified in the config file docker-compose.yml
  -p PASSWORD, --password PASSWORD
                        Password to connect to the database for the user specified in the config file docker-compose.yml
  -host HOST            Host to connect to the database
  -t TABLE [TABLE ...], --table TABLE [TABLE ...]
                        Table(s) name to upload the results of the prediction, the correct sintax is: table1 table2 table3. The sintax must not contain commas, only spaces if there
                        are more than one table

optional arguments:
  -o [OUTPUT], --output [OUTPUT]
                        Output JSON file with the prediction results, if not specified the default name is output_data.json.
  -cr [{squared_error,friedman_mse,absolute_error,poisson}], --criterion [{squared_error,friedman_mse,absolute_error,poisson}]
                        Criterion to use in the model, default is squared error
  -sp [{best,random}], --splitter [{best,random}]
                        Splitter to use in the model, default is best
  -md [MAX_DEPTH], --max_depth [MAX_DEPTH]
                        Maximum depth of the tree, default value is None
  -mss [MIN_SAMPLES_SPLIT], --min_samples_split [MIN_SAMPLES_SPLIT]
                        Minimum number of samples required to split an internal node, default value is 2
  -msl [MIN_SAMPLES_LEAF], --min_samples_leaf [MIN_SAMPLES_LEAF]
                        Minimum number of samples required to be at a leaf node, default value is 1
  -mwfl [{0.0,0.1,0.2,0.30000000000000004,0.4,0.5}], --min_weight_fraction_leaf [{0.0,0.1,0.2,0.30000000000000004,0.4,0.5}]
                        The minimum weighted fraction of the sum total of weights (of all the input samples) required to be at a leaf node, default value is 0.0
  -mf [MAX_FEATURES], --max_features [MAX_FEATURES]
                        The number of features to consider when looking for the best split, default value is None
  -rs [RANDOM_STATE], --random_state [RANDOM_STATE]
                        If int, random_state is the seed used by the random number generator; If RandomState instance, random_state is the random number generator; If None, the
                        random number generator is the RandomState instance used by np.random. Default value is None
  -mln [MAX_LEAF_NODES], --max_leaf_nodes [MAX_LEAF_NODES]
                        Maximum number of leaf nodes for a tree, default value is None
  -mid [MIN_IMPURITY_DECREASE], --min_impurity_decrease [MIN_IMPURITY_DECREASE]
                        The minimum impurity decrease required to split an internal node, default value is 0.0
  -var [{arrivalTime,departureTime,dayOfWeek}], --variables [{arrivalTime,departureTime,dayOfWeek}]
                        Variables to be used in the model predict, default value is arrivalTime and departureTime. The sintax must not contain commas, only spaces if there are more
                        than one variable


```

## Example

1. Predict the estimated time of a vehicle based on the data in the data_extract folder and save the results in a json file named output_pred_1000.json

```
python3 algoritm_c4_5.py -i_tra ../data_extract/db_10000_train.json -i_tst ../data_extract/db_1000.json -db test_db -u postgres -p password -host localhost -t test_table train_table -o output_pred_1000.json -cr squared_error -md 95 -mss 8 -var arrivalTime departureTime dayOfWeek
```

2. Predict the estimated time of a vehicle based on the data in the data_extract folder and save the results in a json file with the default name output_data.json

```
python3 algoritm_c4_5.py -i_tra ../data_extract/db_10000_train.json -i_tst ../data_extract/db_1000.json -db test_db -u postgres -p password -host localhost -t test_table train_table
```

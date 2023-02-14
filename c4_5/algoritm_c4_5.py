import pandas as pd
import numpy as np
import argparse
from sklearn.model_selection import GridSearchCV
from sklearn.tree import DecisionTreeRegressor
import psycopg2
import sys

text = "The program predicts the estimated time of a vehicle based on the data of JSON file, the model is trained and the results are stored in the database and in a JSON file"

parser = argparse.ArgumentParser(description=text)
parser._action_groups.pop()
required = parser.add_argument_group('required arguments')
optional = parser.add_argument_group('optional arguments')
required.add_argument("-i_tra", "--input_training", required=True,
                      type=argparse.FileType('r'), help="JSON file with the data to be used for the model training.")
required.add_argument("-i_tst", "--input_testing", required=True, type=argparse.FileType(
    'r'), help="JSON file with the data to be used for the model testing or evaluation.")
required.add_argument("-db", "--database", required=True,
                      nargs=1, help="Database name to upload the estimated time or prediction")
required.add_argument("-u", "--user", required=True, nargs=1,
                      help="User name to connect to the database, this user is specified in the config file docker-compose.yml")
required.add_argument("-p", "--password", required=True, nargs=1,
                      help="Password to connect to the database for the user specified in the config file docker-compose.yml")
required.add_argument("-host", required=True, nargs=1,
                      help="Host to connect to the database")
required.add_argument("-t", "--table", required=True,
                      nargs='+', help="Table(s) name to upload the results of the prediction, the correct sintax is: table1 table2 table3. The sintax must not contain commas, only spaces if there are more than one table")
optional.add_argument(
    "-o", "--output", type=argparse.FileType('w'), nargs='?', help="Output JSON file with the prediction results, if not specified the default name is output_data.json.", default="output_data.json")
optional.add_argument("-cr", "--criterion", nargs='?',
                      help="Criterion to use in the model, default is squared error", default='squared_error', type=str, choices=['squared_error', 'friedman_mse', 'absolute_error', 'poisson'])
optional.add_argument("-sp", "--splitter", nargs='?',
                      help="Splitter to use in the model, default is best", type=str, default='best', choices=['best', 'random'])
optional.add_argument("-md", "--max_depth", nargs='?',
                      help="Maximum depth of the tree, default value is None", default=None, type=int)
optional.add_argument("-mss", "--min_samples_split", nargs='?',
                      help="Minimum number of samples required to split an internal node, default value is 2", default=2, type=int)
optional.add_argument("-msl", "--min_samples_leaf", nargs='?',
                      help="Minimum number of samples required to be at a leaf node, default value is 1", default=1, type=int)
optional.add_argument("-mwfl", "--min_weight_fraction_leaf", nargs='?',
                      help="The minimum weighted fraction of the sum total of weights (of all the input samples) required to be at a leaf node, default value is 0.0", default=0.0, type=float, choices=np.arange(0.0, 0.6, 0.1))


def allow_type_max_features(f):
    # Allow type str or int or float for max_features for argparse
    if f is None:
        return None
    try:
        f = int(f)
    except ValueError:
        try:
            f = float(f)
        except ValueError:
            pass
    return f


optional.add_argument("-mf", "--max_features", nargs='?',
                      help="The number of features to consider when looking for the best split, default value is None", default=None, type=allow_type_max_features)
optional.add_argument("-rs", "--random_state", nargs='?',
                      help="If int, random_state is the seed used by the random number generator; If RandomState instance, random_state is the random number generator; If None, the random number generator is the RandomState instance used by np.random. Default value is None", default=None, type=int)
optional.add_argument("-mln", "--max_leaf_nodes", nargs='?',
                      help="Maximum number of leaf nodes for a tree, default value is None", default=None, type=int)
optional.add_argument("-mid", "--min_impurity_decrease", nargs='?',
                      help="The minimum impurity decrease required to split an internal node, default value is 0.0", default=0.0, type=float)
optional.add_argument("-var", "--variables", nargs='+',
                      help="Variables to be used in the model predict, default value is arrivalTime and departureTime. The sintax must not contain commas, only spaces if there are more than one variable", default=['arrivalTime', 'departureTime'], choices=['arrivalTime', 'departureTime', 'dayOfWeek'])


def convert():
    # args.min_samples_split can be a float if not is integer
    if not isinstance(args.min_samples_split, int):
        args.min_samples_split = float(args.min_samples_split)
    # args.min_samples_leaf can be a float if not is integer
    if not isinstance(args.min_samples_leaf, int):
        args.min_samples_leaf = float(args.min_samples_leaf)
    # args.max_features must be None or int or float or str, if is str it must be 'auto' or 'sqrt' or 'log2', if not is nothing exit
    if args.max_features is not None:
        if not isinstance(args.max_features, int) and not isinstance(args.max_features, float) and args.max_features != 'auto' and args.max_features != 'sqrt' and args.max_features != 'log2':
            print("Error: max_features must be None or int or float or str, if is str it must be 'auto' or 'sqrt' or 'log2', if not is nothing exit")
            sys.exit(1)


args = parser.parse_args()

conn_string = "dbname=" + args.database[0] + " user=" + args.user[0] + \
    " password=" + args.password[0] + " host=" + args.host[0]
try:
    conn = psycopg2.connect(conn_string)
except psycopg2.Error as e:
    print('Unable to connect!\n%s' % e)
    sys.exit(1)
else:
    print("Connected to database")
    # if all tables exists in database continue
    cursor = conn.cursor()
    print("Checking if all tables exists in database")
    print(args.table)
    for table in args.table:
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '" + table + "');")
        if cursor.fetchone()[0] == 0:
            print("Table " + table + " does not exist in database")
            sys.exit(1)
    print("All tables exists in database")
    with args.input_training as f_tra:
        # create df dataframe from json file with the data to be used for the model training
        df_tra = pd.read_json(f_tra)
        df_training = df_tra.sample(frac=1).reset_index(drop=True)
    with args.input_testing as f_tst:
        # create df dataframe from json file with the data to be used for the model testing or evaluation
        df_test = pd.read_json(f_tst)
        df_testing = df_test.sample(frac=1).reset_index(drop=True)
        # We transform the variables str departureTime and arrivalTime to datetime and then separate year, month, day, hour, minute, second
        # df_traning
        df_training['departureTime'] = pd.to_datetime(
            df_training['departureTime'], format='%Y-%m-%d %H:%M:%S')
        df_training['arrivalTime'] = pd.to_datetime(
            df_training['arrivalTime'], format='%Y-%m-%d %H:%M:%S')
        df_training['departureTime_year'] = df_training['departureTime'].dt.year
        df_training['departureTime_month'] = df_training['departureTime'].dt.month
        df_training['departureTime_day'] = df_training['departureTime'].dt.day
        df_training['departureTime_hour'] = df_training['departureTime'].dt.hour
        df_training['departureTime_minute'] = df_training['departureTime'].dt.minute
        df_training['departureTime_second'] = df_training['departureTime'].dt.second
        df_training['arrivalTime_year'] = df_training['arrivalTime'].dt.year
        df_training['arrivalTime_month'] = df_training['arrivalTime'].dt.month
        df_training['arrivalTime_day'] = df_training['arrivalTime'].dt.day
        df_training['arrivalTime_hour'] = df_training['arrivalTime'].dt.hour
        df_training['arrivalTime_minute'] = df_training['arrivalTime'].dt.minute
        df_training['arrivalTime_second'] = df_training['arrivalTime'].dt.second
        # df_testing
        df_testing['departureTime'] = pd.to_datetime(
            df_testing['departureTime'], format='%Y-%m-%d %H:%M:%S')
        df_testing['arrivalTime'] = pd.to_datetime(
            df_testing['arrivalTime'], format='%Y-%m-%d %H:%M:%S')
        df_testing['departureTime_year'] = df_testing['departureTime'].dt.year
        df_testing['departureTime_month'] = df_testing['departureTime'].dt.month
        df_testing['departureTime_day'] = df_testing['departureTime'].dt.day
        df_testing['departureTime_hour'] = df_testing['departureTime'].dt.hour
        df_testing['departureTime_minute'] = df_testing['departureTime'].dt.minute
        df_testing['departureTime_second'] = df_testing['departureTime'].dt.second
        df_testing['arrivalTime_year'] = df_testing['arrivalTime'].dt.year
        df_testing['arrivalTime_month'] = df_testing['arrivalTime'].dt.month
        df_testing['arrivalTime_day'] = df_testing['arrivalTime'].dt.day
        df_testing['arrivalTime_hour'] = df_testing['arrivalTime'].dt.hour
        df_testing['arrivalTime_minute'] = df_testing['arrivalTime'].dt.minute
        df_testing['arrivalTime_second'] = df_testing['arrivalTime'].dt.second

        # create a new column code_dayOfWeek with the day of week str to int
        df_training['code_dayOfWeek'] = df_training['dayOfWeek'].map(
            {'MONDAY': 1, 'TUESDAY': 2, 'WEDNESDAY': 3, 'THURSDAY': 4, 'FRIDAY': 5, 'SATURDAY': 6, 'SUNDAY': 7}).astype(int)
        df_testing['code_dayOfWeek'] = df_testing['dayOfWeek'].map(
            {'MONDAY': 1, 'TUESDAY': 2, 'WEDNESDAY': 3, 'THURSDAY': 4, 'FRIDAY': 5, 'SATURDAY': 6, 'SUNDAY': 7}).astype(int)

        # print some data from the dataframe
        print("JSON file read for training: ", f_tra.name)
        print("JSON file read for testing: ", f_tst.name)
        # Division of the data in train and test, with args.variables as the filtering of the dataframe
        # df_training
        departureTime_train = df_training[['departureTime_year', 'departureTime_month',
                                           'departureTime_day', 'departureTime_hour', 'departureTime_minute', 'departureTime_second']]
        arrivalTime_train = df_training[['arrivalTime_year', 'arrivalTime_month',
                                         'arrivalTime_day', 'arrivalTime_hour', 'arrivalTime_minute', 'arrivalTime_second']]
        dayOfWeek_train = df_training['code_dayOfWeek']
        train_data = []
        # df_testing
        departureTime_test = df_testing[['departureTime_year', 'departureTime_month',
                                         'departureTime_day', 'departureTime_hour', 'departureTime_minute', 'departureTime_second']]
        arrivalTime_test = df_testing[['arrivalTime_year', 'arrivalTime_month',
                                       'arrivalTime_day', 'arrivalTime_hour', 'arrivalTime_minute', 'arrivalTime_second']]
        dayOfWeek_test = df_testing['code_dayOfWeek']
        test_data = []
        for variable in args.variables:
            if variable == 'departureTime':
                train_data.append(departureTime_train)
                test_data.append(departureTime_test)
            elif variable == 'arrivalTime':
                train_data.append(arrivalTime_train)
                test_data.append(arrivalTime_test)
            elif variable == 'dayOfWeek':
                train_data.append(dayOfWeek_train)
                test_data.append(dayOfWeek_test)
            else:
                print("Variable not found")
                sys.exit(1)

        X_train = pd.concat(train_data, axis=1).values
        y_train = df_training['time'].values
        X_test = pd.concat(test_data, axis=1).values
        y_test = df_testing['time'].values

        print("Pruning is applied by cross validation")
        param_grid = {'ccp_alpha': np.linspace(0, 100, 35)}

        print("Cross Validation Search (CCP Alpha parameter in range 0 to 100)")
        model = GridSearchCV(
            # El árbol se crece al máximo posible para luego aplicar el pruning
            estimator=DecisionTreeRegressor(
                criterion=args.criterion,
                splitter=args.splitter,
                max_depth=args.max_depth,
                min_samples_split=args.min_samples_split,
                min_samples_leaf=args.min_samples_leaf,
                min_weight_fraction_leaf=args.min_weight_fraction_leaf,
                max_features=args.max_features,
                random_state=args.random_state,
                max_leaf_nodes=args.max_leaf_nodes,
                min_impurity_decrease=args.min_impurity_decrease,
            ),
            param_grid=param_grid,
            cv=10,
            refit=True,
            return_train_score=True
        )

        # model training
        model.fit(X_train, y_train)
        print("Best ccp_alpha value found: ", model.best_params_)

        # we calculate which were the predictors that best fit the model
        importance_predictors = pd.DataFrame(
            {'predictor': pd.concat(test_data, axis=1).columns,
             'importance': model.best_estimator_.feature_importances_}
        ).sort_values(by='importance', ascending=False)

        print("Importance of predictors in the model")
        print(importance_predictors)
        modelo_pruned = model.best_estimator_

        # Predict the response for the test data set
        y_pred = modelo_pruned.predict(X_test)
        y_pred2 = modelo_pruned.predict(X_train)
        # Join the predictions and create the column based on the matrix
        df_testing['prediction'] = y_pred
        df_training['prediction'] = y_pred2
        # Print the mean square error (MSE) for the training data
        print("MSE Train data: ", np.mean((y_pred2 - y_train) ** 2))
        # Print the mean square error (MSE) for the test data
        print("MSE Test data: ", np.mean((y_pred - y_test) ** 2))
        # Print the coefficient of determination
        print("score: ", modelo_pruned.score(X_test, y_test))
        # We print the number of nodes of the model
        print("Number of nodes: ", modelo_pruned.tree_.node_count)
        # We print the number of leaves of the model
        print("Number of leaves: ", modelo_pruned.tree_.n_leaves)
        # We print the depth of the model
        print("Depth: ", modelo_pruned.tree_.max_depth)
        df_out = pd.concat([df_training, df_testing])
        # restore df_testing dropping the year, month, day, hour, minute, second columns and code_dayOfWeek, also the arrivalTime and departureTime columns are restored to string
        df_testing = df_testing.drop(['departureTime_year', 'departureTime_month', 'departureTime_day', 'departureTime_hour', 'departureTime_minute', 'departureTime_second',
                                      'arrivalTime_year', 'arrivalTime_month', 'arrivalTime_day', 'arrivalTime_hour', 'arrivalTime_minute', 'arrivalTime_second', 'code_dayOfWeek'], axis=1)
        df_testing['departureTime'] = df_testing['departureTime'].astype(str)
        df_testing['arrivalTime'] = df_testing['arrivalTime'].astype(str)
        df_testing.to_json(args.output, orient='records', indent=7)
        print("Open conexion to database to upload the prediction results")
        # upload the prediction results to the database table(s)
        with cursor as cur:
            for table in args.table:
                for index, row in df_out.iterrows():
                    cur.execute(
                        "UPDATE %s SET prediction = %s WHERE id = %s" % (table, row['prediction'], row['id']))
        conn.commit()
        print("Predictions uploaded to the database:\n table(s): ",
              str(args.table) + "\n database: ", args.database[0])
        # close the connection
        conn.close()
        print("Conexión closed to database")
        print("JSON File created: ", args.output.name)
        print("End of the program")
        sys.exit(0)

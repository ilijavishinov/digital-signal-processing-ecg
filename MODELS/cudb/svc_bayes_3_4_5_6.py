#%%
from comet_ml import Experiment, OfflineExperiment
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupShuffleSplit
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from skopt import BayesSearchCV
from skopt import callbacks
from skopt.callbacks import CheckpointSaver
import skopt


ALGORITHM = 'SVC'
DS = 'DS1'

#%%

for SEGMENTS_LENGTH in [3, 4, 5, 6]:

    EXPERIMENT_ID = F'BayesSearch_{ALGORITHM}_{DS}_{SEGMENTS_LENGTH}s'

    data_dir = f'D:\\FINKI\\8_dps\\Project\\DATA\\MODELS_DATA\\{DS}'
    X_train = pd.read_csv(f'{data_dir}\\segments_{SEGMENTS_LENGTH}s_train.csv')
    X_test = pd.read_csv(f'{data_dir}\\segments_{SEGMENTS_LENGTH}s_test.csv')

    y_train = X_train.pop('episode')
    y_test = X_test.pop('episode')

    results = list()
    workflow_dict = dict()

    hyperparameters_optimizer = BayesSearchCV(
        SVC(),
        {
            'C':      (1e-6, 1e+6, 'log-uniform'),
            'gamma':  (1e-6, 1e+1, 'log-uniform'),
            'coef0': (0.0, 10.0, 'uniform'),
            'degree': (1, 3),
            'kernel': ['linear', 'poly', 'rbf'],
            'random_state': [42]
            
        },
        n_iter=50,
        cv=5,
        verbose = 10,
        n_jobs = 2,
        n_points = 2,
        scoring = 'accuracy',
    )

    checkpoint_callback = skopt.callbacks.CheckpointSaver(f'D:\\FINKI\\8_dps\\Project\\MODELS\\skopt_checkpoints\\{EXPERIMENT_ID}.pkl')
    hyperparameters_optimizer.fit(X_train, y_train, callback = [checkpoint_callback])
    skopt.dump(hyperparameters_optimizer, f'saved_models\\{EXPERIMENT_ID}.pkl')

    y_pred = hyperparameters_optimizer.best_estimator_.predict(X_test)

    for i in range(len(hyperparameters_optimizer.cv_results_['params'])):
        exp = OfflineExperiment(
            api_key = 'A8Lg71j9LtIrsv0deBA0DVGcR',
            project_name = ALGORITHM,
            workspace = "8_dps",
            auto_output_logging = 'native',
            offline_directory = f'D:\\FINKI\\8_dps\\Project\\MODELS\\comet_ml_offline_experiments\\{EXPERIMENT_ID}'
        )
        exp.set_name(f'{EXPERIMENT_ID}_{i + 1}')
        exp.add_tags([DS, SEGMENTS_LENGTH, ])
        for k, v in hyperparameters_optimizer.cv_results_.items():
            if k == "params": exp.log_parameters(dict(v[i]))
            else: exp.log_metric(k, v[i])
        exp.end()

        
        
        

import pandas as pd
import numpy as np
import os
from ast import literal_eval
from collections import defaultdict
from collections import Counter
from sklearn.model_selection import KFold, cross_val_predict, cross_validate
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier


def get_features_labels(filename):

    df = pd.read_csv('songs/{}'.format(filename))

    df.singer_ids = df.singer_ids.apply(literal_eval)
    df.songwriter_ids = df.songwriter_ids.apply(literal_eval)
    singers = df.singer_ids.tolist()
    songwriters = df.songwriter_ids.tolist()

    d = defaultdict(dict)

    for singer_ids, songwriter_ids in zip(singers, songwriters):
        for singer_id in singer_ids:
            for songwriter_id in songwriter_ids:
                if not songwriter_id in d[singer_id]:
                    d[singer_id][songwriter_id] = 0
                d[singer_id][songwriter_id] += 1


    df = pd.read_csv('artists/{}'.format(filename), dtype='Int64', usecols=["singer_ids", "is_popular"])
    singers = df.singer_ids.tolist()
    popularities = df.is_popular.tolist()


    for singer_id, popularity in zip(singers, popularities):
        d[singer_id]['popular'] = popularity

    df = pd.DataFrame.from_dict(d, orient='index', dtype='Int64')
    df.fillna(0, inplace=True)


    df = df[[col for col in df if col != 'popular'] + ['popular']]


    data = df.values
    X, y = data[:, :-1], data[:, -1]
    y=y.astype('int')

    return X, y, list(df.columns[:-1])


if __name__ == '__main__':

    results_dir = 'songs/'

    for filename in os.listdir(results_dir):

        X, y, writers = get_features_labels(filename=filename)
        counter = Counter(y)
        print(counter)

        max_f1 = -1
        max_feature_importances = None
        max_scores = None

        for i in range(8,11):

            over = SMOTE(sampling_strategy=i/10)
            X_temp, y_temp = over.fit_resample(X, y)

            counter = Counter(y_temp)
            print(counter)

            cv = KFold(n_splits=5, shuffle=True)
            model = RandomForestClassifier()
            # model = XGBClassifier(use_label_encoder=False)

            scoring = ['accuracy', 'precision', 'recall', 'f1']
            output = cross_validate(model, X_temp, y_temp, cv=cv, n_jobs=-1, scoring=scoring, return_estimator=True)


            for estimator, f1, acc, prec, recall in zip(output['estimator'], output['test_f1'], output['test_accuracy'], output['test_precision'], output['test_recall']):
                if f1 > max_f1:
                    feature_importances = pd.DataFrame(estimator.feature_importances_,
                                                    index = writers,
                                                    columns=['importance']).sort_values('importance', ascending=False)

                    max_feature_importances = feature_importances
                    max_f1 = f1
                    max_scores = (acc, prec, recall, f1)


        max_feature_importances.to_csv('features/{}'.format(filename))
        # print(max_scores)

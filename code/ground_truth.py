import pandas as pd
import numpy as np
from ast import literal_eval
from collections import defaultdict
from collections import Counter
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE


def get_features_labels(genre='Rock'):

    df = pd.read_csv('songs/{}.csv'.format(genre))
    df = df[df.singer_ids != '0']
    df = df[df.songwriter_ids != '0']
    print(df.shape)
    df.singer_ids = df.singer_ids.apply(literal_eval)
    df.songwriter_ids = df.songwriter_ids.apply(literal_eval)
    singers = df.singer_ids.tolist()
    songwriters = df.songwriter_ids.tolist()

    d = defaultdict(dict)

    for singer_ids, songwriter_ids in zip(singers, songwriters):
        for singer_id in singer_ids:
            for songwriter_id in songwriter_ids:
                d[singer_id][songwriter_id] = 1


    df = pd.read_csv('artists/{}.csv'.format(genre), dtype='Int64', usecols=["singer_ids", "is_popular"])
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

    return X, y


if __name__ == '__main__':

    X, y = get_features_labels()
    counter = Counter(y)
    print(counter)

    for i in range(3,11):

        over = SMOTE(sampling_strategy=i/10)
        X_temp, y_temp = over.fit_resample(X, y)

        counter = Counter(y_temp)
        print(counter)

        cv = KFold(n_splits=8, shuffle=True)
        model = RandomForestClassifier()
        y_pred = cross_val_predict(model, X_temp, y_temp, cv=cv, n_jobs=-1)
        CM = confusion_matrix(y_temp, y_pred)

        print('over: {}'.format(i/10), end =" ")
        print('Accuracy: %.3f' % (accuracy_score(y_temp, y_pred)), end =" ")
        print('Precision: %.3f' % (precision_score(y_temp, y_pred)), end =" ")
        print('Recall: %.3f' % (recall_score(y_temp, y_pred)), end =" ")
        print('TN: {0} - FN: {1} - TP: {2} - FP: {3}'.format(str(CM[0][0]), str(CM[1][0]), str(CM[1][1]), str(CM[0][1])))

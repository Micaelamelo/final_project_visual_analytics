from pathlib import Path
from typing import List, Dict
import pandas as pd
import numpy as np
from sklearn import metrics
from sklearn.cluster import KMeans, DBSCAN
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

from d_data_encoding import generate_label_encoder, replace_with_label_encoder
from e_preprocessing import *


def simple_k_means(X: pd.DataFrame, n_clusters=3, score_metric='euclidean') -> Dict:
    model = KMeans(n_clusters=n_clusters)
    clusters = model.fit_transform(X)

    labels = model.labels_
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)

    print(labels)
    print('Estimated number of clusters:', n_clusters)

    # There are many methods of deciding a score of a cluster model. Here is one example:
    score = metrics.silhouette_score(X, model.labels_, metric=score_metric)
    return dict(model=model, score=score, clusters=clusters, labels=labels)


def earthquakes_clustering():
    df = earthquakes_data()
    # df = df[(df['YEAR'] == 2009)]
    print(df.head().to_string())

    le = generate_label_encoder(df['magnitude type'])
    df_le = replace_with_label_encoder(df, 'magnitude type', le)

    ret = simple_k_means(df_le.iloc[:, 3:6])
    print(ret)
    return ret

def wildfires_clustering():
    df = wildfires_data()
    # TEMPORAL FIX
    # df = df[(df['YEAR'] == 1946) | (df['YEAR'] > 2014)]

    print(df.head().to_string())

    le = generate_label_encoder(df['CAUSE'])
    df_le = replace_with_label_encoder(df, 'CAUSE', le)

    ret = simple_k_means(df_le.iloc[:, [7, 8]])
    print(ret)
    return ret


def floods_clustering():
    df = floods_data()
    print(df.head().to_string())

    ret = simple_k_means(df.iloc[:, [4, 5, 6, 7, 9]])
    print(ret)
    return ret


def hurricanes_clustering():
    df = hurricanes_data()
    print(df.head().to_string())

    ret = simple_k_means(df.iloc[:, [4, 5, 6, 7, 9]])
    print(ret)
    return ret


def tornadoes_clustering():
    df = tornadoes_data()
    print(df.head().to_string())

    ret = simple_k_means(df.iloc[:, 12:15])
    print(ret)
    return ret


if __name__ == "__main__":
   # tornadoes_clustering()
   # floods_clustering()
   # hurricanes_clustering()
   # earthquakes_clustering()
   wildfires_clustering()
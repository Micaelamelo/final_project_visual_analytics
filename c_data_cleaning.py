import collections
import pathlib
from typing import Union, Optional
from enum import Enum
from sklearn import preprocessing
from pandas import Series, DataFrame
import numpy as np


##############################################
# Example(s). Read the comments in the following method(s)
##############################################
from b_data_profile import *


class WrongValueNumericRule(Enum):
    MUST_BE_POSITIVE = 0
    MUST_BE_NEGATIVE = 1
    MUST_BE_GREATER_THAN = 2
    MUST_BE_LESS_THAN = 3


class DistanceMetric(Enum):
    EUCLIDEAN = 0
    MANHATTAN = 1


##############################################
# Implement all the below methods
# All methods should be dataset-independent, using only the methods done in the assignment
# so far and pandas/numpy/sklearn for the operations
##############################################
def fix_numeric_wrong_values(df: DataFrame,
                             column: str,
                             must_be_rule: WrongValueNumericRule,
                             must_be_rule_optional_parameter: Optional[float] = None) -> DataFrame:
    # I consider for "Greater than" and "Less than", like "Greater and equals than"  and "Less and equals than"
    # Example 1: "Greater than 1", 1 is not a wrong value
    # Example 2: "Less than 5", 5 is not a wrong value
    df = df.copy()
    values = df[column].values
    index = 0
    for value in values:
        if must_be_rule == WrongValueNumericRule.MUST_BE_GREATER_THAN:
            if value < must_be_rule_optional_parameter:
                df.loc[index, column] = np.nan
        if must_be_rule == WrongValueNumericRule.MUST_BE_LESS_THAN:
            if value > must_be_rule_optional_parameter:
                df.loc[index, column] = np.nan
        if must_be_rule == WrongValueNumericRule.MUST_BE_NEGATIVE:
            if value > 0:
                df.loc[index, column] = np.nan
        if must_be_rule == WrongValueNumericRule.MUST_BE_POSITIVE:
            if value < 0:
                df.loc[index, column] = np.nan
        index = index + 1
    return df


def fix_outliers(df: DataFrame, column: str) -> DataFrame:
    df = df.copy()
    categorical_columns = get_text_categorical_columns(df)
    numeric_columns = get_numeric_columns(df)
    binary_columns = get_binary_columns(df)

    # For numerical columns, I use z-score method, the one we saw at class
    if (column in numeric_columns):
        aux = standardize_column(df[column])
        index = 0
        for value in aux:
            index = index + 1
            if np.abs(value) >= 3: # I use 3 as the threshold
                df.drop([index])

    # For categorical columns I decided to use this personal strategy: If number of occurrences are less than the half of the mean, I remove it
    # However, we have to analyze the problem and see if this is feasible. For example in 'life expectancy years' is not useful to use this
    # because the only categorical column has unique values: the name of each country.
    if column in categorical_columns:
        vc = df[column].value_counts()
        mean = vc.mean()
        to_remove = vc[vc <= (mean / 2)].index
        for rem in to_remove:
            df.drop(df.index[df[column] == rem], inplace=True)

    # For binary columns, I just see if there is one value who is not 0 or 1 and delete it.
    if column in binary_columns:
        to_remove = df[column].apply(lambda x: x != 0 or x != 1).index
        for rem in to_remove:
            df.drop(df.index[df[column] == rem], inplace=True)

    df.reset_index(drop=True)
    return df


def fix_nans(df: DataFrame, column: str) -> DataFrame:
    df = df.copy()
    categorical_columns = get_text_categorical_columns(df)
    numeric_columns = get_numeric_columns(df)
    binary_columns = get_binary_columns(df)
    nan_size = get_column_count_of_nan(df, column)

    # I replace nones with nans
    df = df.fillna(value=np.nan)

    # To fix nans I decided to do this personal strategy: If the number of nans is <= than 10% of the size column, I drop the rows. Otherwise, I will replace the values.
    # This is because after reading some sources. This one helped me a lot: https://towardsdatascience.com/whats-the-best-way-to-handle-nan-values-62d50f738fc
    # I decided to avoid drop data unnecessarily, so if the % of nans is too little I will drop the data. If the % is too big, I will have to replace the values so I will not lost so much data

    if column in numeric_columns:
        mean = df[column].mean()
        df[column] = df[column].fillna(mean)  # replace nan with column mean value

    if (column in categorical_columns) or (column in binary_columns):
        df[column] = df[column].fillna(df[column].value_counts().index[0])  # replace nan with most frequent value

    return df


def normalize_column(df_column: Series) -> Series:
    # Just normalize numeric columns
    if df_column.dtype == np.float64 or df_column.dtype == np.int64:
        max_value = df_column.max()
        min_value = df_column.min()

        if min_value != max_value:
            df_column = (df_column - min_value) / (max_value - min_value)

    return df_column  # If min=max, normalization is undefined so I return the same column


def standardize_column(df_column: Series) -> Series:
    mu = df_column.mean()
    sigma = df_column.std()
    df_column = ((df_column - mu) / sigma)  # I standardize using avg=0 and std=1, the option of [-1,1] was not included
    return df_column


def calculate_numeric_distance(df_column_1: Series, df_column_2: Series, distance_metric: DistanceMetric) -> Series:
    if distance_metric == DistanceMetric.EUCLIDEAN:
        dist = pd.Series((np.sqrt([np.abs((x - y) * (x - y)) for x, y in zip(df_column_1, df_column_2)])), index=df_column_1.index)
    else:
        dist = pd.Series(([np.abs((x - y)) for x, y in zip(df_column_1, df_column_2)]), index=df_column_1.index)

    return dist


def calculate_binary_distance(df_column_1: Series, df_column_2: Series) -> Series:
    return pd.Series(sum(c1 != c2 for c1, c2 in zip(df_column_1, df_column_2)), index=df_column_1.index)

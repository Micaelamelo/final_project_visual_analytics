from pathlib import Path
from typing import List
import pandas as pd
import numpy as np

##############################################
# Implement all the below methods
# All methods should be dataset-independent, using only the methods done in the assignment
# so far and pandas/numpy/sklearn for the operations
##############################################

def get_column_max(df: pd.DataFrame, column_name: str) -> float:
    return df[column_name].max()


def get_column_min(df: pd.DataFrame, column_name: str) -> float:
    return df[column_name].min()


def get_column_mean(df: pd.DataFrame, column_name: str) -> float:
    return df[column_name].mean()


def get_column_count_of_nan(df: pd.DataFrame, column_name: str) -> float:
    return df[column_name].isna().sum()


def get_column_number_of_duplicates(df: pd.DataFrame, column_name: str) -> float:
    return df[column_name].duplicated().sum()


def get_numeric_columns(df: pd.DataFrame) -> List[str]:
    return df.select_dtypes(include='number').columns.tolist()


def get_binary_columns(df: pd.DataFrame) -> List[str]:
    return [col for col in df if (len(df[col].value_counts()) > 0) & all(df[col].value_counts().index.isin([0, 1]))]


def get_text_categorical_columns(df: pd.DataFrame) -> List[str]:
    return df.select_dtypes(include=['category', 'object']).columns.tolist()


def get_datetime_columns(df: pd.DataFrame) -> List[str]:
    return df.select_dtypes(include=[np.datetime64]).columns.tolist()


def get_correlation_between_columns(df: pd.DataFrame, col1: str, col2: str) -> float:
    return df[col1].corr(df[col2], method='pearson')

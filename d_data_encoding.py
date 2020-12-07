from typing import Union, Optional, List
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, OneHotEncoder

def generate_label_encoder(df_column: pd.Series) -> LabelEncoder:
    labelling = LabelEncoder()
    return labelling.fit(df_column)


def generate_one_hot_encoder(df_column: pd.Series) -> OneHotEncoder:
    return OneHotEncoder().fit(df_column.values.reshape(-1, 1))


def replace_with_label_encoder(df: pd.DataFrame, column: str, le: LabelEncoder) -> pd.DataFrame:
    df = df.copy()
    df[column] = le.transform(df[column])
    return df


def replace_with_one_hot_encoder(df: pd.DataFrame, column: str, ohe: OneHotEncoder,
                                 ohe_column_names: List[str]) -> pd.DataFrame:
    df = df.copy()
    col = df[column]
    # I did manually the formatting of columns. I drop the column passed by parameter:
    df.drop(column, inplace=True, axis=1)
    # I get an array of the data encoded
    x = ohe.transform(col.values.reshape(-1, 1)).toarray()
    # I concat the original df to a new dataframe with the data encoded and the names passed by param: ohe_column_names
    df = pd.concat([df, pd.DataFrame(np.column_stack(list(zip(*x))), columns=ohe_column_names)], axis=1)
    return df 


def replace_label_encoder_with_original_column(df: pd.DataFrame, column: str, le: LabelEncoder) -> pd.DataFrame:
    df = df.copy()
    df[column] = le.inverse_transform(df[column])
    return df


def replace_one_hot_encoder_with_original_column(df: pd.DataFrame,
                                                 columns: List[str],
                                                 ohe: OneHotEncoder,
                                                 original_column_name: str) -> pd.DataFrame:
    df = df.copy()
    inverse = ohe.inverse_transform(df[columns])
    # I did manually the formatting of columns, I drop the columns of the encoded data
    df.drop(columns, inplace=True, axis=1)
    # And then I insert a new column with the value of the decoded data
    df.insert(loc=len(df.columns), column=original_column_name, value=inverse)
    return df
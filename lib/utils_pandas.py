import math
import pandas as pd
import numpy as np
from scipy import stats

from utils_math import *



def standardization(df, column_name, custom_mean=None, custom_std=None):
    df_mean = df[column_name].mean()
    df_std = df[column_name].std()
    
    if custom_mean is not None:
        df_mean = custom_mean
    if custom_std is not None:
        df_std = custom_std
        
    df[column_name] = (df[column_name] - df_mean)/df_std
    return df_mean, df_std

def one_hot_encoding(df, column_name, p='none', delete=True):
    pre = column_name
    if p != 'none':
        pre = p

    df = df.join(pd.get_dummies(df[column_name], prefix=pre))
    if delete:
        return df.drop(column_name, axis=1)
    else:
        return df    
    
def remove_outliers(dataset, columns):
    dataset =  dataset[(np.abs(stats.zscore(dataset.loc[:, columns])) <= 3).all(axis=1)]
    return dataset

    
def explore(df, column_name, detect_not_numbers=True, show_info=False):
    global errors
    errors = {'nan': 0}
    if detect_not_numbers:
        result = df[~df[column_name].apply(is_real_number)]
    else:
        result = df[df[column_name].apply(is_real_number)]
        
    if show_info:
        print(result)
        
    return errors
    
def custom_replace(df, column_name: str, method: str, vars: list):
    
    replaced = df.copy()    
    
    replacement = 0
    
    if method == "mean":
        replacement = replaced[replaced[column_name].apply(is_real_number)][column_name].mean()
        # replacement = df.loc[:, df.loc[:, column_name].apply(is_real_number)][column_name].mean()
    elif method == "median":
        replacement = replaced[replaced[column_name].apply(is_real_number)][column_name].median()
        # replacement = df.loc[:, df.loc[:, column_name].apply(is_real_number)][column_name].median()
    elif method == "mode":
        replacement = replaced[replaced[column_name].notna()][column_name].mode()[0]
        # replacement = df.loc[:, df.loc[:, column_name].notna()][column_name].mode()[0]

    map = {key: replacement for key in vars}
    replaced[column_name].replace(map, inplace=True)
    return replaced
    
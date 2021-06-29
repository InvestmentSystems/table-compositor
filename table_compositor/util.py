import numbers

import pandas as pd

import numpy as np


def df_type_to_str(i):
    """
    Convert into simple datatypes from pandas/numpy types
    """
    if isinstance(i, np.bool_):
        return bool(i)
    if isinstance(i, np.int_):
        return int(i)
    if isinstance(i, np.float):
        if np.isnan(i):
            return "NaN"
        elif np.isinf(i):
            return str(i)
        return float(i)
    if isinstance(i, np.uint):
        return int(i)
    if type(i) == bytes:
        return i.decode("UTF-8")
    if isinstance(i, (tuple, list)):
        return str(i)
    if i is pd.NaT:  # not identified as a float null
        return "NaN"
    if isinstance(i, numbers.Number):
        return i

    return str(i)

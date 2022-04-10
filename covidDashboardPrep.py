import pandas as pd
import numpy as np
import datetime as dt
import streamlit as st

DATE        = "Date"
WEEK_DATE   = "Week Date"
SUNDAY      = 6 # Integer the datetime functionaility associates with Sunday
WEEK_START  = "Week Start"

week_start_date = lambda date: date.name if (date.name.weekday() == SUNDAY) else date.name - dt.timedelta(days=date.name.weekday() + 1)

# region Get Week Data
def validDates(data):
    """
    desc
        Calculate what full weeks of data we have and add those to a list of valid days
    params
        data - dataframe to perform operations on
    return 
        start_week_list - list of the starting Sunday's
        day_list - list of days that belong to a full week of data
    """

    day_list = data.copy()
    day_list = pd.to_datetime(data.columns).to_frame(name=DATE)

    day_list[WEEK_START] = day_list.apply(week_start_date, axis=1)
    day_list = day_list.groupby([WEEK_START]).count()

    # Create a list of week dates
    day_list = day_list[day_list[DATE] == 7]
    day_list = day_list.reset_index()
    day_list = day_list.drop([DATE], axis=1)
    
    start_week_list = day_list[WEEK_START].to_list()
    day_list = pd.to_datetime(data.columns.array)

    return start_week_list, day_list

def trimDays(data, day_list):
    """
    desc
        Trims days from given dataframe that do not belong to a full week.
    params
        data - dataframe to perform operations on
    return 
        data - the dataframe with the given dates removed
    """
    first_day = day_list[0].weekday()
    last_index = len(day_list) - 1
    last_day = day_list[last_index].weekday()

    removeFromStart = SUNDAY - first_day
    removeFromBack =  (2 + last_day) % 7
    removeFromBack = len(day_list) - removeFromBack

    removeFromBack = np.arange(removeFromBack, len(day_list))
    data = data.drop(data.columns[removeFromBack], axis=1)

    removeFromStart = np.arange(0, removeFromStart)
    data = data.drop(data.columns[removeFromStart], axis=1)

    return data

def weeklySumsPerCounty(data, start_week_list):
    """
    desc
        Calculates a summation of data gathered by week for each county
    params
        data - dataframe with days of data
        start_week_list - list of days that represent the start of a week 
    return 
        weekly - the dataframe with every week grouped together with a cumulative
                 subtraction peformed
    """
    m = len(data.columns)

    # Subtract each column from the column previous prior
    for i in reversed(range(m)):
        if(i != 0):
            data.iloc[:, i] = data.iloc[:, i] - data.iloc[:, i-1]
            data.iloc[:, i] = data.iloc[:, i].clip(0)

    # Groups columns in blocks of 7 and sums their contents
    data = data.groupby([i//7 for i in range(0, m)], axis = 1).sum()
    # Restore the names of the columns
    data.columns = start_week_list

    return data

def totalWeeklySums(total_weekly, start_week_list, var_data, id_var, new_label):
    """
    desc
        Calculates a summation of data for each week
    params
        total_weekly - Calculated total for each 
        start_week_list - list of the starting Sunday's
        var_data - variable data to be used in the melting process
        id_var - ID variable to perform melt with 
        new_label - label for the new column to be created
    returns
        weekly - the dataframe with every week grouped together with a cumulative
                 subtraction peformed
    """
    total_weekly[id_var] = var_data
    total_weekly = total_weekly.melt(id_vars=[id_var], value_vars=start_week_list, var_name=DATE, value_name=new_label)
    total_weekly = total_weekly.drop([id_var], axis = 1)
    total_weekly = total_weekly.groupby([DATE]).sum()

    return total_weekly

def scrubData(raw_data, data, id_label):
    """
    desc
        removes data less than 0 in the specified ID label in the data frame
    params
        data - dataframe to perform operations on
        id_label - the id to replace to be checked for the less than 0 condition
    return 
        data - the dataframe with only values greater than 0 for given the ID label
    """
    data[id_label] = raw_data[id_label]
    data = data[data[id_label] > 0]
    data.index = data[id_label]
    data = data.drop([id_label], axis=1)

    return data

# region Q3, Q4 per capita calculations
# Using Plotly Choropleth map produce a map of the USA displaying for each county the new 
# cases of and deaths from, covid per 100,000 people in a week.
def calculatePerCapita(data, pop_data, capita_guidelines=100000):
    """
    desc
        Calculates per capita measurement 
    params
        data - dataframe to perform operations on
        pop_data - dataframe containing population data
        capita_guidelines - the calculations to be made per capita default to 100,000
    return 
        data - the dataframe with the per capita calculations performed
    """
    data.index = pop_data.index
    data = (data * (capita_guidelines))
    data = data.div(pop_data, axis=0).fillna(0)
    data = data.astype('int64')
    return data
# endregion

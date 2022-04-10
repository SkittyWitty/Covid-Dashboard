import pandas as pd
import numpy as np
import datetime as dt
import streamlit as st


STATE       = "State"
COUNTY_NAME = "County Name"
STATE_ID    = "StateFIPS"
COUNTY_ID   = "countyFIPS"
POPULATION  = "population"
DATE        = "Date"
WEEK_DATE   = "Week Date"
FIPS        = "fips"

SUNDAY = 6 # Integer the datetime functionaility associates with Sunday
WEEK_START = "Week Start"
CAPITA_GUIDELINES = 100000

# Common Functions
county_id_transform = lambda row: "0" + row[COUNTY_ID] if (len(row[COUNTY_ID]) == 4) else row[COUNTY_ID]
week_start_date = lambda date: date.name if (date.name.weekday() == SUNDAY) else date.name - dt.timedelta(days=date.name.weekday() + 1)

# region Get Week Data
def validDates(data):
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

def weeklySumsPerCounty(new_weekly, start_week_list):
    m = len(new_weekly.columns)

    for i in reversed(range(m)):
        if(i != 0):
            new_weekly.iloc[:, i] = new_weekly.iloc[:, i] - new_weekly.iloc[:, i-1]
            new_weekly.iloc[:, i] = new_weekly.iloc[:, i].clip(0)

    new_weekly = new_weekly.groupby([i//7 for i in range(0, m)], axis = 1).sum()
    new_weekly.columns = start_week_list

    return new_weekly

def totalWeeklySums(total_weekly, start_week_list, replace_data, replace_id, new_label):
    total_weekly[replace_id] = replace_data
    total_weekly = total_weekly.melt(id_vars=[replace_id], value_vars=start_week_list, var_name=DATE, value_name=new_label)
    total_weekly = total_weekly.drop([replace_id], axis = 1)
    total_weekly = total_weekly.groupby([DATE]).sum()

    return total_weekly

def scrubUnallocated(raw_data, data):
    data[COUNTY_ID] = raw_data[COUNTY_ID]
    data = data[data[COUNTY_ID] > 0]
    data.index = data[COUNTY_ID]
    data = data.drop([COUNTY_ID], axis=1)

    return data

# region Q3
# Using Plotly Choropleth map produce a map of the USA displaying for each county the new 
# cases of covid per 100,000 people in a week. Display the data as a color in each county. An 
# example is below. You need to pick a color scale that is appropriate for the data.
@st.experimental_memo
def getMap(data, CAPITA_GUIDELINES, label, pop):

    # Merge in Counties total population. Calculate cases per capita guidelines.
    data["meh"] = (data["cases"] * CAPITA_GUIDELINES) / data[POPULATION]
    
    return data
# endregion

import streamlit as st
import pandas as pd
import datetime as dt
from covidDashboardPrep import validDates, trimDays

# imports to support opening and reading USA county geojson data
from urllib.request import urlopen
import json

# Constants
PATH = "./"
SUNDAY = 6 # Integer the datetime functionaility associates with Sunday
CAPITA_GUIDELINES = 100000

# Column Labels
STATE       = "State"
COUNTY_NAME = "County Name"
STATE_ID    = "StateFIPS"
COUNTY_ID   = "countyFIPS"
POPULATION  = "population"
DATE        = "Date"
WEEK_DATE   = "Week Date"
FIPS        = "fips"

# Load in all datasets
confirmed_cases = pd.read_csv(PATH + "covid_confirmed_usafacts.csv")
deaths          = pd.read_csv(PATH + "covid_deaths_usafacts.csv")
# General population numbers of each county in the USA
county_population = pd.read_csv(PATH + "covid_county_population_usafacts.csv")

# Get counties where feature.id is the FIPS Code
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

# Common Functions
# A week is defined as starting on Sunday and ending on Saturday
week_start = lambda row: row[DATE] if (row[DATE].weekday() == SUNDAY) else row[DATE] - dt.timedelta(days=row[DATE].weekday() + 1)
county_id_transform = lambda row: "0" + row[COUNTY_ID] if (len(row[COUNTY_ID]) == 4) else row[COUNTY_ID]

# Prepare data for processing
new_weekly_cases = confirmed_cases.drop([COUNTY_ID, COUNTY_NAME, STATE, STATE_ID], axis=1)

# Retrieve a list of dates for week starts and days in the data
start_week_list, all_days_list = validDates(new_weekly_cases)
new_weekly_cases = trimDays(new_weekly_cases, all_days_list)


# region Q1
# Produce a line plot of the weekly new cases of Covid-19 in the USA from the
# start of the pandemic. Weeks start on Sunday and end on Saturday. 
# Only include full weeks
m = len(new_weekly_cases.columns)
new_weekly_cases = new_weekly_cases.groupby([i//7 for i in range(0, m)], axis = 1).sum()

for i in new_weekly_cases.columns:
    if(i != 0):
        new_weekly_cases[i] = new_weekly_cases[i] - new_weekly_cases[i-1]
        new_weekly_cases[i] = new_weekly_cases[i].clip(0)

st.write(new_weekly_cases)

new_weekly_cases.columns = start_week_list
new_weekly_cases[COUNTY_ID] = confirmed_cases[COUNTY_ID]
new_weekly_cases = new_weekly_cases.melt(id_vars=[COUNTY_ID], value_vars=start_week_list, var_name=DATE, value_name="cases")
new_weekly_cases = new_weekly_cases.drop([COUNTY_ID], axis = 1)
new_weekly_cases = new_weekly_cases.groupby([DATE]).sum()
# endregion

# region Display Data
st.title("COVID Dashboard")
st.write(new_weekly_cases)

# Display Q1
st.write("New Weekly Cases Trend")
st.line_chart(new_weekly_cases)

# Display Q2

# Display Q3

# Display Q4

# endregion

st.button("Re-run")
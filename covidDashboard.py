import streamlit as st
import pandas as pd
import datetime as dt
from covidDashboardPrep import calculateWeeklySum, validDates, trimDays

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

# region Q1
# Produce a line plot of the weekly new cases of Covid-19 in the USA from the
# start of the pandemic. Weeks start on Sunday and end on Saturday. Only include full weeks

# Retrieve a list of dates for week starts and days in the data
new_weekly_cases = confirmed_cases.drop([COUNTY_ID, COUNTY_NAME, STATE, STATE_ID], axis=1)
start_week_list, all_days_list = validDates(new_weekly_cases)
new_weekly_cases = trimDays(new_weekly_cases, all_days_list)
new_weekly_cases = calculateWeeklySum(new_weekly_cases, start_week_list, confirmed_cases[COUNTY_ID], COUNTY_ID, "Cases")
# endregion

# region Q2
# Produce a line plot of the weekly deaths due to Covid-19 in the USA from the
# start of the pandemic. Weeks start on Sunday and end on Saturday. Only include full weeks.
new_weekly_deaths = deaths.drop([COUNTY_ID, COUNTY_NAME, STATE, STATE_ID], axis=1)
start_week_list, all_days_list = validDates(new_weekly_deaths)
new_weekly_deaths = trimDays(new_weekly_deaths, all_days_list)
new_weekly_deaths = calculateWeeklySum(new_weekly_deaths, start_week_list, deaths[COUNTY_ID], COUNTY_ID, "Deaths")
# endregion


# region Display Data
st.title("COVID Dashboard")

# Display Q1
st.write("New Weekly Cases Trend")
#st.write(new_weekly_cases)
st.line_chart(new_weekly_cases)

# Display Q2
st.write("Weekly Deaths Trend")
#st.write(new_weekly_deaths)
st.line_chart(new_weekly_deaths)

# Display Q3

# Display Q4

# endregion

st.button("Re-run")
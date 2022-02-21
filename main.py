import streamlit as st
import pandas as pd
import datetime as dt
import numpy as np

st.title("COVID Dashboard")

# Load in all datasets
PATH = "./"

confirmed_cases  = pd.read_csv(PATH + "covid_confirmed_usafacts.csv")
county_population = pd.read_csv(PATH + "covid_county_population_usafacts.csv")
deaths = pd.read_csv(PATH + "covid_deaths_usafacts.csv")

# Column Labels
STATE = "State"
COUNTY_NAME = "County Name"
STATE_ID = "StateFIPS"
COUNTY_ID = "countyFIPS"

# View the dataframes

# Q1: Produce a line plot of the weekly new cases of Covid-19 in the USA from the
# start of the pandemic. Weeks start on Sunday and end on Saturday. 
# Only include full weeks

# Q2 Produce a line plot of the weekly deaths due to Covid-19 in the USA from the
# start of the pandemic. Weeks start on Sunday and end on Saturday.
# Only include full weeks.
dates = deaths.keys()
SUNDAY = 6 # Integer the datetime functionaility associates with Sunday

# Will sum all columns that have numeric values
death_sum = deaths.sum(axis=0, numeric_only=True) # is now a series
death_sum = death_sum.drop([COUNTY_ID, STATE_ID])
death_sum = death_sum.to_frame().reset_index()
death_sum = death_sum.rename(columns={"index":"Date", 0:"Total Deaths"})
death_sum["Date"] = pd.to_datetime(death_sum["Date"])
st.write(death_sum)

# Want to groupby to get the sum for the entire week
week_start = lambda row: row["Date"] if (row["Date"].weekday() == SUNDAY) else row["Date"] - dt.timedelta(days=row["Date"].weekday() + 1)
death_sum["Week Date"] = death_sum.apply(week_start, axis=1)

st.write(death_sum)

#st.write(monday - dt.timedelta(days=monday.weekday() + 1))

# Goal is to convert Wednesday to Sunday

# Notes:
# Use st.write to view raw data

# Take into account that some days may be missed?
# Find a date range from Sunday to Saturday (dates need to be mapped to days)




# Streamlit widgets automatically run the script from top to bottom. Since
# this button is not connected to any other logic, it just causes a plain
# rerun.
st.button("Re-run")
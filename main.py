import streamlit as st
import pandas as pd
import datetime as dt
import numpy as np

# Load in all datasets
PATH = "./"

confirmed_cases  = pd.read_csv(PATH + "covid_confirmed_usafacts.csv")
county_population = pd.read_csv(PATH + "covid_county_population_usafacts.csv")
deaths = pd.read_csv(PATH + "covid_deaths_usafacts.csv")

# Column Labels
STATE       = "State"
COUNTY_NAME = "County Name"
STATE_ID    = "StateFIPS"
COUNTY_ID   = "countyFIPS"

# Constants
SUNDAY = 6 # Integer the datetime functionaility associates with Sunday

# Begin displaying data
st.title("COVID Dashboard")

# region Q1
# Produce a line plot of the weekly new cases of Covid-19 in the USA from the
# start of the pandemic. Weeks start on Sunday and end on Saturday. 
# Only include full weeks

# Will sum all columns that have numeric values
new_case_sum = confirmed_cases.sum(axis=0, numeric_only=True) # is now a series
new_case_sum = new_case_sum.drop([COUNTY_ID, STATE_ID])
new_case_sum = new_case_sum.to_frame().reset_index()
new_case_sum = new_case_sum.rename(columns={"index":"Date", 0:"Total Cases"})
new_case_sum["Date"] = pd.to_datetime(new_case_sum["Date"])

# Label each row with what week they belong to 
# A week is defined as starting on Sunday and ending on Saturday
week_start = lambda row: row["Date"] if (row["Date"].weekday() == SUNDAY) else row["Date"] - dt.timedelta(days=row["Date"].weekday() + 1)
new_case_sum["Week Date"] = new_case_sum.apply(week_start, axis=1)

# Cut out weeks that do not have the full 7 days accounted for
week_day_count = new_case_sum.groupby(["Week Date"]).count()
label_list = week_day_count[week_day_count["Date"] < 7].index.tolist()

new_case_sum = new_case_sum.groupby(["Week Date"]).sum()
new_case_sum = new_case_sum.drop(label_list)

st.write("New Weekly Cases")
st.line_chart(new_case_sum)
#endregion

# region Q2
# Produce a line plot of the weekly deaths due to Covid-19 in the USA from the
# start of the pandemic. Weeks start on Sunday and end on Saturday.
# Only include full weeks.

# Will sum all columns that have numeric values
death_sum = deaths.sum(axis=0, numeric_only=True) # is now a series
death_sum = death_sum.drop([COUNTY_ID, STATE_ID])
death_sum = death_sum.to_frame().reset_index()
death_sum = death_sum.rename(columns={"index":"Date", 0:"Total Deaths"})
death_sum["Date"] = pd.to_datetime(death_sum["Date"])

# Label each row with what week they belong to 
# A week is defined as starting on Sunday and ending on Saturday
week_start = lambda row: row["Date"] if (row["Date"].weekday() == SUNDAY) else row["Date"] - dt.timedelta(days=row["Date"].weekday() + 1)
death_sum["Week Date"] = death_sum.apply(week_start, axis=1)

# Cut out weeks that do not have the full 7 days accounted for
week_day_count = death_sum.groupby(["Week Date"]).count()
label_list = week_day_count[week_day_count["Date"] < 7].index.tolist()

death_sum = death_sum.groupby(["Week Date"]).sum()
death_sum = death_sum.drop(label_list)

st.write("Weekly Deaths")
st.line_chart(death_sum)
#endregion

# region Q3
# end region


# Notes:
# Use st.write to view raw data



# Streamlit widgets automatically run the script from top to bottom. Since
# this button is not connected to any other logic, it just causes a plain
# rerun.
st.button("Re-run")
import streamlit as st
import pandas as pd
import datetime as dt
import plotly.express as px
import plotly

# imports to support opening and reading USA county geojson data
from urllib.request import urlopen
import json

# Constants
PATH = "./"
SUNDAY = 6 # Integer the datetime functionaility associates with Sunday

# Column Labels
STATE       = "State"
COUNTY_NAME = "County Name"
STATE_ID    = "StateFIPS"
COUNTY_ID   = "countyFIPS"
POPULATION  = "population"
DATE = "Date"
WEEK_DATE = "Week Date"
FIPS = "fips"

# Load in all datasets
confirmed_cases = pd.read_csv(PATH + "covid_confirmed_usafacts.csv")
deaths          = pd.read_csv(PATH + "covid_deaths_usafacts.csv")
# General population numbers of each county in the USA
county_population = pd.read_csv(PATH + "covid_county_population_usafacts.csv")


# Common Functions
# A week is defined as starting on Sunday and ending on Saturday
week_start = lambda row: row[DATE] if (row[DATE].weekday() == SUNDAY) else row[DATE] - dt.timedelta(days=row[DATE].weekday() + 1)
county_id_tranfrom = lambda row: "0" + row[COUNTY_ID] if (len(row[COUNTY_ID]) == 4) else row[COUNTY_ID]

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
new_case_sum = new_case_sum.rename(columns={"index":DATE, 0:"Total Cases"})
new_case_sum[DATE] = pd.to_datetime(new_case_sum[DATE])

# Label each row with what week they belong to 
new_case_sum["Week Date"] = new_case_sum.apply(week_start, axis=1)

# Cut out weeks that do not have the full 7 days accounted for
week_day_count = new_case_sum.groupby(["Week Date"]).count()
new_case_short_weeks = week_day_count[week_day_count[DATE] < 7].index.tolist()
new_case_weeks = week_day_count[week_day_count[DATE] == 7].index.tolist()

new_case_sum = new_case_sum.groupby(["Week Date"]).sum()
new_case_sum = new_case_sum.drop(new_case_short_weeks)

# st.write("New Weekly Cases")
# st.line_chart(new_case_sum)
#endregion

# region Q2
# Produce a line plot of the weekly deaths due to Covid-19 in the USA from the
# start of the pandemic. Weeks start on Sunday and end on Saturday.
# Only include full weeks.

# Will sum all columns that have numeric values
death_sum = deaths.sum(axis=0, numeric_only=True) # is now a series
death_sum = death_sum.drop([COUNTY_ID, STATE_ID])
death_sum = death_sum.to_frame().reset_index()
death_sum = death_sum.rename(columns={"index":DATE, 0:"Total Deaths"})
death_sum[DATE] = pd.to_datetime(death_sum[DATE])
# Label each row with what week they belong to 
death_sum["Week Date"] = death_sum.apply(week_start, axis=1)

# Cut out weeks that do not have the full 7 days accounted for
week_day_count = death_sum.groupby(["Week Date"]).count()
label_list = week_day_count[week_day_count[DATE] < 7].index.tolist()

death_sum = death_sum.groupby(["Week Date"]).sum()
death_sum = death_sum.drop(label_list)

# st.write("Weekly Deaths")
# st.line_chart(death_sum)
#endregion

# region Q3
# Using Plotly Choropleth map produce a map of the USA displaying for each county the new 
# cases of covid per 100,000 people in a week. Display the data as a color in each county. An 
# example is below. You need to pick a color scale that is appropriate for the data.

# Get counties where feature.id is the FIPS Code
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

# Goal Data
# Week (Sunday Date)| County | Number of new cases that week / 100,000 | County's total population (will give input on the color the county should be)
weekly_county_cases = confirmed_cases.drop([COUNTY_NAME, STATE, STATE_ID], axis=1)
weekly_county_cases = weekly_county_cases[weekly_county_cases[COUNTY_ID] > 0] # Removing State Unallocated areas unable to properly render on map

# For now let's work with a subset of counties !!!!!!!!!!!!
weekly_county_cases = weekly_county_cases[(weekly_county_cases[COUNTY_ID] < 7000)]

# Adding a "0" to COUNTY_ID's that are too short
weekly_county_cases[COUNTY_ID] = weekly_county_cases[COUNTY_ID].astype(str)
weekly_county_cases[COUNTY_ID] = weekly_county_cases.apply(county_id_tranfrom, axis=1)

dates = weekly_county_cases.keys().tolist()
dates.remove(COUNTY_ID) # removing County FIPS from the list
week_day_count = death_sum.groupby([WEEK_DATE]).count()

# If county FIPS only has 4 characters add a "0" to the beginning
weekly_county_cases = weekly_county_cases.melt(id_vars=[COUNTY_ID], value_vars=dates, var_name=DATE, value_name="cases")
weekly_county_cases[DATE] = pd.to_datetime(weekly_county_cases[DATE])

# Maybe here the user can select a week from the previous list of weeks that have been calculated
# We can backwards calculate the days for that week.
# Than select 

# Calculating the week start date of each date
weekly_county_cases[WEEK_DATE] = weekly_county_cases.apply(week_start, axis=1) # This function takes forever

# Retain Week Date and County FIPS. Summing over all cases that have the same week date
weekly_county_cases = weekly_county_cases.groupby([COUNTY_ID, WEEK_DATE]).sum()

# Remove short weeks
weekly_county_cases = weekly_county_cases.drop(index=new_case_short_weeks, level=1)
weekly_county_cases = weekly_county_cases.reset_index()
week_dates = list(dict.fromkeys(weekly_county_cases[WEEK_DATE]))

# per 100,000 people
weekly_county_cases["cases"] = weekly_county_cases["cases"].floordiv(100000)

# Create dictionary of all choropleth's
meh = []
for i in range(len(week_dates)):
    test_date = week_dates[i]
    test_thing = weekly_county_cases[weekly_county_cases[WEEK_DATE] == test_date]
    meh.append(
        dict(type='choropleth',
             locations = test_thing[COUNTY_ID],
             z=test_thing["cases"],
             geojson=counties))

meh[0]

# Slider using all the possible weeks to select from
steps = []
for i in range(len(week_dates)):
    step = dict(method='restyle',
                args=['visible', [False] * len(week_dates)],
                label=week_dates[i].strftime("%B %d, %Y"))
    step['args'][1][i] = True
    steps.append(step)


slider = [dict(active=0,
                pad={"t": 1},
                steps=steps)]    
layout = dict(title ='Meh', 
                geo=dict(scope='usa', projection={'type': 'albers usa'}),
                sliders=slider)
  
fig = dict(data=meh, 
           layout=layout)
plotly.offline.iplot(fig)


# end region


# Streamlit widgets automatically run the script from top to bottom. Since
# this button is not connected to any other logic, it just causes a plain
# rerun.
st.button("Re-run")
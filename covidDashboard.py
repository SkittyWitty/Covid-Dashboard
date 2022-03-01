import streamlit as st
import pandas as pd
import datetime as dt
import plotly.express as px

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
new_case_week_day_count = new_case_sum.groupby([WEEK_DATE]).count()

new_case_short_weeks = new_case_week_day_count[new_case_week_day_count[DATE] < 7].index.tolist()
new_case_valid_weeks = new_case_week_day_count[new_case_week_day_count[DATE] == 7].index.to_pydatetime().tolist()

new_case_sum = new_case_sum.groupby([WEEK_DATE]).sum()
new_case_sum = new_case_sum.drop(new_case_short_weeks)

st.write("New Weekly Cases Trend")
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
death_sum = death_sum.rename(columns={"index":DATE, 0:"Total Deaths"})
death_sum[DATE] = pd.to_datetime(death_sum[DATE])
# Label each row with what week they belong to 
death_sum["Week Date"] = death_sum.apply(week_start, axis=1)

# Cut out weeks that do not have the full 7 days accounted for
death_week_day_count = death_sum.groupby(["Week Date"]).count()
death_short_weeks = death_week_day_count[death_week_day_count[DATE] < 7].index.tolist()
death_valid_weeks = death_week_day_count[death_week_day_count[DATE] == 7].index.tolist()

death_sum = death_sum.groupby(["Week Date"]).sum()
death_sum = death_sum.drop(death_short_weeks)

st.write("Weekly Deaths Trend")
st.line_chart(death_sum)
#endregion

# region Prepare County Population Data
county_population = county_population.drop([COUNTY_NAME, STATE], axis=1)
county_population[COUNTY_ID] = county_population[COUNTY_ID].astype(str)
county_population[COUNTY_ID] = county_population.apply(county_id_transform, axis=1)
# endregion

# region Q3
# Using Plotly Choropleth map produce a map of the USA displaying for each county the new 
# cases of covid per 100,000 people in a week. Display the data as a color in each county. An 
# example is below. You need to pick a color scale that is appropriate for the data.
@st.experimental_memo
def get_cases(week):
    dates = pd.date_range(week, periods=7).strftime("%Y-%m-%d").tolist()
    col_list = dates
    col_list.append(COUNTY_ID)

    # Goal Data
    # County | Week (Sunday Date) | Number of cases that week per capita
    weekly_county_cases = confirmed_cases.drop([COUNTY_NAME, STATE, STATE_ID], axis=1)
    weekly_county_cases = weekly_county_cases[weekly_county_cases[COUNTY_ID] > 0] # Removing State Unallocated areas unable to properly render on map

    # If county FIPS only has 4 characters add a "0" to the beginning
    weekly_county_cases[COUNTY_ID] = weekly_county_cases[COUNTY_ID].astype(str)
    weekly_county_cases[COUNTY_ID] = weekly_county_cases.apply(county_id_transform, axis=1)

    weekly_county_cases = weekly_county_cases.melt(id_vars=[COUNTY_ID], value_vars=dates, var_name=DATE, value_name="cases")
    weekly_county_cases[DATE] = pd.to_datetime(weekly_county_cases[DATE], format="%Y-%m-%d")

    # Calculating the week start date of each date
    weekly_county_cases[WEEK_DATE] = weekly_county_cases.apply(week_start, axis=1) # This function takes forever

    # Retain Week Date and County FIPS. Summing over all cases that have the same week date
    weekly_county_cases = weekly_county_cases.groupby([COUNTY_ID, WEEK_DATE]).sum()
    weekly_county_cases = weekly_county_cases.reset_index()

    # Merge in Counties total population. Calculate cases per capita guidelines.
    weekly_county_cases = weekly_county_cases.merge(county_population, how='left', on=COUNTY_ID)
    weekly_county_cases["cases"] = (weekly_county_cases["cases"] * CAPITA_GUIDELINES) / weekly_county_cases[POPULATION]
    
    return weekly_county_cases
#endregion


# region Q4
# Using Plotly Choropleth map produce a map of the USA displaying for each county the 
# covid deaths per 100,000 people in a week. Display the data as a color in each county.
@st.experimental_memo
def get_deaths(week):
    dates = pd.date_range(week, periods=7).strftime("%Y-%m-%d").tolist()
    col_list = dates
    col_list.append(COUNTY_ID)

    # Goal Data
    # County | Week (Sunday Date) | Number of deaths that week per capita
    weekly_deaths = deaths[col_list]
    weekly_deaths = weekly_deaths[weekly_deaths[COUNTY_ID] > 0] # Removing State Unallocated areas unable to properly render on map
    
    # If county FIPS only has 4 characters add a "0" to the beginning
    weekly_deaths[COUNTY_ID] = weekly_deaths[COUNTY_ID].astype(str)
    weekly_deaths[COUNTY_ID] = weekly_deaths.apply(county_id_transform, axis=1)
    
    weekly_deaths = weekly_deaths.melt(id_vars=[COUNTY_ID], value_vars=dates, var_name=DATE, value_name="deaths")
    weekly_deaths[DATE] = pd.to_datetime(weekly_deaths[DATE], format="%Y-%m-%d")
    
    # Calculating the week start date of each date
    weekly_deaths[WEEK_DATE] = weekly_deaths.apply(week_start, axis=1) # This function takes forever

    # Retain Week Date and County FIPS. Summing over all cases that have the same week date
    weekly_deaths = weekly_deaths.groupby([COUNTY_ID, WEEK_DATE]).sum()
    weekly_deaths = weekly_deaths.reset_index()

    # Merge in Counties total population. Calculate deaths per capita guidelines.
    weekly_deaths = weekly_deaths.merge(county_population, how='left', on=COUNTY_ID)
    weekly_deaths["deaths"] = (weekly_deaths["deaths"] * CAPITA_GUIDELINES) / weekly_deaths[POPULATION]
    
    return weekly_deaths
#endregion

# region Q5 & Q6
# Map and Slider Constants
FIRST_WEEK = new_case_valid_weeks[0]
NUMBER_OF_WEEKS = len(new_case_valid_weeks) - 1
LAST_WEEK = new_case_valid_weeks[NUMBER_OF_WEEKS]
DATE_SAVE_FORMAT = "%Y-%m-%d"

def new_cases_map(week):
    # Prepare DateTime of week to be used for filtering and displaying
    week = week.replace(hour=0, minute=0, second=0)
    week_formatted = week.strftime(DATE_SAVE_FORMAT)
    week_case = get_cases(week_formatted)

    figure = px.choropleth(week_case, title="New Cases per 100,000",
    geojson=counties, locations=COUNTY_ID,
                                color='cases',
                                color_continuous_scale="amp",
                                range_color=[0, CAPITA_GUIDELINES],
                                scope="usa",
                                labels={'cases':'Cases per 100k'})
    figure.update_layout(title_text="New Cases Recorded on Week: " + week_formatted)
    return figure

def death_map(week):
    # Prepare DateTime of week to be used for filtering and displaying
    week = week.replace(hour=0, minute=0, second=0)
    week_formatted = week.strftime(DATE_SAVE_FORMAT)
    week_case = get_deaths(week_formatted)

    # Building map figure
    figure = px.choropleth(week_case, title="Death's per 100,000",
    geojson=counties, locations=COUNTY_ID,
                                color='deaths',
                                color_continuous_scale="amp",
                                range_color=[0, 5000],
                                scope="usa",
                                labels={'deaths':'Deaths per 100k'})
    figure.update_layout(title_text="Deaths Recorded on Week: " + week_formatted)
    return figure

with st.spinner('Fetching a new map'):
    cases_map_location = st.empty()
    death_map_location = st.empty()

with st.form("Compute_Values"):
    week = st.slider(
        label='Please select a week.',
        value=FIRST_WEEK,
        min_value=FIRST_WEEK,
        step=pd.Timedelta("7 days"),
        max_value=LAST_WEEK,
        format="YYYY-MM-DD")
    submitted = st.form_submit_button("Update Figure")

if st.button("Auto Play"):
    for week in new_case_valid_weeks:
        death_map_location.plotly_chart(death_map(week))
        cases_map_location.plotly_chart(new_cases_map(week))
else:
    cases_map_location.plotly_chart(new_cases_map(week))
    death_map_location.plotly_chart(death_map(week))
# endregion


# Streamlit widgets automatically run the script from top to bottom. Since
# this button is not connected to any other logic, it just causes a plain
# rerun.
st.button("Re-run")
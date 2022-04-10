import streamlit as st
import pandas as pd
from covidDashboardPrep import calculatePerCapita, scrubUnallocated, weeklySumsPerCounty, totalWeeklySums, validDates, trimDays
import plotly.express as px

# imports to support opening and reading USA county geojson data
from urllib.request import urlopen
import json

# Constants
PATH = "./"

# Column Labels
STATE       = "State"
COUNTY_NAME = "County Name"
STATE_ID    = "StateFIPS"
COUNTY_ID   = "countyFIPS"
POPULATION  = "population"
DATE        = "Date"
WEEK_DATE   = "Week Date"
FIPS        = "fips"
DEATHS      = "Deaths"
CASES       = "Cases"

CAPITA_GUIDELINES = 100000

# Common Functions
county_id_transform = lambda meh: "0" + meh if (len(meh)) == 4 else meh

# Load in all datasets
confirmed_cases     = pd.read_csv(PATH + "covid_confirmed_usafacts.csv")
deaths              = pd.read_csv(PATH + "covid_deaths_usafacts.csv")
county_population   = pd.read_csv(PATH + "covid_county_population_usafacts.csv")

# Get counties where feature.id is the FIPS Code
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

# region Q1
# Produce a line plot of the weekly new cases of Covid-19 in the USA from the
# start of the pandemic. Weeks start on Sunday and end on Saturday. Only include full weeks

# Retrieve a list of dates for week starts and days in the data
new_weekly_cases_per_county = confirmed_cases.drop([COUNTY_ID, COUNTY_NAME, STATE, STATE_ID], axis=1)
start_week_list, all_days_list = validDates(new_weekly_cases_per_county)

new_weekly_cases_per_county = trimDays(new_weekly_cases_per_county, all_days_list)
new_weekly_cases_per_county = weeklySumsPerCounty(new_weekly_cases_per_county, start_week_list)

new_weekly_cases = new_weekly_cases_per_county.copy()
new_weekly_cases = totalWeeklySums(new_weekly_cases, start_week_list, confirmed_cases[COUNTY_ID], COUNTY_ID, CASES)
# endregion

# region Q2
# Produce a line plot of the weekly deaths due to Covid-19 in the USA from the
# start of the pandemic. Weeks start on Sunday and end on Saturday. Only include full weeks.
new_weekly_deaths_per_county = deaths.drop([COUNTY_ID, COUNTY_NAME, STATE, STATE_ID], axis=1)

new_weekly_deaths_per_county = trimDays(new_weekly_deaths_per_county, all_days_list)
new_weekly_deaths_per_county = weeklySumsPerCounty(new_weekly_deaths_per_county, start_week_list)

new_weekly_deaths = new_weekly_deaths_per_county.copy()
new_weekly_deaths = totalWeeklySums(new_weekly_deaths, start_week_list, deaths[COUNTY_ID], COUNTY_ID, DEATHS)
# endregion

# region Prepare County Population Data
county_population = county_population.drop([COUNTY_NAME, STATE], axis=1)
county_population = county_population[county_population[COUNTY_ID] > 0]
county_population = county_population[county_population[POPULATION] > 0]

county_population = county_population.astype({COUNTY_ID : str})
county_population.index = county_population[COUNTY_ID].apply(county_id_transform)
county_population = county_population.drop(COUNTY_ID, axis=1)
# endregion

# region Display Data
st.title("COVID Dashboard")

# Display Q1
st.write("New Weekly Cases Trend")
weekly_cases_per_capita = scrubUnallocated(confirmed_cases, new_weekly_cases_per_county, COUNTY_ID)
weekly_cases_per_capita = calculatePerCapita(weekly_cases_per_capita, county_population[POPULATION], CAPITA_GUIDELINES)
st.write(weekly_cases_per_capita)
st.line_chart(new_weekly_cases)

# Display Q2
st.write("Weekly Deaths Trend")
weekly_deaths_per_capita = scrubUnallocated(deaths, new_weekly_deaths_per_county, COUNTY_ID)
weekly_deaths_per_capita = calculatePerCapita(weekly_cases_per_capita, county_population[POPULATION], CAPITA_GUIDELINES)
st.line_chart(new_weekly_deaths)

#region Display Choropleth
def get_map(week, data, title, label, max_range):
    week_case = data[week]
    st.write(week_case)
    # Building map figure
    figure = px.choropleth(week_case,
    geojson=counties, locations=data.index,
                                color=week,
                                color_continuous_scale="amp",
                                range_color=[0, max_range],
                                scope="usa",
                                labels={str(week):label})
    figure.update_layout(title_text=title + " week of " + str(week))
    return figure

FIRST_WEEK = start_week_list[0]
LAST_WEEK = start_week_list[len(start_week_list) - 1]

with st.spinner('Fetching a new map'):
    cases_map_location = st.empty()
    death_map_location = st.empty()

with st.form("Compute_Values"):
    week = st.select_slider(
        label='Please select a week.',
        options=start_week_list)
    submitted = st.form_submit_button("Update Figure")

if st.button("Auto Play"):
    for week in start_week_list:
        cases_map_location.plotly_chart(get_map(week, weekly_cases_per_capita, "Cases's per 100,000", "Cases per 100k", CAPITA_GUIDELINES))
        death_map_location.plotly_chart(get_map(week, weekly_deaths_per_capita,"Death's per 100,000", "Deaths per 100k", CAPITA_GUIDELINES))
else:
    cases_map_location.plotly_chart(get_map(week, weekly_cases_per_capita, "Cases's per 100,000", "Cases per 100k", CAPITA_GUIDELINES))
    death_map_location.plotly_chart(get_map(week, weekly_deaths_per_capita, "Death's per 100,000", "Deaths per 100k", CAPITA_GUIDELINES))

# endregion

st.button("Re-run")
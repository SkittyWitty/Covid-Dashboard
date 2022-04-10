import streamlit as st
import pandas as pd
import datetime as dt
from covidDashboardPrep import county_id_transform, getMap, scrubUnallocated, weeklySumsPerCounty, totalWeeklySums, validDates, trimDays

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
new_weekly_cases = totalWeeklySums(new_weekly_cases, start_week_list, confirmed_cases[COUNTY_ID], COUNTY_ID, "Cases")
# endregion

# region Q2
# Produce a line plot of the weekly deaths due to Covid-19 in the USA from the
# start of the pandemic. Weeks start on Sunday and end on Saturday. Only include full weeks.
new_weekly_deaths_per_county = deaths.drop([COUNTY_ID, COUNTY_NAME, STATE, STATE_ID], axis=1)

new_weekly_deaths_per_county = trimDays(new_weekly_deaths_per_county, all_days_list)
new_weekly_deaths_per_county = weeklySumsPerCounty(new_weekly_deaths_per_county, start_week_list)

new_weekly_deaths = new_weekly_deaths_per_county.copy()
new_weekly_deaths = totalWeeklySums(new_weekly_deaths, start_week_list, deaths[COUNTY_ID], COUNTY_ID, "Deaths")
# endregion

# region Prepare County Population Data
county_population = county_population.drop([COUNTY_NAME, STATE], axis=1)
county_population = county_population[county_population[COUNTY_ID] > 0]
county_population = county_population[county_population[POPULATION] > 0]
# endregion

# region Display Data
st.title("COVID Dashboard")

# Display Q1
st.write("New Weekly Cases Trend")
#st.write(new_weekly_cases)
new_weekly_cases_per_county = scrubUnallocated(confirmed_cases, new_weekly_cases_per_county)
st.write(new_weekly_cases_per_county)
st.line_chart(new_weekly_cases)

# Display Q2
st.write("Weekly Deaths Trend")
#st.write(new_weekly_deaths)
new_weekly_deaths_per_county = scrubUnallocated(deaths, new_weekly_deaths_per_county)
st.write(new_weekly_deaths_per_county)
st.line_chart(new_weekly_deaths)


# Display Choropleth
# def death_map(week):
#     # Prepare DateTime of week to be used for filtering and displaying
#     week = week.replace(hour=0, minute=0, second=0)
#     week_formatted = week.strftime(DATE_SAVE_FORMAT)
#     week_case = get_deaths(week_formatted)

#     # Building map figure
#     figure = px.choropleth(week_case, title="Death's per 100,000",
#     geojson=counties, locations=COUNTY_ID,
#                                 color='deaths',
#                                 color_continuous_scale="amp",
#                                 range_color=[0, 5000],
#                                 scope="usa",
#                                 labels={'deaths':'Deaths per 100k'})
#     figure.update_layout(title_text="Deaths Recorded on Week: " + week_formatted)
#     return figure

with st.spinner('Fetching a new map'):
    cases_map_location = st.empty()
    death_map_location = st.empty()

# with st.form("Compute_Values"):
#     week = st.slider(
#         label='Please select a week.',
#         value=start_week_list[0],
#         min_value=FIRST_WEEK,
#         step=pd.Timedelta("7 days"),
#         max_value=LAST_WEEK,
#         format="YYYY-MM-DD")
#     submitted = st.form_submit_button("Update Figure")

# if st.button("Auto Play"):
#     for week in new_case_valid_weeks:
#         death_map_location.plotly_chart(death_map(week))
#         cases_map_location.plotly_chart(new_cases_map(week))
# else:
#     cases_map_location.plotly_chart(new_cases_map(week))
#     death_map_location.plotly_chart(death_map(week))


# region Q3
#getMap(start_week_list, new_weekly_cases_per_county)
#getMap(deaths_start_week_list, new_weekly_deaths_per_county)
# endrgion

# Display Q4

# endregion

st.button("Re-run")
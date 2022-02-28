import streamlit as st
import pandas as pd
import datetime as dt
import plotly.express as px
from PIL import Image

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
# Get counties where feature.id is the FIPS Code
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)


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

# region Q3
# Using Plotly Choropleth map produce a map of the USA displaying for each county the new 
# cases of covid per 100,000 people in a week. Display the data as a color in each county. An 
# example is below. You need to pick a color scale that is appropriate for the data.
@st.experimental_memo
def get_cases():
    # Goal Data
    # County | Week (Sunday Date) | Number of new cases that week / 100,000
    weekly_county_cases = confirmed_cases.drop([COUNTY_NAME, STATE, STATE_ID], axis=1)
    weekly_county_cases = weekly_county_cases[weekly_county_cases[COUNTY_ID] > 0] # Removing State Unallocated areas unable to properly render on map
    
    # Adding a "0" to COUNTY_ID's that are too short
    weekly_county_cases[COUNTY_ID] = weekly_county_cases[COUNTY_ID].astype(str)
    weekly_county_cases[COUNTY_ID] = weekly_county_cases.apply(county_id_tranfrom, axis=1)

    dates = weekly_county_cases.keys().tolist()
    dates.remove(COUNTY_ID) # removing County FIPS from the list

    # If county FIPS only has 4 characters add a "0" to the beginning
    weekly_county_cases = weekly_county_cases.melt(id_vars=[COUNTY_ID], value_vars=dates, var_name=DATE, value_name="cases")
    weekly_county_cases[DATE] = pd.to_datetime(weekly_county_cases[DATE], format="%Y-%m-%d")

    # Calculating the week start date of each date
    weekly_county_cases[WEEK_DATE] = weekly_county_cases.apply(week_start, axis=1) # This function takes forever

    # Retain Week Date and County FIPS. Summing over all cases that have the same week date
    weekly_county_cases = weekly_county_cases.groupby([COUNTY_ID, WEEK_DATE]).sum()

    # Remove short weeks
    weekly_county_cases = weekly_county_cases.drop(index=new_case_short_weeks, level=1)
    weekly_county_cases = weekly_county_cases.reset_index()

    # per 100,000 people
    weekly_county_cases["cases"] = weekly_county_cases["cases"].divide(100000)
    return weekly_county_cases
#endregion


# region Q4
# Using Plotly Choropleth map produce a map of the USA displaying for each county the 
# covid deaths per 100,000 people in a week. Display the data as a color in each county.
@st.experimental_memo
def get_deaths():
    # Goal Data
    # County | Week (Sunday Date) | Number of deaths that week / 100,000
    weekly_deaths = deaths.drop([COUNTY_NAME, STATE, STATE_ID], axis=1)
    weekly_deaths = weekly_deaths[weekly_deaths[COUNTY_ID] > 0] # Removing State Unallocated areas unable to properly render on map

    # Adding a "0" to COUNTY_ID's that are too short
    weekly_deaths[COUNTY_ID] = weekly_deaths[COUNTY_ID].astype(str)
    weekly_deaths[COUNTY_ID] = weekly_deaths.apply(county_id_tranfrom, axis=1)

    dates = weekly_deaths.keys().tolist()
    dates.remove(COUNTY_ID) # removing County FIPS from the list

    # If county FIPS only has 4 characters add a "0" to the beginning
    weekly_deaths = weekly_deaths.melt(id_vars=[COUNTY_ID], value_vars=dates, var_name=DATE, value_name="deaths")
    weekly_deaths[DATE] = pd.to_datetime(weekly_deaths[DATE], format="%Y-%m-%d")

    # Calculating the week start date of each date
    weekly_deaths[WEEK_DATE] = weekly_deaths.apply(week_start, axis=1) # This function takes forever

    # Retain Week Date and County FIPS. Summing over all cases that have the same week date
    weekly_deaths = weekly_deaths.groupby([COUNTY_ID, WEEK_DATE]).sum()

    # Remove short weeks
    weekly_deaths = weekly_deaths.drop(index=new_case_short_weeks, level=1)
    weekly_deaths = weekly_deaths.reset_index()
    
    # per 100,000 people
    weekly_deaths["deaths"] = weekly_deaths["deaths"].divide(100000)
    return weekly_deaths
#endregion


# region Q5 & Q6
# Slider
FIRST_WEEK = new_case_valid_weeks[0]
NUMBER_OF_WEEKS = len(new_case_valid_weeks) - 1
LAST_WEEK = new_case_valid_weeks[NUMBER_OF_WEEKS]
DATE_SAVE_FORMAT = "%Y-%m-%d"

weekly_county_cases = get_cases()
weekly_deaths = get_deaths()

if "images" not in st.session_state:
    #Should read in existing images if any otherwise empty dictionary
    st.session_state.images = dict()

if "auto_play" not in st.session_state:
    st.session_state.week = FIRST_WEEK
    st.session_state.count = 0
    st.session_state.auto_play = False

@st.experimental_memo
def new_cases_map(week):
    week = week.replace(hour=0, minute=0, second=0)
    week_formatted = week.strftime(DATE_SAVE_FORMAT)
    week_case = weekly_county_cases[weekly_county_cases[WEEK_DATE] == week]

    fig = px.choropleth(week_case, title="New Cases per 100,000",
    geojson=counties, locations=COUNTY_ID,
                                color='cases',
                                color_continuous_scale="viridis",
                                range_color=[0, 1.0],
                                scope="usa",
                                labels={'cases':'Cases per 100k'})
    fig.update_layout(title_text="New Cases Week: " + week_formatted)
    meh = "D:/Users/kawii/uni/BigData-CS649/Covid-Dashboard/images/new_cases_maps/" + week_formatted + ".png"
    st.session_state.images[week_formatted] = meh
    fig.write_image(file=meh)
    return fig

@st.experimental_memo
def death_map(week):
    week = week.replace(hour=0, minute=0, second=0)
    week_formatted = week.strftime(DATE_SAVE_FORMAT)
    week_case = weekly_deaths[weekly_deaths[WEEK_DATE] == week]

    fig = px.choropleth(week_case, title="Death's per 100,000",
    geojson=counties, locations=COUNTY_ID,
                                color='deaths',
                                color_continuous_scale="viridis",
                                range_color=[0, 1.0],
                                scope="usa",
                                labels={'cases':'Cases per 100k'})
    fig.update_layout(title_text="Deaths Week: " + week_formatted)
    return fig


with st.form("Compute_Values"):
        if st.session_state.auto_play and st.session_state.count < NUMBER_OF_WEEKS:
            st.session_state.auto_play = True
            st.session_state.count += 1
            st.session_state.week = new_case_valid_weeks[st.session_state.count]
        else:
            st.session_state.auto_play = False
            st.session_state.week = FIRST_WEEK
            st.session_state.count = 0
# Maybe wrap entire slider into a function call
        week = st.slider(
                label='What week is it?',
                value=st.session_state.week,
                min_value=FIRST_WEEK,
                step=pd.Timedelta("7 days"),
                max_value=LAST_WEEK,
                format="YYYY-MM-DD")
        submitted = st.form_submit_button("Update Figure")
        with st.spinner('Fetching a new map'):
                st.plotly_chart(new_cases_map(week))
                st.plotly_chart(death_map(week))


def auto_play_on():
    st.session_state.auto_play = True

st.button("Auto Play", on_click=auto_play_on)
# endregion


# Streamlit widgets automatically run the script from top to bottom. Since
# this button is not connected to any other logic, it just causes a plain
# rerun.
st.button("Re-run")
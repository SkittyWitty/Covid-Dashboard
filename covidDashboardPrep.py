import pandas as pd
import numpy as np
import datetime as dt


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
# endregion
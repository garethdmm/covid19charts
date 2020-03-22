from delorean import parse

pop = {
    'Nunavut': 3594,
    'Alberta': 4067175,
    'Saskatchewan': 1098352,
    'Yukon': 3587,
    'Manitoba': 1278365,
    'British Columbia': 4648055,
    'Ontario': 13448494,
    'Quebec': 8164361,
    'Prince Edward Island': 142907,
    'Newfoundland and Labrador': 519716,
    'Northwest Territories': 41786,
    'Nova Scotia': 923598,
    'New Brunswick': 747101,
}

def format_data(raw_data):
    formatted_data = raw_data.drop(columns=[
        'Lat',
        'Long',
    ])

    formatted_data = formatted_data.rename(columns={
        'Country/Region': 'region',
        'Province/State': 'subregion',
    })

    return formatted_data


def subregion_timeseries(subregion_name, raw_data):
    subregion_data = raw_data[raw_data['Province/State'] == subregion_name]

    subregion_data = subregion_data.drop(columns=[
        'Lat',
        'Long',
        'Country/Region',
        'Province/State',
    ])

    return subregion_data


def get_canada(raw_data):
    canada = raw_data[raw_data.region == 'Canada']\
        .drop(columns=['region'])\
        .set_index('subregion')

    cols = [
        parse(t, dayfirst=False, yearfirst=False).datetime.replace(tzinfo=None)
        for t in canada.columns
    ]                                                              

    canada.columns = cols

    return canada

def get_daily_change_in_region(region):
    return region - region.shift(1, axis=1)


def get_new_data_for_province(subregion, raw_data, per_capita=False, per_thousand=False):
    formatted_data = format_data(raw_data)
    canada = get_canada(formatted_data)
    subregion_data = canada.T[subregion]

    for timestamp, value in canada.T.Quebec.items():
        formatted_timestamp = str(int(timestamp.strftime('%s'))*1000)

        if per_capita is True:
            value = value / pop[subregion]

        if per_thousand is True:
            value = value * 1000 / pop[subregion]

        print('[%s,%.5f],' % (int(timestamp.strftime('%s'))*1000, value))









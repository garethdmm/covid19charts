from delorean import parse
import pandas as pd

shortcodes = {
    'Alberta': 'AB',
    'Saskatchewan': 'SK',
    'Manitoba': 'MB',
    'British Columbia': 'BC',
    'Ontario': 'ON',
    'Quebec': 'QC',
    'Prince Edward Island': 'PE',
    'Newfoundland and Labrador': 'NL',
    'Nova Scotia': 'NS',
    'New Brunswick': 'NB',
    'Nunavut': 'NU',
    'Yukon': 'YK',
    'Northwest Territories': 'NT',
}

pop = {
    'Alberta': 4067175,
    'Saskatchewan': 1098352,
    'Manitoba': 1278365,
    'British Columbia': 4648055,
    'Ontario': 13448494,
    'Quebec': 8164361,
    'Prince Edward Island': 142907,
    'Newfoundland and Labrador': 519716,
    'Nova Scotia': 923598,
    'New Brunswick': 747101,
    # No data for these presently.
    #'Nunavut': 3594,
    #'Yukon': 3587,
    #'Northwest Territories': 41786,
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


def generate_new_data_js():
    raw_data = pd.read_csv('data/current.csv')
    datajs = generate_new_data_js_string(raw_data)
    f = open('website/js/data.js', 'w')
    f.write(datajs)
    f.close()


def generate_new_data_js_string(raw_data):
    data_js = ''

    for province in pop.keys():
        province_total_str = generate_new_data_js_string_for_province(
            province,
            raw_data,
        )

        province_perthousand_str = generate_new_data_js_string_for_province(
            province,
            raw_data,
            per_thousand=True,
        )

        data_js += province_total_str + '\n\n'
        data_js += province_perthousand_str + '\n\n'

    return data_js


def generate_new_data_js_string_for_province(subregion, raw_data, per_capita=False, per_thousand=False):
    formatted_data = format_data(raw_data)
    canada = get_canada(formatted_data)
    subregion_data = canada.T[subregion]

    variable_name = '%s_total' % shortcodes[subregion].lower()

    if per_thousand:
        variable_name = '%s_per_thousand' % shortcodes[subregion].lower()

    data = ''

    for timestamp, value in canada.T[subregion].items():
        formatted_timestamp = str(int(timestamp.strftime('%s'))*1000)

        if per_capita is True:
            value = value / pop[subregion]

        if per_thousand is True:
            value = value * 1000 / pop[subregion]

        data = data + ('\n  [%s,%.5f],' % (int(timestamp.strftime('%s'))*1000, value))

    data = '%s = [%s\n];' % (variable_name, data)

    return data


if __name__ == '__main__':
    generate_new_data_js()


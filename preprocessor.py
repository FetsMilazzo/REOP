from datetime import datetime
from geopy.geocoders import GoogleV3


def process(arrivals_df, runway_info_df, gate_nodes_df, actype_df, weather_df):
    touchdown_df = extract_touchdown(arrivals_df)
    runway_assign_df = assign_runway_info(touchdown_df, runway_info_df)
    node_assign_df = assign_nodes(runway_assign_df, gate_nodes_df)
    actype_assign_df = assign_categories(node_assign_df, actype_df)
    weather_assign_df = assign_weather(actype_assign_df, weather_df)
    return weather_assign_df


def extract_touchdown(arrivals_df):
    split_pos = [i.split('|')[0] for i in arrivals_df.positions]
    touchdown_lat = [float(i.split(';')[0]) for i in split_pos]
    touchdown_long = [float(i.split(';')[1]) for i in split_pos]
    touchdown_epoch = [float(i.split(';')[2]) for i in split_pos]

    touchdown_date, touchdown_hour = convert_epoch(
        touchdown_lat,
        touchdown_long,
        touchdown_epoch)

    prelim_df = arrivals_df.assign(
        date=touchdown_date,
        hour=touchdown_hour,
        touchdownLat=touchdown_lat,
        touchdownLong=touchdown_long)

    result_df = prelim_df.drop('positions', axis=1)
    return result_df


def convert_epoch(touchdown_lat, touchdown_long, touchdown_epoch):
    google_geo_api = GoogleV3()
    airport_tz = google_geo_api.timezone((touchdown_lat[0], touchdown_long[0]))

    dt = [datetime.fromtimestamp(int(i*0.001), airport_tz)
          for i in touchdown_epoch]

    date = [f'{i.month}.{i.day}.{i:%y}' for i in dt]
    hour = [int(f'{i.hour}') for i in dt]
    return date, hour


def assign_runway_info(touchdown_pos_df, runway_info_df):
    prelim_df = touchdown_pos_df.merge(touchdown_pos_df.merge(
        runway_info_df,
        how='inner',
        on='runway',
        sort=False))

    result_df = prelim_df.rename(
        columns={'arrGate': 'gate', 'lat': 'runwayLat', 'long': 'runwayLong'})
    return result_df


def assign_nodes(runway_assign_df, gate_nodes_df):
    result_df = runway_assign_df.merge(runway_assign_df.merge(
        gate_nodes_df,
        how='inner',
        on='gate',
        sort=False))
    return result_df


def assign_categories(node_assign_df, actype_df):
    prelim_df = node_assign_df.merge(node_assign_df.merge(
        actype_df,
        how='outer',
        on='aircraftType',
        sort=False))

    prelim_df.category.fillna('GA', inplace=True)
    result_df = prelim_df.dropna()
    return result_df


# (Weather isn't getting used yet in any calculations for the LP)
def assign_weather(actype_assign_df, weather_df):
    prelim_df = actype_assign_df.merge(actype_assign_df.merge(
        weather_df,
        how='inner',
        on=['date', 'hour'],
        sort=False))

    prelim_df['Wind Speed (mph):'] *= 5280 / 6076  # mph to knots
    result_df = prelim_df.rename(
        columns={'Wind Speed (mph):': 'Wind Speed (knots)'})
    return result_df

import pandas as pd


def cleanse(data_files, airport):
    input_df = import_relevant_cols(data_files)
    clean_df = remove_nulls(input_df)
    arrivals_df = keep_relevant_airports(clean_df, airport)
    return arrivals_df


def import_relevant_cols(data_files):
    df_from_each_file = (pd.read_csv(
        f,
        index_col=None,
        usecols=['callsign',
                 'runway',
                 'positions',
                 'initialGateTimeOfDeparture',
                 'aircraftType',
                 'arrAirport',
                 'arrGate'],
        header=0,
        na_values='null')
                         for f in data_files)

    result_df = pd.DataFrame(pd.concat(df_from_each_file, ignore_index=True))
    return result_df


def remove_nulls(input_df):
    result_df = input_df.dropna()
    return result_df


def keep_relevant_airports(clean_df, airport):
    result_df = clean_df[clean_df.arrAirport.str.contains(airport)]
    return result_df


import glob
import os
import re
import sys
import time

import pandas as pd

import calculator
import cleanser
import lp
import preprocessor


def main():
    # LOAD
    path = './Data'
    data_files = glob.glob(os.path.join(path, '*.csv'))
    airport = re.search(r'_(.*)_', data_files[0]).group(1)

    # CREATE
    try:  # Import all reference files pertaining to the arrival airport
        runway_info_df = pd.read_csv(
            './References/runwayInfo_' + airport + '.csv',
            na_filter=False)

        gate_nodes_df = pd.read_csv(
            './References/gateNodes_' + airport + '.csv',
            na_filter=False)
        gate_nodes_df.node = gate_nodes_df.node.apply(str)

        exit_info_df = pd.read_csv(
            './References/exitInfo_' + airport + '.csv',
            na_filter=False)
        exit_info_df.exit = exit_info_df.exit.apply(str)

        weather_df = pd.read_csv(
            './References/weatherData_' + airport + '.csv',
            usecols=['Date:',
                     'Hour:',
                     'Precipitation ID:',
                     'Wind Speed (mph):',
                     'Wind Dir.:'])
        weather_df = weather_df.rename(
            columns={'Date:': 'date', 'Hour:': 'hour'})
    except IOError:  # If any file doesn't exist, airport is not supported
        sys.exit('Airport not supported')

    actype_df = pd.read_csv(
        './References/PlaneSizeDefinition.csv',
        usecols=['aircraftType', 'category'],
        na_filter=False)

    # CLEANSE
    arrivals_df = cleanser.cleanse(data_files, airport)

    # PRE-PROCESS
    final_df = preprocessor.process(
        arrivals_df,
        runway_info_df,
        gate_nodes_df,
        actype_df,
        weather_df)

    # CALCULATIONS
    touchdown_dist = calculator.td_distance(final_df)
    exit_dist = calculator.exit_distance(runway_info_df, exit_info_df)

    # PREP AND SOLVE LP
    lp_exits, lp_values = lp.optimal(
        final_df,
        exit_info_df,
        touchdown_dist,
        exit_dist)

    # OUTPUT TO FILE
    end_df = final_df.rename(columns={'gate': 'arrGate'}).drop(
        ['date', 'hour', 'touchdownLat', 'touchdownLong', 'runwayLat',
         'runwayLong', 'category', 'direction', 'Precipitation ID:',
         'Wind Speed (knots)', 'Wind Dir.:'],
        axis=1)

    optimal_df = end_df.assign(optimalExit=lp_exits, optimalValue=lp_values)
    output = optimal_df.assign(
        meanValue=[round(optimal_df.optimalValue.mean(0), 2)] +
                  [None] * (len(optimal_df) - 1),
        stdevValue=[round(optimal_df.optimalValue.std(0), 2)] +
                 [None] * (len(optimal_df) - 1))

    if not os.path.exists('./RESULTS'):
        os.makedirs('./RESULTS')

    output.to_csv('./RESULTS/'+airport+'_'+str(int(time.time()))+'.csv')


if __name__ == '__main__':
    main()

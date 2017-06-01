from geopy.distance import vincenty


def td_distance(final_df):
    runway_start = [[final_df.runwayLat[i], final_df.runwayLong[i]]
                    for i in range(len(final_df))]

    plane_land = [[final_df.touchdownLat[i], final_df.touchdownLong[i]]
                  for i in range(len(final_df))]

    td_dist = [vincenty(runway_start[i], plane_land[i]).meters
               for i in range(len(runway_start))]
    return td_dist


def exit_distance(runway_info_df, exit_info_df):
    all_dist = []
    for i in runway_info_df.runway:
        exits_on_runway = exit_info_df[exit_info_df.runway.str.contains(i)]

        exit_loc = [[exits_on_runway.lat[w], exits_on_runway.long[w]]
                    for w in exits_on_runway.axes[0]]

        runway_start = [float(runway_info_df.lat[runway_info_df.runway == i]),
                        float(runway_info_df.long[runway_info_df.runway == i])]

        distance = [vincenty(runway_start, exit_loc[j]).meters
                    for j in range(len(exit_loc))]

        # Matches exit label with distance
        dist_dict = dict(zip(exits_on_runway.exit, distance))

        all_dist.append(dist_dict)

    # Matches runways with their exits
    all_dict = dict(zip(runway_info_df.runway, all_dist))

    return all_dict

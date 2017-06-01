import multiprocessing as mp
import pulp


def optimal(final_df, exit_info_df, touchdown_dist, exit_dist):
    all_exits = [list(exit_dist[i]) for i in final_df.runway]
    setup(final_df, touchdown_dist, exit_dist, all_exits)

    # All costs are $ per second
    costs = {'PT':   {'GA':     0.22,
                      'Small':  0.49,
                      'Medium': 3.16,
                      'Large':  4.86,
                      'Super':  6.69},
             'ENV':  0.60,
             'TT':   0.83,
             'FUEL': 0.18}

    rot_list, tt_list = get_time(
        all_exits,
        final_df,
        exit_dist,
        touchdown_dist,
        exit_info_df)

    cost_list = get_costs(final_df, rot_list, tt_list, costs)

    print('Solving...')
    with mp.Pool(processes=int(mp.cpu_count()/2)) as pool:
        lp_results = list(pool.starmap(solve, list(zip(all_exits, cost_list))))
    print('Done solving.')

    lp_exits = [i[0] for i in lp_results]
    lp_values = []
    for j in lp_results:
        if j[1] is None:
            lp_values.append(j[1])
        else:
            lp_values.append(round(j[1], 2))

    return lp_exits, lp_values


def setup(final_df, touchdown_dist, exit_dist, all_exits):
    for i in range(len(final_df.runway)):
        for j in reversed(range(len(exit_dist[final_df.runway[i]]))):
            if touchdown_dist[i] > exit_dist[final_df.runway[i]][all_exits[i][j]]:
                del all_exits[i][j]


def get_time(feasible_exits, final_df, exit_dist, touchdown_dist, exit_info_df):
    rot_list, tt_list = [], []
    taxi_speed = 20 * (6076 / 5280) * (1609.344 / 3600)  # knots to mph to m/s

    # Get times in seconds
    for i in range(len(final_df)):
        rot = [((exit_dist[final_df.runway[i]][j] -
                 touchdown_dist[i]) / taxi_speed)
               for j in feasible_exits[i]]
        rot_list.append(rot)

        exit_taxi_info = exit_info_df[
            exit_info_df.exit.isin(feasible_exits[i])]

        tt = [(k / taxi_speed)
              for k in exit_taxi_info['distNode' + final_df.node[i]]]
        tt_list.append(tt)

    return rot_list, tt_list


def get_costs(final_df, rot_list, tt_list, costs):
    rot_constant = [costs['FUEL'] + costs['ENV'] + costs['PT'][i]
                    for i in final_df.category]

    tt_constant = [costs['TT'] + costs['ENV'] + costs['PT'][i]
                   for i in final_df.category]

    cost_list = []
    for j in range(len(final_df)):
        combined_cost = [(rot_constant[j] * rot_list[j][k] +
                          tt_constant[j] * tt_list[j][k])
                         for k in range(len(rot_list[j]))]
        cost_list.append(combined_cost)
    return cost_list


def solve(flight_exits, costs):
    # Runway exits are binary decision variables
    variables = pulp.LpVariable.matrix(
        'Exit',
        flight_exits,
        0,
        1,
        pulp.LpInteger)

    # Creates the 'prob' variable to contain the problem data
    prob = pulp.LpProblem("Airport Exits Optimization", pulp.LpMinimize)

    prob += pulp.lpSum([variables[w] * costs[w] for w in range(len(costs))])

    prob += pulp.lpSum(variables) == 1  # s.t. Only choose one exit

    prob.solve()

    if prob.status == 1:
        for v in variables:
            if v.value() == 1.0:
                lp_exit = v.name[5:].replace('_', '-')
                break
        lp_value = pulp.value(prob.objective)
    else:
        lp_exit = None
        lp_value = None

    return lp_exit, lp_value

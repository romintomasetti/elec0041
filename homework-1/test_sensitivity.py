import copy
import logging
import os
import json

from matplotlib import pyplot as plt
import numpy
import typeguard

import optimization
from test_mesh_convergence import set_common_props

@typeguard.typechecked
def prepare_points(*,GEOM_PARAMS_OPTIMAL : dict, name : str, SENSITIVITY_RANGE : float, NUM_PTS : int) -> numpy.ndarray:
    """
    Prepare sensitivity points.
    SENSITIVITY_RANGE : sensitivity range around nominal value in percent, e.g. 5.
    """
    start_value = (1.0-SENSITIVITY_RANGE/100.0) * GEOM_PARAMS_OPTIMAL[name]
    stop_value  = (1.0+SENSITIVITY_RANGE/100.0) * GEOM_PARAMS_OPTIMAL[name]
    tmp = numpy.linspace(start=start_value,stop=stop_value,num=NUM_PTS)
    tmp = numpy.insert(tmp,[0],GEOM_PARAMS_OPTIMAL[name])
    tmp = numpy.sort(tmp)
    return tmp

@typeguard.typechecked
def evaluate_sensitivity(
    *,GEOM_PARAMS_OPTIMAL : dict,
    name : str, DO_EVAL : bool,
    problem : optimization.Problem,
    SENSITIVITY_RANGE : float,
    NUM_PTS : float,
) -> dict:
    """
    Evaluate sensitivity w.r.t. a single parameter.
    """
    sensitivity = {}
    filename = os.path.abspath(__file__).replace('.py',f'.{name}.json')
    if DO_EVAL:
        for point in prepare_points(name=name,GEOM_PARAMS_OPTIMAL=GEOM_PARAMS_OPTIMAL,SENSITIVITY_RANGE=SENSITIVITY_RANGE,NUM_PTS=NUM_PTS):
            params = copy.deepcopy(GEOM_PARAMS_OPTIMAL)
            params[name] = point
            logging.info(f"> Sensitivity : {name} : {params}")
            currents = problem(x=params.values())
            sensitivity[point] = problem.objective_func_inner(currents=currents)
        with open(filename,'w+') as f:
            json.dump(sensitivity,f)
    else:
        with open(filename,'r') as f:
            sensitivity = json.load(f)
        sensitivity = {float(k) : v for k,v in sensitivity.items()}
        assert len(sensitivity) == NUM_PTS+1
    return sensitivity

def test_sensitivity_near_optimal():
    """
    Check sensitivity of optimal point.
    It is a simple One-At-A-Time method.
    """
    # Parameters of the optimal point
    GEOM_PARAMS_OPTIMAL = {
        "DO_y"      : 0.027866968988955805,
        "DO_a"      : 0.010593076883293234,
        "DO_b"      : 0.00635262054464091,
    }

    # Create problem with symmetry
    problem = optimization.problem_homework_1(
        filenamebase = "busbar.sym",
        outputfiles  = ".sym",
        coef_I_inobj = 2.0,
    )

    # Sensitivity range w.r.t. to nominal value in percent
    SENSITIVITY_RANGE = 1

    # Number of points
    NUM_PTS = 20

    # Set to True to run simulations, False to read from files
    DO_EVAL = True

    # Common parameters for sensitivity evaluation
    evaluate_sensitivity_params = {
        'GEOM_PARAMS_OPTIMAL': GEOM_PARAMS_OPTIMAL,
        'DO_EVAL'            : DO_EVAL,
        'problem'            : problem,
        'NUM_PTS'            : NUM_PTS,
        'SENSITIVITY_RANGE'  : SENSITIVITY_RANGE,
    }

    # Sensitivity w.r.t. DO_y
    doy_sens = evaluate_sensitivity(name='DO_y',**evaluate_sensitivity_params)

    # Sensitivity w.r.t. DO_a
    doa_sens = evaluate_sensitivity(name="DO_a",**evaluate_sensitivity_params)

    # Sensitivity w.r.t. DO_b
    dob_sens = evaluate_sensitivity(name='DO_b',**evaluate_sensitivity_params)

    # Global sensitivity plot
    fig, ax = plt.subplots(1,1,figsize=(6,6))
    for k,v in {"DO_y" : doy_sens, "DO_a" : doa_sens, "DO_b" : dob_sens}.items():
        ax.plot(
            numpy.array(list(v.keys())) / GEOM_PARAMS_OPTIMAL[k],
            v.values(),
            "*-.",
            label=f'${k}$'
        )
    set_common_props(ax,xlabel=f"Deviation from optimal value [-]",legend=True)
    ax.set_ylabel("Current imbalance [A]")
    ax.ticklabel_format(axis="x", style="sci", scilimits=(0,0))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45 )
    plt.savefig(os.path.abspath(__file__).replace('.py',f'.svg'))
    plt.close(fig)

if __name__ == "__main__":

    test_sensitivity_near_optimal()

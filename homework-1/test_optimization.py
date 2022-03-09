import numpy

import optimization

# Copper plate thickness [m]
CP_thickn = 0.002

# Expected currents for full or half simulation.
# Should be in a ratio of 2 for input port and middle output port.
EXPECTED_RESULT_FULL = numpy.array([375.      , -118.8039755425, -137.3923153039, -118.8037091536]) / CP_thickn
EXPECTED_RESULT_SYM  = numpy.array([375. / 2.0, -118.8049184147, -68.6950815853                  ]) / CP_thickn

def test_homework_1():
    # Create problem
    problem = optimization.problem_homework_1(filenamebase="busbar", outputfiles = "", coef_I_inobj = 1.0)

    # Run a nominal to check it's allright
    res = problem.nominal()
    assert numpy.allclose(res,EXPECTED_RESULT_FULL),res

    assert numpy.allclose(problem.fields['voltages'][1::],[0.,0.,0.,])

def test_homework_1_sym():
    # Create problem with symmetry
    problem = optimization.problem_homework_1(filenamebase="busbar.sym", outputfiles = ".sym", coef_I_inobj = 2.0)

    # Run a nominal to check it's allright
    res = problem.nominal()
    assert numpy.allclose(res,EXPECTED_RESULT_SYM),res

    assert numpy.allclose(problem.fields['voltages'][1::],[0.,0.,])

def test_homework_1_near_optimal():
    """
    Test a 'near-optimal' configuration, i.e. currents are 'nearly' balanced.
    """
    GEOM_PARAMS = [
        0.02787345, # Y position of DO center
        0.01059685, # Half vertical axis
        0.0063542 , # Half horizontal axis
    ]
    EXPECTED_CURRENTS  = numpy.array([ 187.5 , -125.0010832372 , -62.4989167628]) / CP_thickn

    # Create problem with symmetry
    problem = optimization.problem_homework_1(filenamebase="busbar.sym", outputfiles = ".sym", coef_I_inobj = 2.0)

    # Run at that point and check currents values
    currents = problem(x=GEOM_PARAMS)
    assert numpy.allclose(currents,EXPECTED_CURRENTS)

    assert numpy.allclose(problem.fields['voltages'][1::],[0.,0.,])

import numpy

import optimization

# Expected currents for full or half simulation.
# Should be in a ratio of 2 for input port and middle output port.
EXPECTED_RESULT_FULL = [375.      , -118.80611118, -137.38703399, -118.80685483]
EXPECTED_RESULT_SYM  = [375. / 2.0, -118.80420895, -68.69579105]

def test_homework_1():
    # Create problem
    problem = optimization.problem_homework_1(filenamebase="busbar", outputfiles = "", coef_I_inobj = 1.0)

    # Run a nominal to check it's allright
    res = problem.nominal()
    assert numpy.allclose(res,EXPECTED_RESULT_FULL),res

def test_homework_1_sym():
    # Create problem with symmetry
    problem = optimization.problem_homework_1(filenamebase="busbar.sym", outputfiles = ".sym", coef_I_inobj = 2.0)

    # Run a nominal to check it's allright
    res = problem.nominal()
    assert numpy.allclose(res,EXPECTED_RESULT_SYM),res

def test_homework_1_near_optimal():
    GEOM_PARAMS = [
        0.02787345, # Y position of DO center
        0.01059685, # Half vertical axis
        0.0063542 , # Half horizontal axis
    ]
    EXPECTED_CURRENTS  = [ 187.5      ,  -125.00003487 , -62.49996513]

    # Create problem with symmetry
    problem = optimization.problem_homework_1(filenamebase="busbar.sym", outputfiles = ".sym", coef_I_inobj = 2.0)

    # Run at that point and check currents values
    currents = problem(x=GEOM_PARAMS)
    assert numpy.allclose(currents,EXPECTED_CURRENTS)

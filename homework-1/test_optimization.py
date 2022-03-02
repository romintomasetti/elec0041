import numpy

import optimization

def test_homework_1():
    # Create problem
    problem = optimization.problem_homework_1()

    # Run a nominal to check its allright
    res = problem.nominal()
    assert numpy.allclose(res,[375., -118.80611118, -137.38703399, -118.80685483]),res

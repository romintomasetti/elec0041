import os
from pathlib import Path
import typing
import logging
import subprocess
import re

import numpy
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.differential_evolution.html#scipy.optimize.differential_evolution
import scipy.optimize
import typeguard

# Setup logging
logging.basicConfig(
    level = logging.DEBUG
)

# Constant variables
HOMEWORK_1 = Path('homework-1')

class Problem(object):
    """
    Class that defines our problem.
    """

    @typeguard.typechecked
    def __init__(self,*,
        geo_file : typing.Union[str,Path],
        pro_file : typing.Union[str,Path],
        outputfiles : str,
        problem : str,
        postpro : str,
        input_parameters : typing.Dict[str,typing.List],
        coef_I_inobj : float
    ):
        """
        Initialize problem:
            * .geo file
            * .pro file
            * suffix to add to output files
            * problem name in the .pro file to solve
            * post-pro name in the .pro file
            * input variables
            * coefficient to be applied to input current in objective function
        """
        assert os.path.exists(geo_file)
        assert os.path.exists(pro_file)
        self.geo_file = geo_file
        self.pro_file = pro_file

        self.outputfiles = outputfiles

        self.problem = problem
        self.postpro = postpro

        self.input_parameters=  input_parameters

        self.coef_I_inobj = coef_I_inobj

        # Count the number of evaluations
        self.counter = 0

    @typeguard.typechecked
    def _setnumber(self,*,input_parameters_values : typing.Dict[str,float]) -> typing.List[str]:
        a = [["-setnumber",k,str(v)] for k,v in input_parameters_values.items()]
        return [item for sublist in a for item in sublist]

    @typeguard.typechecked
    def _mesh(self,*,input_parameters_values : typing.Dict[str,float]):
        """
        Use GMSH to mesh the geometry.
        """
        # Run GMSH
        o = subprocess.check_output(
            args = [
                "gmsh",
                *self._setnumber(input_parameters_values=input_parameters_values),
                "-2",
                self.geo_file,
            ]
        )
        logging.debug(o.decode())

        # Determine the number of elements in the mesh
        match = re.search(r'([0-9]*) nodes ([0-9]*) elements',o.decode())
        assert match is not None and len(match.groups()) == 2
        self.number_of_nodes, self.number_of_elements = [int(x) for x in match.groups()]

        # Ensure there is no warning or skipping in the output of GMSH
        if any(x in o.decode() for x in ['Warning','warning','skipping','Skipping']):
            raise RuntimeError(f"An error occured while meshing with {input_parameters_values}")

    def _read(self):
        """
        Load the following fields:
            * current at output ports
            * voltage at input port
            * integrated losses
        Always discards the first element in the file (not useful in this case).
        """
        fields = {}

        # Read currents
        with open(Path(os.path.dirname(self.geo_file)) / f"I{self.outputfiles}.txt","r") as f:
            fields['currents'] = numpy.loadtxt(f)[1::]

        # Read voltages
        with open(Path(os.path.dirname(self.geo_file)) / f"U{self.outputfiles}.txt","r") as f:
            fields['voltages'] = numpy.loadtxt(f)[1::]

        # Read integrated losses
        with open(Path(os.path.dirname(self.geo_file)) / f"integrated.losses{self.outputfiles}.txt","r") as f:
            fields['losses'] = numpy.loadtxt(f)[1::]

        return fields

    @typeguard.typechecked
    def _solve(self,*,input_parameters_values : typing.Dict[str,float]):
        """
        Use GETDP to solve the problem.
        """
        # Run GETDP
        o = subprocess.check_output(
            args = [
                "getdp",
                *self._setnumber(input_parameters_values=input_parameters_values),
                self.pro_file,
                "-solve",self.problem,
                "-pos",self.postpro,
            ]
        )
        logging.debug(o.decode())

        # Check in the output that the input parameters where correctly recognized by GETDP
        for k,v in input_parameters_values.items():
            tmp = f"Adding number {k} = {str(v)[0:3]}"
            assert tmp in o.decode(),"{} not found in {}".format(tmp,o.decode())

    def nominal(self):
        """
        Run the workflow with nominal values to check everything is OK.
        """
        input_parameters_values = [x[0] for x in self.input_parameters.values()]
        return self(input_parameters_values)

    def __call__(self,x):
        self.counter += 1
        logging.info(f"> Computing model with {x} for the {self.counter} time")
        x = {
            k : v for k,v in zip(self.input_parameters.keys(),x)
        }
        self._mesh (input_parameters_values=x)
        self._solve(input_parameters_values=x)
        self.fields = self._read()
        return self.fields['currents']

    def objective_func(self,x):
        """
        Objective function will be minimized.
        F(I1,I2,I3) = abs( abs(I1) - abs(I2) )
        (I1 and I3 are considered equal and we want them to equal I2).
        """
        currents = self(x)
        o = numpy.abs(numpy.abs(currents[1]) - self.coef_I_inobj * numpy.abs(currents[2]))
        logging.info(f"> Objective({x} => {currents}) = {o}")
        return o

    def run(self):
        """
        Run the optimization problem.
        """
        # Reset counter
        self.counter = 0

        # Bounds for the optimizer
        bounds = [
            (x[1],x[2]) for x in self.input_parameters.values()
        ]

        logging.info(f"> Launching optimization with bounds {bounds}")

        # Brute force DOE
        result = scipy.optimize.brute(
            func    = self.objective_func,
            ranges  = bounds,
            Ns      = 4,
            # finish  = None,
        )
        logging.info(f"Global best point found is {result}")

def problem_homework_1(filenamebase : str = "busbar",outputfiles : str = "", coef_I_inobj : float = 1.0):
    """
    Create problem for homework 1.
    """
    return Problem(
        geo_file         = HOMEWORK_1 / f"{filenamebase}.geo",
        pro_file         = HOMEWORK_1 / f"{filenamebase}.pro",
        outputfiles      = outputfiles,
        problem          = "EleKin_v",
        postpro          = "Map",
        coef_I_inobj     = coef_I_inobj,
        input_parameters = {
            # Input variable with nominal/low/high range.
            "DO_y" : [0.035  , 0.03  , 0.04  ],
            "DO_a" : [0.0075 , 0.005 , 0.01  ],
            "DO_b" : [0.004  , 0.002 , 0.006 ],
        }
    )

if __name__ == "__main__":

    problem = problem_homework_1(
        filenamebase = "busbar.sym",
        outputfiles  = ".sym",
        coef_I_inobj = 2.0,
    )
    problem.run()

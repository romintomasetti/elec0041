import os
from pathlib import Path
import typing
import logging
import subprocess
import re
import copy

import numpy
import pandas
import scipy.optimize
import typeguard

# Setup logging
logging.basicConfig(
    level = logging.INFO
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
        coef_I_inobj : float,
        mesh_parameters : dict = {},
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
            * mesh constants (defaults to empty dict, i.e. default values from .geo file)
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

        self.mesh_parameters = mesh_parameters

        # Count the number of evaluations
        self.counter = 0

        # Store the fields at each optimization iteration
        self.database : pandas.DataFrame = None

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
                *self._setnumber(input_parameters_values=self.mesh_parameters),
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

        # Add to database
        if self.database is None:
            self.database = pandas.DataFrame(columns=list(self.fields.keys()) + list(x.keys()))
        data = copy.deepcopy(self.fields)
        data.update(copy.deepcopy(x))
        self.database = self.database.append(
            data,
            ignore_index=True,
        )

        return self.fields['currents']

    def objective_func_inner(self,*,currents):
        return numpy.abs(numpy.abs(currents[1]) - self.coef_I_inobj * numpy.abs(currents[2]))

    def objective_func(self,x):
        """
        Objective function will be minimized.
        F(I1,I2,I3) = abs( abs(I1) - abs(I2) )
        (I1 and I3 are considered equal and we want them to equal I2).
        """
        currents = self(x)
        o = self.objective_func_inner(currents = currents)
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

def problem_homework_1(filenamebase : str = "busbar",outputfiles : str = "", coef_I_inobj : float = 1.0, mesh_parameters : dict = {}):
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
        },
        mesh_parameters  = mesh_parameters,
    )

if __name__ == "__main__":

    DATABASE_FILE = os.path.abspath(__file__).replace('.py','.db')

    problem = problem_homework_1(
        filenamebase = "busbar.sym",
        outputfiles  = ".sym",
        coef_I_inobj = 2.0,
    )

    # Use this switch to run the optimization only once, and then use the saved database
    if True:
        problem.run()
        problem.database.to_csv(
            path_or_buf = DATABASE_FILE,
        )
    else:
        string_to_numpy_array = lambda s : numpy.array([float(x) for x in s.strip('[]').split(' ') if x != ""])
        problem.database = pandas.read_csv(
            filepath_or_buffer = DATABASE_FILE,
            converters = {
                # Convert from string representation of a list of floats to a numpy array
                "currents" : string_to_numpy_array,
                "voltages" : string_to_numpy_array,
                "losses"   : string_to_numpy_array,
                "DO_y"     : string_to_numpy_array,
                "DO_a"     : string_to_numpy_array,
                "DO_b"     : string_to_numpy_array,
            }
        )

    # Transform data to numpy array for easier manipulation
    currents = numpy.stack(problem.database["currents"].to_numpy(),axis=0)
    voltages = numpy.stack(problem.database["voltages"].to_numpy(),axis=0)
    losses   = numpy.stack(problem.database["losses"  ].to_numpy(),axis=0)
    DO_y     = numpy.stack(problem.database["DO_y"    ].to_numpy(),axis=0)
    DO_a     = numpy.stack(problem.database["DO_a"    ].to_numpy(),axis=0)
    DO_b     = numpy.stack(problem.database["DO_b"    ].to_numpy(),axis=0)

    # Re-create objective function
    objective = numpy.abs(currents[:,1]- problem.coef_I_inobj * currents[:,2])

    # Check sizes
    assert currents .shape == (problem.database.shape[0],3) and currents .dtype == float
    assert voltages .shape == (problem.database.shape[0],3) and currents .dtype == float
    assert losses   .shape == (problem.database.shape[0],1) and losses   .dtype == float
    assert DO_y     .shape == (problem.database.shape[0],1) and DO_y     .dtype == float
    assert DO_a     .shape == (problem.database.shape[0],1) and DO_a     .dtype == float
    assert DO_b     .shape == (problem.database.shape[0],1) and DO_b     .dtype == float
    assert objective.shape == (problem.database.shape[0], ) and objective.dtype == float

    # For the graphs, only use the points that have small objective
    logging.info(
        "> Optimal point is:\n"
        "\t> DO_a      : {}\n"
        "\t> DO_b      : {}\n"
        "\t> DO_y      : {}\n"
        "\t> imbalance : {}\n"
        "\t> losses    : {}".format(
        DO_a[-1,0],
        DO_b[-1,0],
        DO_y[-1,0],
        objective[-1],
        losses[-1,0],
    ))

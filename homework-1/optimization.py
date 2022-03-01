import os
from pathlib import Path
import typing
import itertools
import subprocess

import typeguard

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
        problem : str,
        postpro : str,
        input_parameters : typing.Dict[str,typing.List]
    ):
        """
        Initialize problem:
            * .geo file
            * .pro file
            * problem name in the .pro file to solve
            * post-pro name in the .pro file
            * input variables
        """
        assert os.path.exists(geo_file)
        assert os.path.exists(pro_file)
        self.geo_file = geo_file
        self.pro_file = pro_file

        self.problem = problem
        self.postpro = postpro

        self.input_parameters=  input_parameters

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

        # Ensure there is no warning or skipping in the output of GMSH
        if any(x in o.decode() for x in ['Warning','warning','skipping','Skipping']):
            raise RuntimeError(f"An error occured while meshing with {input_parameters_values}")

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

        # Check in the output that the input parameters where correctly recognized by GETDP
        for k,v in input_parameters_values.items():
            assert f"Adding number {k} = {v}" in o.decode()

    def nominal(self):
        """
        Run the workflow with nominal values to check everything is OK.
        """
        input_parameters_values = {
            k : v[0] for k,v in self.input_parameters.items()
        }
        self._mesh (input_parameters_values=input_parameters_values)
        self._solve(input_parameters_values=input_parameters_values)

    def run(self):
        """
        Run the optimization problem.
        """

if __name__ == "__main__":

    problem = Problem(
        geo_file         = HOMEWORK_1 / "busbar.geo",
        pro_file         = HOMEWORK_1 / "busbar.pro",
        problem          = "EleKin_v",
        postpro          = "Map",
        input_parameters = {
            # Input variable with nominal/low/high range
            "DO_y" : [0.035  , 0.01  , 0.06 ],
            "DO_a" : [0.0075 , 0.005 , 0.01 ],
            "DO_b" : [0.004  , 0.002 , 0.006],
        }
    )

    problem.nominal()
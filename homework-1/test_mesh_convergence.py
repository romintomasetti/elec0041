import logging
import pprint
import time
import os
from pathlib import Path
import re

import typeguard
import numpy
import pandas
import matplotlib
from matplotlib import pyplot as plt

font = {'size' : 12}
matplotlib.rc('font', **font)

import optimization

DEFAULT_MESH_PARAMETERS = {
    'CP_mesh_t' : 0.0009,
    'CP_mesh_b' : 0.0009,
    'IO_mesh'   : 0.000225,
    'DO_mesh'   : 0.000225,
}

@typeguard.typechecked
def set_common_props(ax,legend : bool = True, xlabel : str = 'Number of elements [-]'):
    """
    Set common plot properties.
    """
    ax.grid(visible=True,which="major",color='#666666', linestyle='-',linewidth=0.2)
    ax.set_yscale('linear')
    ax.set_xlabel(xlabel)
    if legend: ax.legend()

def test_mesh_parameters():
    """
    Ensure that the default mesh parameters are indeed used in the .geo.
    """
    file = Path(os.path.dirname(os.path.abspath(__file__))) / 'mesh.parameters.geo'
    assert os.path.exists(file)

    content = Path(file).read_text()

    for param,value in DEFAULT_MESH_PARAMETERS.items():
        pattern = rf'DefineConstant[[ ]*{param}[ ]*=[ ]*{{{value}[ ]*, Name'
        assert re.search(pattern,content) is not None,pattern

def test_mesh_convergence():
    """
    Check mesh convergence as elements get smaller.
    """
    # Columns of the dataframe
    columns = ['ratio', 'elapsed', 'current-left', 'current-center', 'number-of-elements', 'voltage-input', 'losses']

    # Ratios of the mesh size
    ratios = [4,3,2.5,2,1.75,1.5,1.3,1.2,1.0,0.9,0.8,]

    # Create dataframe
    pd = pandas.DataFrame(columns = columns)
    for col in columns:
        pd[col] = numpy.zeros(shape=(len(ratios),1)) if col != 'ratio' else numpy.array(ratios)
    for row,ratio in enumerate(pd['ratio']):
        started_at = time.time()
        logging.info(f"> Mesh with ratio {ratio} ({started_at})")
        problem = optimization.problem_homework_1(
            filenamebase    = "busbar.sym",
            outputfiles     = ".sym",
            coef_I_inobj    = 2.0,
            mesh_parameters = {
                "CP_mesh_t" : ratio * DEFAULT_MESH_PARAMETERS['CP_mesh_t'],
                "CP_mesh_b" : ratio * DEFAULT_MESH_PARAMETERS['CP_mesh_b'],
                "IO_mesh"   : ratio * DEFAULT_MESH_PARAMETERS['IO_mesh'],
                "DO_mesh"   : ratio * DEFAULT_MESH_PARAMETERS['DO_mesh'],
            }
        )
        _ = problem.nominal()
        pd.at[row,'elapsed'           ] = time.time()-started_at
        pd.at[row,'current-left'      ] = problem.fields['currents'][1]
        pd.at[row,'current-center'    ] = problem.fields['currents'][2]
        pd.at[row,'number-of-elements'] = problem.number_of_elements
        pd.at[row,'voltage-input'     ] = problem.fields['voltages'][0]
        pd.at[row,'losses'            ] = problem.fields['losses'][0]

    pprint.pprint(pd)

    # Chosen mesh parametrization
    chosen_mesh = pd.loc[pd['ratio'] == 1.0]
    chosen_mesh_plt = {'marker' : 'X', 'color' : 'tab:green', 'markersize' : 10}

    # Create plots
    fig, axes = plt.subplots(1,2,figsize=(12,6))

    # Left plot : currents
    axes[0].plot(pd['number-of-elements'],pd['current-center'] / pd['current-center'].mean(),'*-.',label="$I_c / I_{c,mean}$ [-]")
    axes[0].plot(pd['number-of-elements'],pd['current-left']   / pd['current-left']  .mean(),'*--',label="$I_l / I_{l,mean}$ [-]")
    axes[0].grid(visible=True,which="major",color='#666666', linestyle='-',linewidth=0.2)
    set_common_props(axes[0])
    axes[0].ticklabel_format(axis="y", style="sci", scilimits=(0,0))
    axes[0].plot(chosen_mesh['number-of-elements'],chosen_mesh['current-center'] / pd['current-center'].mean(),**chosen_mesh_plt)
    axes[0].plot(chosen_mesh['number-of-elements'],chosen_mesh['current-left'  ] / pd['current-left'  ].mean(),**chosen_mesh_plt)

    # Right plot : losses
    color_losses  = 'tab:blue'
    color_elapsed = 'tab:red'
    line_losses = axes[1].plot(pd['number-of-elements'],pd['losses'] ,'*-.',color=color_losses,label="Integrated losses [$W \cdot m^{-2}$]")
    axes[1].tick_params(axis='y', labelcolor=color_losses)
    twin = axes[1].twinx()
    line_elapsed = twin.plot(pd['number-of-elements'],pd['elapsed'],'*--',color=color_elapsed,label='Elapsed time [s]')
    twin.tick_params(axis='y', labelcolor=color_elapsed)
    set_common_props(axes[1],legend=False)
    legend_elts = line_losses + line_elapsed
    legend_labels = [x.get_label() for x in legend_elts]
    axes[1].legend(legend_elts,legend_labels)
    axes[1].plot(chosen_mesh['number-of-elements'],chosen_mesh['losses'],**chosen_mesh_plt)
    twin   .plot(chosen_mesh['number-of-elements'],chosen_mesh['elapsed'],**chosen_mesh_plt)

    # Save figure
    plt.savefig(
        os.path.abspath(__file__).replace('.py','.svg'),
        bbox_inches='tight',
    )

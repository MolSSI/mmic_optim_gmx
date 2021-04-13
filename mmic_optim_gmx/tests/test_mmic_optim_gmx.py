"""
Unit and regression test for the mmic_optim_gmx package.
"""

# Import package, test suite, and other packages as needed
import mmic_optim
from mmic_optim import OptimInput, OptimOutput
from mmic_optim_gmx.components import (
    GmxPreProcessComponent,
    GmxComputeComponent,
    GmxPostComponent,
)
import pytest
import sys
import os

mol_file = os.path.join("mmic_optim_gmx", "data", "molecule.json")
ff_file = os.path.join("mmic_optim_gmx", "data", "forcefield.json")


def test_mmic_optim_gmx_imported():
    """Sample test, will always pass so long as import statement worked"""
    assert "mmic_optim_gmx" in sys.modules


def test_preprocess_component():
    """
    This test reads the mol and ff files in data/ and
    runs preprocess component to see if a .mdp file can be
    written successfully
    """

    with open(mol_file, "r") as fp:
        mol = json.load(fp)

    with open(ff_file, "r") as fp:
        ff = json.load(fp)

    inputs = OptiomInput(
        molecule={"mol": mol},
        forcefield={"ff": ff},
        boundary=(periodic, periodic, periodic),
        max_steps=10000,
        step_stze=0.01,
        tol=1000,
        method="steepest descent",
    )

    return gmx_preprocess_component.compute(inputs)


def test_compute_component():
    """
    This test runs the compute component
    """

    inputs = test_preprocess_component() if inputs == None else inputs

    # assert os.path.exists("GMX_pre.pdb") == False#should be moved to another test

    return gmx_compute_component.compute(inputs)


def test_postprocess_component():
    """
    This test runs the postprocess component
    """

    inputs = test_compute_component() if inputs == None else inputs

    # assert os.path.exists("mdout.mdp") == Falseshould be moved to another test

    outputs = gmx_post_component.compute(inputs)


def test_cleaner():
    """
    This test will figure out if all the files are
    removed. (pdb, mdp, gro, edr, trr)
    Should search for file extensions instead of
    specific file names
    """
    cwd = os.getcwd()
    f_path = os.listdir(cwd)

    j = 0
    for i in f_path:
        if os.path.splitext(i)[1] in {
            ".log",
            ".tpr",
            ".pdb",
            ".mdp",
            ".edr",
            ".trr",
            ".err",
        }:
            j = j + 1

    assert j == 0

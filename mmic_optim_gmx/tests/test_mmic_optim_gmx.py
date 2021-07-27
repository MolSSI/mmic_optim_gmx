"""
Unit and regression test for the mmic_optim_gmx package.
"""

# Import package, test suite, and other packages as needed
import mmelemental
import mmic_optim
from mmic_optim import OptimInput, OptimOutput
from mmelemental.models import Molecule, Trajectory, ForceField
import mmic_optim_gmx

from mmic_optim_gmx.components import OptimGmxComponent

import mm_data
import pytest
import sys
import os


def test_mmic_optim_gmx_imported():
    """Sample test, will always pass so long as import statement worked"""
    assert "mmic_optim_gmx" in sys.modules


def test_preprocess_component():
    """
    This test reads the mol and ff files in data/ and
    runs preprocess component to see if a .mdp file can be
    written successfully
    """

    mol = mmelemental.models.Molecule.from_file(mm_data.mols["water-mol.json"])
    ff = mmelemental.models.ForceField.from_file(mm_data.ffs["water-ff.json"])
    # ff.to_file("temp.json")
    # ff = mmelemental.models.ForceField.from_file("temp.json")
    # traj = Trajectory.from_file(traj_file)

    inputs = OptimInput(
        engine="gmx",  # This is important
        schema_name="test",
        schema_version=1.0,
        molecule={"mol": mol},
        forcefield={"mol": ff},
        boundary=(
            "periodic",
            "periodic",
            "periodic",
            "periodic",
            "periodic",
            "periodic",
        ),
        cell=(0, 0, 0, 1, 1, 1),
        max_steps=10,
        step_size=0.01,
        tol=1000,
        method="steepest descent",
        long_forces={"method": "PME"},
        short_forces={"method": "cutoff"},
    )

    outputs = OptimGmxComponent.compute(inputs)


def test_cleaner():
    """
    This test will figure out if all the files are
    removed. (pdb, mdp, gro, edr, trr)
    Should search for file extensions instead of
    specific file names
    """
    cwd = os.getcwd()
    f_path = os.listdir(cwd)
    print(cwd)

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
            ".top",
        }:
            j = j + 1

    assert j == 0

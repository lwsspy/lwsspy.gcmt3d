import os
import shutil
import numpy as np
import _pickle as pickle
from .constants import Constants
from .model import write_model, write_model_names, write_scaling
from lwsspy.seismo.source import CMTSource
from lwsspy.seismo.read_inventory import flex_read_inventory as read_inventory
from lwsspy.seismo.specfem.inv2STATIONS import inv2STATIONS
from lwsspy.utils.io import read_yaml_file, write_yaml_file
from lwsspy.gcmt3d.process_classifier import ProcessParams


def write_pickle(filename, obj):
    with open(filename, 'wb') as f:
        pickle.dump(obj, f)


def read_pickle(filename):
    with open(filename, 'rb') as f:
        obj = pickle.load(f)

    return obj


def createdir(cdir):
    """"Creates directory tree of specified path if it doesn't exist yet

    Parameters
    ----------
    cdir : str
        Path for building directory tree
    """
    if not os.path.exists(cdir):
        os.makedirs(cdir)


def rmdir(cdir):
    """Removes directory tree if it doesnt exist yet

    Parameters
    ----------
    cdir : str
        Removes directory recursively
    """
    shutil.rmtree(cdir)


# Setup directories
def optimdir(inputfile, cmtfilename, get_dirs_only=False):
    """Sets up source inversion optimization directory

    Parameters
    ----------
    inputfile : str
        location of the input file
    cmtfilename : cmtfilename
        location of original CMTSOLUTION
    get_dirs_only : bool, optional
        Whether to only output the relevant directories, by default False

    Returns
    -------
    _type_
        _description_
    """

    # Read inputfile
    input_params = read_yaml_file(inputfile)

    # Get database location
    databasedir = input_params["database"]

    # Read CMT file
    cmtsource = CMTSource.from_CMTSOLUTION_file(cmtfilename)

    # Get full filename
    outdir = os.path.join(databasedir, cmtsource.eventname)

    # Define the directories
    modldir = os.path.join(outdir, "modl")
    metadir = os.path.join(outdir, "meta")
    datadir = os.path.join(outdir, "data")
    simudir = os.path.join(outdir, "simu")
    ssyndir = os.path.join(simudir, "synt")
    sfredir = os.path.join(simudir, "frec")
    syntdir = os.path.join(outdir, "synt")
    frecdir = os.path.join(outdir, "frec")
    costdir = os.path.join(outdir, "cost")
    graddir = os.path.join(outdir, "grad")
    hessdir = os.path.join(outdir, "hess")
    descdir = os.path.join(outdir, "desc")
    optdir = os.path.join(outdir, 'opt')

    # Only output outdir if wanted
    if get_dirs_only is False:

        # Create directories
        createdir(modldir)
        createdir(metadir)
        createdir(datadir)
        createdir(ssyndir)
        createdir(sfredir)
        createdir(syntdir)
        createdir(frecdir)
        createdir(costdir)
        createdir(graddir)
        createdir(hessdir)
        createdir(descdir)
        createdir(optdir)

    return outdir, modldir, metadir, datadir, simudir, ssyndir, sfredir, syntdir, \
        frecdir, costdir, graddir, hessdir, descdir, optdir


def adapt_processdict(cmtsource, processdict, duration):
    """This is a fairly important method because it implements the
        magnitude dependent processing scheme of the Global CMT project.
        Depending on the magnitude, and depth, the methods chooses which
        wavetypes and passbands are going to be used in the inversion.

    Parameters
    ----------
    cmtsource : lwsspy.seismo.cmtsource.CMTSource
        Earthquake solution
    processdict : dict
        process parameter dictionary
    duration : float
        max duration of the seismograms after processing

    Returns
    -------
    dict
        updated processing parameters
    """

    # Get Process parameters
    PP = ProcessParams(
        cmtsource.moment_magnitude, cmtsource.depth_in_m)
    proc_params = PP.determine_all()

    # Adjust the process dictionary
    for _wave, _process_dict in proc_params.items():

        if _wave in processdict:

            # Adjust weight or drop wave altogether
            if _process_dict['weight'] == 0.0 \
                    or _process_dict['weight'] is None:
                processdict.popitem(_wave)
                continue

            else:
                processdict[_wave]['weight'] = _process_dict["weight"]

            # Adjust pre_filt
            processdict[_wave]['process']['pre_filt'] = \
                [1.0/x for x in _process_dict["filter"]]

            # Adjust trace length depending on the duration
            # given to the class
            processdict[_wave]['process']['relative_endtime'] = \
                _process_dict["relative_endtime"]

            if processdict[_wave]['process']['relative_endtime'] \
                    > duration:
                processdict[_wave]['process']['relative_endtime'] \
                    = duration

            # Adjust windowing config
            for _windict in processdict[_wave]["window"]:
                _windict["config"]["min_period"] = \
                    _process_dict["filter"][3]

                _windict["config"]["max_period"] = \
                    _process_dict["filter"][0]

    # Remove unnecessary wavetypes
    popkeys = []
    for _wave in processdict.keys():
        if _wave not in proc_params:
            popkeys.append(_wave)

    for _key in popkeys:
        processdict.pop(_key, None)

    return processdict


def prepare_inversion_dir(cmtfile, outdir, metadir, inputparamfile):

    # Load CMT solution
    cmtsource = CMTSource.from_CMTSOLUTION_file(cmtfile)

    # Read parameterfile
    inputparams = read_yaml_file(inputparamfile)

    # Write the input parameters to the inversion directory (for easy inversion)
    write_yaml_file(inputparams, os.path.join(outdir, 'input.yml'))

    # Read parameterfile
    inputparams = read_yaml_file(inputparamfile)

    # start label
    start_label = '_' + \
        inputparams['start_label'] if inputparams['start_label'] is not None else ''

    # Get duration from the parameter file
    duration = inputparams['duration']

    # Get initial processing directory
    if inputparams["processparams"] is None:
        processdict = Constants.processdict
    else:
        processdict = read_yaml_file(inputparams['processparams'])

    # Adapting the processing dictionary
    processdict = adapt_processdict(cmtsource, processdict, duration)

    # Writing the new processing file to the directory
    write_yaml_file(processdict, os.path.join(outdir, 'process.yml'))

    # Writing Original CMTSOLUTION
    cmtsource.write_CMTSOLUTION_file(
        os.path.join(metadir, cmtsource.eventname + start_label))

    # Write model with generic name for easy access
    cmtsource.write_CMTSOLUTION_file(
        os.path.join(metadir, 'init_model.cmt'))


def prepare_model(outdir, metadir, modldir):

    # Get the initial model
    init_cmt = CMTSource.from_CMTSOLUTION_file(
        os.path.join(metadir, 'init_model.cmt'))

    # Read parameterfile
    inputparams = read_yaml_file(os.path.join(outdir, 'input.yml'))

    # Get the parameters to invert for
    parameters = inputparams['parameters']

    # Get model names
    model_names = list(parameters.keys())

    # Write model names
    write_model_names(model_names, metadir)

    # Get model vector
    model_vector = np.array([getattr(init_cmt, key)
                            for key in parameters.keys()])

    # Write model vector
    write_model(model_vector, modldir, 0, 0)

    # Get scaling
    scaling_vector = np.array([val['scale'] for _, val in parameters.items()])

    # Write scaling vector
    write_scaling(scaling_vector, metadir)


def prepare_stations(metadir):

    # Read inventory from the station directory and put into a single stations.xml
    inv = read_inventory(os.path.join(metadir, 'stations', '*.xml'))

    # Write inventory to a single station directory
    inv.write(os.path.join(metadir, 'stations.xml'), format='STATIONXML')

    # Write SPECFEM STATIONS FILE
    inv2STATIONS(inv, os.path.join(metadir, 'STATIONS.txt'))

#!/usr/bin/python

# import global modules
import os
import sys
import argparse
import logging
import re

# import workflow builder
import wf

# Module metadata variables
__author__ = "Jose Rodriguez"
__credits__ = ["Marco Trevisan", "Jesus Vazquez"]
__license__ = "Creative Commons Attribution-NonCommercial-NoDerivs 4.0 Unported License https://creativecommons.org/licenses/by-nc-nd/4.0/"
__version__ = "1.0.1"
__maintainer__ = "Jose Rodriguez"
__email__ = "jmrodriguezc@cnic.es"
__status__ = "Development"

def _print_exception(code, msg):
    '''
    Print the code message
    '''
    logging.exception(msg)
    sys.exit(code)

def main(args):
    '''
    Main function
    '''
    # check parameters
    # extract params for the methods
    params = {}
    methods = ["sanxot1", "sanxotsieve1", "sanxot2"]
    for method in methods:
        if not method in args.params:
            _print_exception( 2, "checking the parameters for the {} method".format(method) )
        match = re.search(r'{\s*' + method + r'\s*:\s*([^\}]*)}', args.params, re.IGNORECASE)
        if match.group():
            params[method] = match.group(1)
        else:
            _print_exception( 2, "checking the parameters for the {} method".format(method) )
    # extract temporal working directory...
    if args.tmpdir:
        tmpdir = args.tmpdir
    # otherwisae, get directory from input files
    else:
        tmpdir = os.path.dirname(os.path.realpath(args.relfile))+"/tmp"
    
    # create builder ---
    logging.info("create workflow builder")
    w = wf.builder(tmpdir, logging)

    logging.info("execute sanxot")
    w.sanxot({
        "-a": "p2q_outs",
        "-d": args.pepfile,
        "-r": args.relfile
    }, params["sanxot1"])

    logging.info("execute sanxotsieve")
    p = { "-d": args.pepfile, "-r": args.relfile, "-f": args.fdr }
    if args.variance: # force the variance
        p["-v"] = args.variance
    else: # use the file variance
        p["-V"] = "p2q_outs_infoFile.txt"
    w.sanxotsieve(p, params["sanxotsieve1"])

    logging.info("execute sanxot")
    tagfile = os.path.splitext( os.path.basename(args.pepfile) )[0] + "_tagged.xls"
    p = { "-a": "p2q_nouts", "-d": args.pepfile, "-r": tagfile, "-o": args.profile }
    if args.variance:
        p["-v"] = args.variance
    else:
        p["-V"] = "p2q_outs_infoFile.txt"
    w.sanxot(p, params["sanxot2"])


if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser(
        description='Create the relationship table for peptide2protein method',
        epilog='''
        Example:
            peptide2protein.py -i 
            -r 
            -s 
        Parameter example:
            "{aljamia1: -i [Raw_FirstScan]-[Charge] -j [Xs_127_N_126] -k [Vs_127_N_126] -f !([FASTAProteinDescription]~~TRYP_PIG||[FASTAProteinDescription]~~Krt||[FASTAProteinDescription]~~KRT) }
            {aljamia2: -i [Sequence] -j [Raw_FirstScan]-[Charge] }
            {klibrate1: -g  -f }"
        ''')
    parser.add_argument('-p',  '--pepfile',  required=True, help='Input file with the peptides')    
    parser.add_argument('-r',  '--relfile',  required=True, help='Input file with the relationship table')
    parser.add_argument('-f',  '--fdr',  required=True, help='FDR value')
    parser.add_argument('-v',  '--variance',  help='Force the variance value')
    parser.add_argument('-q',  '--profile',  required=True, help='Output file with the proteins')
    parser.add_argument('-a',  '--params',  required=True, help='Input parameters for the sub-methods')
    parser.add_argument('-t',  '--tmpdir',   help='Temporal working directory')
    parser.add_argument('-l',  '--logfile',  help='Output file with the log tracks')
    parser.add_argument('-vv', dest='verbose', action='store_true', help="Increase output verbosity")
    args = parser.parse_args()

    # set-up logging
    scriptname = os.path.splitext( os.path.basename(__file__) )[0]

    # add filehandler
    logfile = os.path.dirname(os.path.realpath(args.relfile)) + "/"+ scriptname +".log"
    if args.logfile:
        logfile = args.logfile

    # logging debug level. By default, info level
    if args.verbose:
        logging.basicConfig(filename=logfile, level=logging.DEBUG,
                            format='%(asctime)s - %(levelname)s - '+scriptname+' - %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p')
    else:
        logging.basicConfig(filename=logfile, level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - '+scriptname+' - %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p')

    # start main function
    logging.info('start script: '+"{0}".format(" ".join([x for x in sys.argv])))
    main(args)
    logging.info('end script')
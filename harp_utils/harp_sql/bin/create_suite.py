import os, sys
#import time, datetime
from datetime import datetime, timedelta
import time
from time import gmtime as gmtime
from time import strftime as tstrftime
import getpass
import argparse

import ecflow as ec

# System configuration
ECFPROJ_LIB = os.environ["ECFPROJ_LIB"]
ECFPROJ_CONFIG = os.environ["ECFPROJ_CONFIG"]
ECFPROJ_WORK   = os.environ["ECFPROJ_WORK"]

# Common
EXP = os.environ['EXP']
CLUSTER = os.environ['HOSTNAME']
USER = os.environ["USER"]
ECF_HOST = os.environ["ECF_HOST"]
ECF_PORT = os.environ["ECF_PORT"]

# Force replace suite
FORCE = os.environ["FORCE"]
# Archive
#ARCHIVE = os.environ["ARCHIVE"]

# Start YMD/HH
# This will setup the first date of processing. If it is not set it will not work!
START_DTG = os.environ["START_DTG"]
#Test: hardcoded here
#START_DTG = "20230307"
start_ymd = START_DTG[0:8]
start_yyyy = START_DTG[0:4]
start_mm = START_DTG[4:6]
start_hh = START_DTG[8:10]

# List of streams to process
ecfproj_streams = os.getenv('ECFPROJ_STREAMS').split(',')

# Read in other options from the config file
DELAY_VFLD = os.environ["DELAY_VFLD"] # In days
DELAY_VOBS = os.environ["DELAY_VOBS"] # In days
DELAY_GRIB = os.environ["DELAY_GRIB"] # In days
DELAY_ARCHIVE_SQLITE = os.environ["DELAY_ARCHIVE_SQLITE"] # In months
ICM_MIN = os.environ["ICM_MIN"]
ICM_INT = os.environ["ICM_INT"]
ICM_MAX = os.environ["ICM_MAX"]

defs = ec.Defs()
suite = defs.add_suite(EXP)
suite.add_variable("USER",           USER)
suite.add_variable("ECFPROJ_LIB",       ECFPROJ_LIB)
suite.add_variable("ECFPROJ_CONFIG",     ECFPROJ_CONFIG)
suite.add_variable("EXP",            EXP)
suite.add_variable("ECF_HOME",       "%s"%ECFPROJ_WORK)
suite.add_variable("ECF_INCLUDE",    "%s/share/ecf"%ECFPROJ_LIB)
suite.add_variable("ECF_FILES",      "%s/share/ecf"%ECFPROJ_LIB)

SCHOST= 'hpc'
ECF_JOB_CMD = '%TROIKA% -c %TROIKA_CONFIG% submit -o %ECF_JOBOUT% %SCHOST% %ECF_JOB%'
ECF_KILL_CMD = '%TROIKA% -c %TROIKA_CONFIG% kill %SCHOST% %ECF_JOB%'
ECF_STATUS_CMD = '%TROIKA% -c %TROIKA_CONFIG% monitor %SCHOST% %ECF_JOB%'
suite.add_variable("SCHOST",            SCHOST)
suite.add_variable("ECF_JOB_CMD",       ECF_JOB_CMD)
suite.add_variable("ECF_KILL_CMD",      ECF_KILL_CMD)
suite.add_variable("ECF_STATUS_CMD",    ECF_STATUS_CMD)
suite.add_variable("QUEUE",             'nf')
suite.add_variable("SUB_H",             "sbatch." + ECFPROJ_CONFIG + ".h")
# Added
suite.add_variable("TASK",           "")
suite.add_variable("YMD",            "")
suite.add_variable("HH",             "")
suite.add_variable("ICM_MIN",        ICM_MIN)
suite.add_variable("ICM_INT",        ICM_INT)
suite.add_variable("ICM_MAX",        ICM_MAX)

# Add common "par" limit to jobs
suite.add_limit("par", 10)

# Create the vobs conversion family
def create_sqlite_vobs(run_hhmm):
    run = ec.Family("run")
    run.add_inlimit("par")
    run.add_repeat(ec.RepeatDate("YMD",int(start_ymd), 20990101, 1))
    #run.add_trigger("((run:YMD + %s) < :ECF_DATE) or ((run:YMD + %s) == :ECF_DATE and :TIME >= %s)" %(DELAY_VOBS,DELAY_VOBS,run_hhmm))
    run.add_trigger(f"((run:YMD == :ECF_DATE) and (:TIME >= {run_hhmm}))")
    t1 = run.add_task("vobs2sql")

    return run

# Create the vfld conversion family
def create_sqlite_vfld(run_hhmm):
    run = ec.Family("run")
    run.add_inlimit("par")
    run.add_repeat(ec.RepeatDate("YMD",int(start_ymd), 20990101, 1))
    #run.add_trigger("((run:YMD + %s) < :ECF_DATE) or ((run:YMD + %s) == :ECF_DATE and :TIME >= %s)" %(DELAY_VFLD,DELAY_VFLD,run_hhmm))
    run.add_trigger(f"((run:YMD == :ECF_DATE) and (:TIME >= {run_hhmm}))") #%(DELAY_VFLD,DELAY_VFLD,run_hhmm))
    t1 = run.add_task("vfld2sql")

    return run


# Create the families in the suite
for ecfproj_stream in ecfproj_streams:
    fs = suite.add_family(ecfproj_stream)
    fs.add_variable("ECFPROJ_STREAM", ecfproj_stream)
    if (ecfproj_stream == "DMI_OBS"):
        run_hhmm="0900"
        fs.add_family(create_sqlite_vobs(run_hhmm))
    elif ((ecfproj_stream == "enea43h22mbr000") or (ecfproj_stream == "enea43h22opr") or (ecfproj_stream == "MEPS_prodmbr000") or (ecfproj_stream == "EC9") or (ecfproj_stream == "ecds_v2")):
        run_hhmm="0900"
        fs.add_family(create_sqlite_vfld(run_hhmm))
    else:
        print("ERROR: The stream %s is not considered, aborting" %(ecfproj_stream))
        exit(2)

if __name__=="__main__":
    # Define a client object with the target ecFlow server
    client = ec.Client(ECF_HOST, ECF_PORT)
    
    # Save the definition to a .def file
    print("Saving definition to file '%s.def'"%EXP)
    defs.save_as_defs("%s.def"%EXP)
    # If the force flag is set, load the suite regardless of whether an
    # experiment of the same name exists in the ecFlow server
    if FORCE == "True":
        client.load(defs, force=True)
    else:
        try:
            client.load(defs, force=False)
        except:
            print("ERROR: Could not load %s on %s@%s" %(suite.name(), ECF_HOST, ECF_PORT))
            print("Use the force option to replace an existing suite:")
            print("    ./ecfproj_start -f")
            exit(1)
    
    print("loading on %s@%s" %(ECF_HOST,ECF_PORT))
    
    # Suspend the suite to allow cycles to be forced complete
    client.suspend("/%s" %suite.name())
    # Begin the suite
    client.begin_suite("/%s" % suite.name(), True)
    
    # Resume the suite
    client.resume("/%s" %suite.name())
    
    exit(0)

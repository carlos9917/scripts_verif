import argparse
import netCDF4
import numpy as np
import sys

import Input

def main():
    ''' 
    Store the observations from Bjarne in a netcdf format
    '''
    parser = argparse.ArgumentParser(prog="text2verif", description="Convert obs text to NetCDF format")
    parser.add_argument('ifile', type=str, help="obs text file (input)")
    parser.add_argument('ofile', type=str, help="NetCDF file (output)")
    parser.add_argument('--debug', help='Print debug information', action="store_true")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    obsinput = Input.get_input(args.ifile)
    times = obsinput.times
    leadtimes = obsinput.leadtimes
    stations = obsinput.stations
    variable = obsinput.variable

    output = netCDF4.Dataset(args.ofile, 'w')
    output.createDimension("time", None)
    output.createDimension("leadtime", len(leadtimes))
    output.createDimension("station", len(stations))

    vTime = output.createVariable("time", "i4", ("time",))
    vOffset = output.createVariable("leadtime", "f4", ("leadtime",))
    vStation = output.createVariable("station", "i4", ("station",))
    vLat = output.createVariable("lat", "f4", ("station",))
    vLon = output.createVariable("lon", "f4", ("station",))
    vElev = output.createVariable("altitude", "f4", ("station",))
    vobs = output.createVariable("obs", "f4", ("time", "leadtime", "station"))

    output.standard_name = variable.name
    output.units = unit = variable.units.replace("$", "")

    vobs[:] = obsinput.obs
    vTime[:] = obsinput.times
    vOffset[:] = obsinput.leadtimes
    vStation[:] = [s.id for s in stations]
    vLat[:] = [s.lat for s in stations]
    vLon[:] = [s.lon for s in stations]
    vElev[:] = [s.elev for s in stations]
    output.Conventions = "netcdf 4.0"
    output.close()


if __name__ == '__main__':
    main()

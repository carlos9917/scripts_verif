#!/usr/bin/env bash
#SBATCH --error=danra_ecp_%j.err
#SBATCH --output=danra_ecp_%j.out
#SBATCH --job-name=danra_copy

DEF_USER=nhe
#if [ -z $1 ]; then
#  echo "Please provide stream and period"
#  echo "Example: carra2_spinup 199201"
#  echo "For ERA5 use ERA5 as stream: ERA5 199201"
#  echo "Extra: add user as 3rd argument if stream not in $DEF_USER"
#  exit 1
#else
#  STREAM=$1
#  PERIOD=$2
#  [ -z $3 ] && USER=$DEF_USER || USER=$3
#fi


copy_CARRA2()
{
  DEST=/ec/res4/scratch/nhd/verification/vfld/CARRA2/$STREAM/
  ORIG=ec:/fac2/CARRA2/vfld/$STREAM/$PERIOD 
  echo "ecfscopying $ORIG to $DEST/$PERIOD and unpacking... (this might take a while)"
  ecfsdir $ORIG $DEST/$PERIOD
  mv $DEST/$PERIOD/* $DEST
  rmdir $DEST/$PERIOD
  cd $DEST
  tar xvf vfld${STREAM}${PERIOD}.tar
  rm vfld${STREAM}${PERIOD}.tar
  for TB in vfld${STREAM}${PERIOD}*.tar.gz; do
    tar zxvf $TB
  done
  rm vfld${STREAM}${PERIOD}*.tar.gz  
  cd -
}

copy_ERA5()
{
  DEST=/ec/res4/scratch/nhd/verification/vfld/ERA5
  [ ! -d $DEST ] && mkdir $DEST
  if [[ $YYYY <  2000 ]] ; then
    [ -d $DEST/$YYYY ] && rmdir $DEST/$YYYY
    ORIG=ec:/hirlam/oprint/ECMWF/ERA5/$YYYY/$PERIOD
    echo "ecfscopying $ORIG to $DEST/$PERIOD and unpacking... (this might take a while)"
    ecfsdir $ORIG $DEST/$YYYY
    mv $DEST/$YYYY/* $DEST
    rmdir $DEST/$YYYY
  else
  [ -d $DEST/$PERIOD ] && rmdir $DEST/$PERIOD
    ecfsdir ec:/hirlam/oprint/ECMWF/ERA5/$YYYY/$PERIOD $DEST/$PERIOD
    mv $DEST/$PERIOD/* $DEST
    rmdir $DEST/$PERIOD
  fi
}
copy_old_obs()
{
  echo "Old observation data copied by years. Copying $YYYY"
  DEST=/ec/res4/scratch/nhd/verification/DMI_data/vobs/MARS
  ORIG=ec:/hirlam/oprint/OBSMARS/$YYYY
  [ -d $DEST/$YYYY ] && rmdir $DEST/$YYYY
  ecfsdir $ORIG $DEST/$YYYY
  mv $DEST/$YYYY/* $DEST
  rmdir $DEST/$YYYY

}

copy_new_obs()
{
  echo "Recent observation data copied by period $PERIOD"
  DEST=/ec/res4/scratch/nhd/verification/DMI_data/vobs/MARS
  ORIG=ec:/hirlam/oprint/OBS4/${PERIOD}.tar.gz
  [ -d $DEST/$YYYY ] && rmdir $DEST/$YYYY
  echo "Copying $ORIG to $DEST"
  ecp $ORIG $DEST
  cd $DEST
  tar zxvf ${PERIOD}.tar.gz 
  rm ${PERIOD}.tar.gz
  #sometimes it is all packed in a diff directory. Move them
  if [ -d ${PERIOD} ]; then
    mv $PERIOD/* .
    rmdir $PERIOD
  fi
  cd -

}

# variable to save CLI arguments
dataset=""
PERIOD=""

# Function to display usage
usage() {
    echo "Usage: $0 [-e|-c|-v|-n] <period> [optional_arguments...]"
    echo "  -e: Use ERA5 dataset"
    echo "  -c: Use CARRA2 dataset"
    echo "  -o: Use vobs old dataset (up to ca. 1996)"
    echo "  -n: Use vobs new dataset"
    echo "  <period>: A mandatory second argument for the period (YYYYMM, ie 198909)"
    exit 1
}

# Parse command line options
while getopts ":e:c:o:n:" opt; do
  case $opt in
    e)
      dataset="ERA5"
      PERIOD="$OPTARG"
      ;;
    c)
      dataset="CARRA2"
      PERIOD="$OPTARG"
      ;;
    o)
      dataset="vobs_old"
      PERIOD="$OPTARG"
      ;;
    n)
      dataset="vobs_new"
      PERIOD="$OPTARG"
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      usage
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      usage
      ;;
  esac
done

# Shift the parsed options out of the argument list
shift $((OPTIND-1))

echo $dataset
echo $OPTARG
# Check if a dataset was selected and if the required argument is provided
if [ -z "$dataset" ] || [ -z "$PERIOD" ]; then
  echo "Error: You must select a dataset and provide a required argument."
  usage
fi

# Print the selected dataset and required argument
echo "Selected dataset: $dataset"
echo "period: $PERIOD"

# Print any additional arguments
#if [ $# -gt 0 ]; then
#  echo "Additional argument for period: $@"
#fi

declare -i YYYY=${PERIOD:0:4}

# Add your processing logic here
case $dataset in
  "ERA5")
    echo "Copying ERA5 dataset for $PERIOD..."
    copy_ERA5
    ;;
  "CARRA2")
    echo "Copying CARRA2 dataset for $PERIOD..."
    STREAM=carra2_spinup
    copy_CARRA2
    ;;
  "vobs_old")
    echo "Copying old vobs dataset for $PERIOD..."
    copy_old_obs
    ;;
  "vobs_new")
    echo "Copying new vobs dataset for $PERIOD..."
    copy_new_obs
    ;;
esac


#if [ $STREAM == "ERA5" ]; then
#  copy_ERA5
#else 
#  copy_CARRA2
#fi

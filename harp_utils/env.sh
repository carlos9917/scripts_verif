#!/usr/bin/env bash
# Set some env variables depending on the machine
#
dmi_servers=("glatmodelvm1p","volta")
if [[ " ${dmi_servers[@]} " =~ " $HOSTNAME " ]]; then
  echo "$HOSTNAME in DMI servers: ${dmi_servers[@]}"
  HARPV=/data/users/cap/R/harp-verif
else
  echo "$HOSTNAME not in DMI servers: ${dmi_servers[@]}, hence assuming we are in ATOS"	
  HARPV=$HOME/R/harp-verif
fi

export HARPV
echo "Location of harp-verif scripts: $HARPV"

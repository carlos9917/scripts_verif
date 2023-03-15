# Some generic varibales to load
TASK=%TASK%             export TASK
ECF_TRYNO=%ECF_TRYNO%   export ECF_TRYNO
HH=%HH%                 export HH
YMD=%YMD%               export YMD
ECFPROJ_LIB=%ECFPROJ_LIB%     export ECFPROJ_LIB
EXP=%EXP%               export EXP
# HH needs two characters. From that, define DTG etc
HH=`echo %HH% | awk '{printf "%%2.2d",$1}'`
DTG=%YMD%$HH                    export DTG

YY=`echo %YMD% | awk '{print substr($1,1,4)}'`
MM=`echo %YMD% | awk '{print substr($1,5,2)}'`
DD=`echo %YMD% | awk '{print substr($1,7,2)}'`
export YY MM DD

export ECF_PARENT ECF_GRANDPARENT
ECF_PARENT=$( perl -e "@_=split('/','$ECF_NAME');"'print $_[$#_-1]' )
ECF_GRANDPARENT=$( perl -e "@_=split('/','$ECF_NAME');"'print $_[$#_-2]' )

# Source config
. %ECFPROJ_LIB%/share/config/config.%ECFPROJ_CONFIG%

# Specific variables for this project

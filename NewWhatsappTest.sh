#!/bin/bash
script='/c/Users/Swati/Desktop/rajsionic/openshift/myflaskapp/run.py'
#script=$OPENSHIFT_REPO_DIR/run.py
while :
do
echo "Script Started"
py -3 $script
#HOME=$OPENSHIFT_REPO_DIR python $script
echo "Script Ended"
done



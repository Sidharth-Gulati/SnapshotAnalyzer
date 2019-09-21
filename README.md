# SnapshotAnalyzer
Project to manage AWS EC2 instance snapshots

# About

This project uses thee boto3 package to manage EC2 instances snapshots.

# Prerequisites

Install the boto3 package using  'conda install -c anaconda boto3' if using anaconda.

Installing the click package using 'conda install -c anaconda click' if using anaconda.

# Configuration

shots uses aws configure to access the configuration file created by AWS cli
Eg : aws configure --profile Your_Name

A --profile sub-command has been provided in the console script to configure AWS profile : 'python shots.py --profile=Sidharth_Gulati instances list'

A --region sub-command has been provided in the console script to set the region of the instance : 'python shots.py --region=us-east-1 instances list'

-- AWS configure is to be used before this to setup Access key and Secret Access Key.

# Running

General Pattern -- python shots.py *command* *sub-command*

Run the program using the command 'python shots.py' from the directory.

The --uni tag is optinal

The --force tag is optional for no tag value being provided -- It's available for starting, stopping, terminating, snapshotting and rebooting EC2 instances

## For EC2 instances command--- 

To use the Listing sub-command : 'python shots.py instances list --uni=*Value*'

To use the Stopping sub-command : 'python shots.py instances stop --uni=*Value*'

To use the Starting sub-command : 'python shots.py instances start --uni=*Value*'

To use the Termination sub-command : 'python shots.py instances terminate --uni=*Value*'

To use the Create Snapshots sub-command : 'python shots.py instances create_snapshots --uni=*Value*'

Only previously running instances are restarted

To use the Rebooting sub-command : 'python shots.py' instances reboot --uni=*Value*'

## For EBS volumes command---

To use the Listing sub-command : 'python shots.py volumes list --uni=*Value*'

## For EC2 snapshots command---

To use the Listing sub-command : 'python shots.py snapshots list --uni=*Value*' -- This only prints the most recent snapshot

To print all the snapshots use : 'python shots.py snapshots list --all'
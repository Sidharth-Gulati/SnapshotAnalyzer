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

# Running

Run the program using the command 'python shots.py' from the directory.
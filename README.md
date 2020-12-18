# linux scan 

# Installation Instructions 

The linux scan script will pull information about the host from the system. The script will need the installation of psutils to collect cpu/memory data from the linux host. This can be installed using:

1. Create a directory on the server 
2. Download the script from github, see GitHub location section below.
3. Create a virtual environment for python : virtualvenv system
4. Activate virtual environment source system/bin/activate 
5. pip install -r requirements.txt 

This will prepare the environment to allow the script to run. 

# GitHub Location

To clone using HTTPS:

git clone https://github.com/junkshon/junkshon_linux_scan.git 

Using SSH:

git clone git@github.com:junkshon/junkshon_linux_scan.git

Or you can go directly to the GitHub repo via the web browser and download the script from there. 

https://github.com/junkshon/junkshon_linux_scan
# Running the script 

This will provide help text for the command utility:

python junkshon_linux_scan.py -h 

To run the utility type the following: 

python junkshon_linux_scan.py -d system

You have the following options:

-d system (this will get the host information including cpu/mem/os)
-d process (this will provide a running process stack)
-d top (this will provide the top processes consuming the most memory)
-d disk (this will provide a summary of disks / layout and size)
-d network (this will provide a network stack summary of connections with src/dest ip and ports, ** this may require the script to be run in sudo mode on some systems)

-d all (this will run each of the above options)

Each option will generate a csv file that is prefix with the output type e.g. system and then the servername and datetime stamp.

- example file name : systeminfo_server1234_201218_132247.csv

# Output

Once the script has been run and produed the .csv files these can be uploaded. 
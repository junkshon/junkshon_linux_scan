'''
 Linux discovery tool..
'''

import socket
from socket import AF_INET, SOCK_STREAM, SOCK_DGRAM
import platform 
import os 
import psutil
import json
import csv
import datetime
import argparse

def getListOfProcessSortedByMemory():
    '''
    Get list of running process sorted by Memory Usage
    '''
    listOfProcObjects = []
    # Iterate over the list
    for proc in psutil.process_iter():
       try:
           # Fetch process details as dict
           pinfo = proc.as_dict(attrs=['pid', 'name', 'username'])
           pinfo['vms'] = proc.memory_info().vms / (1024 * 1024)
           # Append dict to list
           listOfProcObjects.append(pinfo);
       except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
           pass
    # Sort list of dict by key vms i.e. memory usage
    listOfProcObjects = sorted(listOfProcObjects, key=lambda procObj: procObj['vms'], reverse=True)
    return listOfProcObjects

def getProcessInfo():
    '''
    Get a list of all processes runnong on the server
    '''

    processNames = []

    print('*** Create a list of all running processes ***')
    listOfProcessNames = list()
    # Iterate over all running processes
    for proc in psutil.process_iter():
       # Get process detail as dictionary
       pInfoDict = proc.as_dict(attrs=['pid', 'name', 'cpu_percent'])
       # Append dict of process detail in list
       listOfProcessNames.append(pInfoDict)
    # Iterate over the list of dictionary and print each elem
    for elem in listOfProcessNames:
        processNames.append(elem)

    return processNames

def getTopProcesses():
    '''
    Get a list of the top 10 processes by memory usage
    '''

    listOfTopProcesses = []
    
    print('*** Top 10 process with highest memory usage ***')
    listOfRunningProcess = getListOfProcessSortedByMemory()
    for elem in listOfRunningProcess[:10] :
        listOfTopProcesses.append(elem)
    
    return listOfTopProcesses

def getDiskInfo(): 
    '''
    Get disk information
    '''

    disk_info = psutil.disk_partitions()
    print('*** Getting disk information ***')  
    disks = []
    for disk in disk_info:      
        try:
            disk = {
                "name" : disk.device,
                "mount_point" : disk.mountpoint,
                "type" : disk.fstype,
                "total_size" : psutil.disk_usage(disk.mountpoint).total,
                "used_size" : psutil.disk_usage(disk.mountpoint).used,
                "percent_used" : psutil.disk_usage(disk.mountpoint).percent
            }
            disks.append(disk)
        except:
            print('Error on Disk Info')
    return disks

def getNetworkConnectionInfo(): 
    '''
    Get network information, for certain O/S this function will require sudo
    '''
    try:
        print('*** Getting network information ***')  
        network_info = []
        AD = "-"
        AF_INET6 = getattr(socket, 'AF_INET6', object())
        proto_map = {
        (AF_INET, SOCK_STREAM): 'tcp',
        (AF_INET6, SOCK_STREAM): 'tcp6',
        (AF_INET, SOCK_DGRAM): 'udp',
        (AF_INET6, SOCK_DGRAM): 'udp6',
        }

        templ = "%-5s %-30s %-30s %-13s %-6s %s"
        proc_names = {}
        for p in psutil.process_iter(['pid', 'name']):
            proc_names[p.info['pid']] = p.info['name']
        for c in psutil.net_connections(kind='inet'):
            laddr = "%s:%s" % (c.laddr)
            raddr = ""
            if c.raddr:
                raddr = "%s:%s" % (c.raddr)
            name = proc_names.get(c.pid, '?') or ''

            network = {
                "protocol": proto_map[(c.family, c.type)],
                "localaddr": laddr,
                "raddr": raddr,
                "status": c.status,
                "pid": c.pid,
                "program": name[:15]
            }
            network_info.append(network)
        return network_info
    except:
        print('Error: You need to run network discovery as sudo.')

def getSystemInfo():
    '''
    Gets base system information
    '''
    print('*** Getting base system information ***')  
    host_system = platform.uname()
    cpu_count = psutil.cpu_count()

    memory_stats = psutil.virtual_memory()
    memory_total = memory_stats.total / 1024
    memory_used = memory_stats.used / 1024
    memory_used_percent = memory_stats.percent
    
    system_info = {     
        "system_node": host_system.node,
        "system_release": host_system.release, 
        "system_version": host_system.version,
        "system_machine": host_system.machine,
        "system_processor": host_system.processor,
        "physical_proc_count": psutil.cpu_count(logical=False),
        "logical_proc_count": psutil.cpu_count(logical=True),
        "system_total_mem": memory_total,        
        "system_mem_used": memory_used,
        "system_mem_used_perc": memory_used_percent
    }
    return system_info

def fileNameGenerator(fileprefix, nodeName):
    '''
    Creates filename string
    '''
    
    suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
    extension = ".csv"
    filename = "_".join([fileprefix, nodeName, suffix]) + extension
    return filename

def writeObject(fileName, fieldDef, rowData): 
    '''
    Write single object
    '''

    with open(fileName, 'w') as fileOutput:
        writer = csv.DictWriter(fileOutput, fieldnames=fieldDef)
        writer.writeheader()
        writer.writerow(rowData)        

def writeObjectArray(fileName, fieldDef, rowData):
    '''
    Writes object array
    '''

    with open(fileName, 'w') as fileOutput:
        writer = csv.DictWriter(fileOutput, fieldnames=fieldDef)
        writer.writeheader()
        for row in rowData:
            writer.writerow(row)        

def systemInformation():
    system_info = getSystemInfo()
    nodeName = system_info['system_node']
    fieldDef = ['system_node', 'system_release', 'system_version', 'system_machine', 
                    'system_processor', 'physical_proc_count', 'logical_proc_count', 'system_total_mem', 
                    'system_mem_used', 'system_mem_used_perc']
    fileName = fileNameGenerator("systeminfo", system_info['system_node'])    
    writeObject(fileName, fieldDef, system_info)

def processInformation():
    system_info = getSystemInfo()
    nodeName = system_info['system_node']
    process_info = getProcessInfo()
    fieldDef = ['pid', 'cpu_percent', 'name']
    fileName = fileNameGenerator("processinfo", nodeName) 
    writeObjectArray(fileName, fieldDef, process_info)

def topProcessInformation():
    system_info = getSystemInfo()
    nodeName = system_info['system_node']
    top_process_info = getTopProcesses()
    fieldDef = ['pid', 'username', 'name', 'vms']
    fileName = fileNameGenerator('topinfo', nodeName)
    writeObjectArray(fileName, fieldDef, top_process_info)

def diskInformation():
    system_info = getSystemInfo()
    nodeName = system_info['system_node']
    disk_info = getDiskInfo()
    fieldDef = ['name', 'mount_point', 'type', 'total_size', 'used_size', 'percent_used']
    fileName = fileNameGenerator('diskinfo', nodeName)
    writeObjectArray(fileName, fieldDef, disk_info)  

def networkInformation():
    try:
        system_info = getSystemInfo()
        nodeName = system_info['system_node']
        connection_info = getNetworkConnectionInfo()
        fieldDef = ['protocol', 'localaddr', 'raddr', 'status', 'pid', 'program']
        fileName = fileNameGenerator('netinfo', nodeName)
        writeObjectArray(fileName, fieldDef, connection_info)
    except: 
        print("Error: Failed to collect network information")

def main(discoveryOption):
    '''
    Main function 
    '''

    if discoveryOption == 'system':
        systemInformation()
    elif discoveryOption == 'process':
        processInformation()
    elif discoveryOption == 'top':
        topProcessInformation()
    elif discoveryOption == 'disk':
        diskInformation()
    elif discoveryOption == 'network': 
        networkInformation()
    elif discoveryOption == 'all':
        systemInformation()
        processInformation()
        topProcessInformation()
        diskInformation()
        networkInformation()

if __name__ == '__main__':    
    parser = argparse.ArgumentParser(prog='junkshon_linux_scan',  description='Performs system level discovery based upon selected options and creates a CSV output')
    parser.add_argument('-d', '--discovery', type=str, choices=['system', 'process', 'top', 'disk', 'network', 'all'], help='Options include: system : system level information, \
                                                                                                                      process : process information, \
                                                                                                                      top : top 10 processes by memory, \
                                                                                                                      disk : disk information, \
                                                                                                                      network : network connection information, \
                                                                                                                      all : discover all')
                                                                                                                      
                                                                                                                
    args = parser.parse_args()
    main(args.discovery)

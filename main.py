from fastapi import FastAPI
import platform, subprocess, json


app=FastAPI()

def get_size(bytes):
    # List of suffixes and their respective power of 1024
    suffixes = ['B', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    # Calculate the index of the closest suffix to use
    index = 0
    while bytes >= 1024 and index < len(suffixes) - 1:
        bytes /= 1024
        index += 1

    # Format the value with the appropriate suffix
    size = f"{bytes:.2f} {suffixes[index]}"

    return size

def get_os_platform():
    uname = platform.uname()
    os_command = "hostnamectl | grep -i System | awk -F[:] '{print $NF}'"
    vendor_command= "hostnamectl | grep -i Vendor | awk -F[:] '{print $NF}'"
    hw_command= "hostnamectl | grep -i Model | awk -F[:] '{print $NF}'"
    try:
        os_output = subprocess.check_output(os_command, shell=True, universal_newlines=True).strip()
        vendor_output = subprocess.check_output(vendor_command, shell=True, universal_newlines=True).strip()
        hw_output = subprocess.check_output(hw_command, shell=True, universal_newlines=True).strip()
        
        os_platform= {
            "os":os_output,
            "hostname":uname.node,
            "release":uname.release,
            "vendor":vendor_output,
            "chasiss": hw_output 
        }
        return os_platform
    except subprocess.CalledProcessError as e:
        print("Error executing the command:", e)
        return None

def get_sys_info():
    cpu_command= "lscpu | egrep 'Model name|Socket|Thread'"
    core_count_cmd = "nproc --all"
    bmc_ip= 'ipmitool lan print | grep -w "IP Address"'
    host_ip= "hostname -I"
    memDDR = "vmstat -s | grep -i 'total memory'"
    try:
        #cpu type
        cpu_output = subprocess.check_output(cpu_command, shell=True, universal_newlines=True)
        #cpu type
        core_count_output = subprocess.check_output(core_count_cmd, shell=True, universal_newlines=True).strip()
        #bmc Ip
        bmc_output = subprocess.check_output(bmc_ip, shell=True, universal_newlines=True).strip()
        #host IP
        host_ip_output = subprocess.check_output(host_ip, shell=True, universal_newlines=True).strip()
        #DDR mem
        mem_output = subprocess.check_output(memDDR, shell=True, universal_newlines=True).strip()
        cpu_to_list = cpu_output.strip().splitlines()
        bmc_to_list = bmc_output.strip().splitlines()
        cpu_dict = {line.split(':')[0]: line.split(': ')[1].strip() for line in cpu_to_list}
        cpu_dict["core_count"]= int(int(core_count_output)/int((cpu_dict['Thread(s) per core']) * int(cpu_dict['Socket(s)'])))
        cpu_dict["bmc_ip"]=bmc_to_list[1].split(':')[1]
        cpu_dict['host_ip']=host_ip_output 
        cpu_dict["Total_DDR"] = get_size(int(mem_output.split()[0]))
        return cpu_dict
    except subprocess.CalledProcessError as e:
        print("Error executing the command:", e)
        return None    
    
def get_network_info():
    command = "lspci | grep Eth | grep Controller"
    try:
        output = subprocess.check_output(command, shell=True, text=True)
        output_to_list = output.strip().splitlines()
        dict_data = {line.split(' Ethernet controller: ')[0]: line.split(': ')[1] for line in output_to_list}
        return dict_data

    except subprocess.CalledProcessError as e:
        print("Error executing the command:", e)
        return None
    
def get_FPGA_info():
    fpga_cmd= "lspci | grep acc"
    try:
        #fpga type
        fpga_output = subprocess.check_output(fpga_cmd, shell=True, universal_newlines=True)
       
        fpga_to_list = fpga_output.strip().splitlines()
        fpga_dict = {line.split()[0]: line.split()[-1] for line in fpga_to_list}
        
        return fpga_dict
    except subprocess.CalledProcessError as e:
        print("Error executing the command:", e)
        return None

#gather info
platform_info = get_os_platform()
nic = get_network_info()
sys_info = get_sys_info()
fpga_info = get_FPGA_info()

uname = platform.uname()

@app.get("/")
async def root():
    return {
        "platform": platform_info,
        "Sys_info": sys_info,
        "Ethernet": nic,
        "FPGA": fpga_info
        
    }
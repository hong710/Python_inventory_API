import platform, subprocess, json

fpga_dict = {
    "0b3*": "N3000",
    "0d5*": "ACC100",
    "57c*": "ACC200"   
    }
    
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

print (get_FPGA_info())
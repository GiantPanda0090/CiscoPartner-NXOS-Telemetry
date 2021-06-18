import socket
import os
import time
import sys

#-s Start Function
def start():
    #ELK startup
    os.chdir("elasticsearch/")
    os.system("docker-compose up -d")
    #Param
    ip = "0.0.0.0"
    elastic_port = "9200"
    kibana_port = "5601"
    (result_of_check,elastic_result_of_check,kibana_result_of_check) = check_elastic_kibana_port(ip, elastic_port, kibana_port)
    retry_time = 0
    #if both port are open -> Proceed. Else -> retry
    while result_of_check != 0:
        if elastic_result_of_check !=0:
            print("Elasticsearch Port is not open, retrying the " + str(retry_time) + " times")
            (result_of_check,elastic_result_of_check,kibana_result_of_check) = check_elastic_kibana_port(ip,elastic_port, kibana_port)
            time.sleep(5)
            retry_time +=1
        elif elastic_result_of_check !=0:
            print("Kibana Port is not open, retrying the " + str(retry_time) + " times")
            (result_of_check,elastic_result_of_check,kibana_result_of_check) = check_elastic_kibana_port(ip, elastic_port, kibana_port)
            time.sleep(5)
            retry_time += 1

    #Update Mapping API
    print("Elasticsearch Port 9200 and Kibana port 5601 are both open. ")
    mapping_api = os.system("./update.sh " + ip + " " + elastic_port)

    #telegraf startup
    os.chdir("../telegraf/")
    os.system("docker-compose up -d")
    os.system("docker ps")

    print("Please access the ELK via http://<VM_IP>:5601/")

#check ELK port up or not
def check_elastic_kibana_port(ip,elastic_port, kibana_port):
    elastic_result_of_check = check_port(ip,elastic_port)
    kibana_result_of_check = check_port(ip,kibana_port)
    result_of_check = elastic_result_of_check + kibana_result_of_check
    return (result_of_check,elastic_result_of_check,kibana_result_of_check)

#check  port up or not
def check_port(ip,port):
    #https://www.kite.com/python/answers/how-to-check-if-a-network-port-is-open-in-python
    location = (ip, int(port))
    a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result_of_check = a_socket.connect_ex(location)
    return result_of_check

# -t Termination Function
def stop():
    os.system("chmod 755 stop.sh ")
    os.system("./stop.sh")

# -u Update Mapping API for dial out
def update_MappingAPI():
    os.system("chmod 755 update_mapping_api.sh ")
    os.system("./update_mapping_api.sh")

#-d deploy from local to the remote VM
def deploy_to_server(server_ip,username):
    os.system("chmod 755 deploy.sh ")
    os.system("./deploy.sh "+server_ip +" "+username)


if __name__ == "__main__":
    arg = sys.argv
    if arg[1] == "-s":
        start()
    elif arg[1] == "-t":
        stop()
    elif arg[1] == "-d":
        deploy_to_server(arg[2],arg[3])
    elif arg[1] == "-u":
        update_MappingAPI()
    elif arg[1] == "--help":
        print("Help Menu ")
        print("-s : Start")
        print("-t : Terminate")
        print("-d : Deploy to remote server(via SCP). This is an temporary solution. Suggest to deploy via git instead. Second argument \"server_ip\" Third argument \"username\"")
        print("-u : Update Mapping API Binding. Make sure you update the script file under elasticsearch/update.sh beforehand. ")
        print("END")
    else:
        print("Invalid flag. use --help flag to see the available option")








# CiscoPartner-NXOS-Telemetry
Cisco Data Center Partner Training demo setup script for NXOS Telemetry Server

## Project Structure
```
.  
├── LICENSE  
├── README.md  
├── deploy.sh  <<< -d Deploy Script
├── elasticsearch  
│   ├── docker-compose.yml  <<< Docker configuration file for ELK 
│   └── update.sh  <<< Mapping API
├── start.py  <<< Main Class
├── stop.sh  <<< -t Termination script
├── telegraf  
│   ├── cert  
│   │   └── self_sign2048.pem  <<< gNMI Certification
│   ├── conf  
│   │   ├── telegraf_in.conf  <<< Dial in configurations
│   │   └── telegraf_out.conf  <<< Dial out configurations
│   └── docker-compose.yml  <<< Docker configuration file for telegraf 
├── update_mapping_api.sh <<< -u Update Mapping API script
```


## Prequisition
The following are the tested enviorment during Development
Operating System:  
• Ubuntu 64-bit  
Software Prequisition:  
• Docker 20.10.6, build 370c289  
• Docker-Compose 1.25.0  
• Python 3.8.5  
Hardware Prequisition:  
• 4 cores  
• 16GB RAM  
• At least 50 GB available after OS installations. Suggest to have 100 GB available for storing history data at data
store.

### Install Software Prequisition
Docker Engine  
• Please follow the guide from official docker website  
<https://docs.docker.com/engine/install/ubuntu/>  
Docker-Compose 1.25.0  
• Use command “sudo apt-get install docker-compose” or follow the guide from official docker website  
<https://docs.docker.com/compose/install/>  
Python 3.8.5  
• This should be pre-install by ubuntu already. If not, follow the guide from phoenixNap  
<https://phoenixnap.com/kb/how-to-install-python-3-ubuntu>

## Build
This section will introduce how to build the code.  

### Collector - Telegraf
We will mark the one that is mandatory to review with (Mandatory) Tag and the one that can be used with default config via (Optional) Tag.

#### Output Plugin - Elasticsearch
Modify “telegraf/conf/telegraf_out.conf” as the steps stated below.  
(Optional) Modify the following pararmeter in  “outputs.elasticsearch”
```
urls = [ "http://elasticsearch:9200" ] # required. <<< Change this to elasticsearch. We are using Docker internal Network DNS here. 
## Elasticsearch client timeout, defaults to "5s" if not set.
index_name = "<Templet Name>" <<< The name that will be used ad index name in ELK 
## If enabled it will create a recommended index template for telegraf indexes
```

#### Dial In
Modify “telegraf/conf/telegraf_in.conf” as the steps stated below  
(Madatory) Setup “inputs.gnmi” based on the following structure
```
# ## Address and port of the gNMI GRPC server 
addresses = ["<Switch IP>:<Port Default:50051>"]
#
# ## define credentials
username = "<Username of the Switch>" 
password = "<Password of the Switch> "
```

(Optional) Setup subscription of interest via “inputs.gnmi.subscription”. the default setting extract Interface counters via xPath “interfaces/interface/state/counters” under Openconfig every 10 second.
```
# ## Name of the measurement that will be emitted 
name = "<Name of interest>"

# ## YANG models can be found e.g. here: <https://github.com/YangModels/yang/tree/master/vendor/cisco/xr>
origin = "<YANG Module>"
path = "<Yang Path>" <<< Check chatper “Yang Suit for Dial In xPath” to learn how to construct xpath
# # Subscription mode (one of: "target_defined", "sample", "on_change") and interval
subscription_mode = "<Push Type>" 
sample_interval = "<interval in sec>”
```
##### Switch side config
(Madatory) Download the OpenConfig SMU via the link  
<https://devhub.cisco.com/artifactory/webapp/#/artifacts/browse/tree/Properties/open-nxos-agents/9.3-7/x86_64/mtx-openconfig-all-1.0.0.0-9.3.7.lib32_n9000.rpm>  
(Madatory) Install the SMU via command
```
install add mtx-openconfig-all-1.0.0.182-9.3.5.lib32_n9000.rpm activate
```
(Madatory) gNMI requires an OpenSSH certificate for authentication purposes. We need to generate from the switch. The certification can be generated and enabled by the switch via the command below:
```
feature bash-shell
run bash sudo su
cd /bootflash/
openssl req -x509 -newkey rsa:2048 -keyout self_sign2048.key -out self_sign2048.pem -days 365 -nodes This will give us the following file
>>>> self_sign2048.key
>>>> self_sign2048.pem

openssl pkcs12 -export -out self_sign2048.pfx -inkey self_sign2048.key -in self_sign2048.pem -certfile self_sign2048.pem -password pass:Ciscolab123! We will get the final pfx here that will be used by the switch
>>>> self_sign2048.pfx

Enable the gRPC and active the pfx certificate
feature grpc
crypto ca trustpoint mytrustpoint
crypto ca import mytrustpoint pkcs12 self_sign2048.pfx Ciscolab123!
grpc gnmi max-concurrent-calls 16 
grpc use-vrf default
grpc certificate mytrustpoint
```

(Madatory) Copy the “self_sign2048.pem” from the switch into the “telegraf/cert/” path in the Project Folder.  
More Detail Regarding Dial-In can be found in Cisco Guide  
<https://www.cisco.com/c/en/us/products/collateral/switches/nexus-9000-series-switches/white-paper-c11-744191.html>

#### Dial Out
Modify “telegraf/conf/telegraf_out.conf” as the step stated below  
(Optional) Setup “ inputs.cisco_telemetry_mdt” with the structure below

```
# ## Telemetry transport can be "tcp" or "grpc". TLS is only supported when # ## using the grpc transport.
transport = "<encoding mode>"
```

##### Switch side config
(Madatory) Ochestrate or Config the following command via CLI
```
ntp server <NTP Server> prefer use-vrf management
feature telemetry

telemetry
    destination-group 1
    use-vrf management
    ip address <TOLD Server IP address> port 50001 protocol <encoding method> encoding GPB
    sensor-group 1
        path sys < use xPATH here for example “/bgp/inst/dom-default”> depth 0
    sensor-group 2
        data-source NX-API
        path "<CLI show command>" depth 0
    subscription 1
        dst-grp 1
        snsr-grp 1 sample-interval <Streaming Interval per ms>
    subscription 2
        dst-grp 1
        snsr-grp 2 sample-interval <Streaming Interval per ms>

```

More Detail Regarding Dial Out can be found in Cisco Guide  
<https://www.cisco.com/c/en/us/td/docs/switches/datacenter/nexus9000/sw/7-x/programmability/guide/b_Cisco_Nexus_9000_Series_NX-OS_Programmability_Guide_7x/b_Cisco_Nexus_9000_Series_NX-OS_Programmability_Guide_7x_chapter_011000.html>

Other telegraf input plugin can be found via the link  
<https://docs.influxdata.com/telegraf/v1.18/plugins/>

### Data Store and Visualization – ELK Stack
We use the ELK Mapping API here. To modify the Mapping API for parsing, please modify the ‘elasticsearch/update.sh” file.  
For each Mapping API, we use the curl command to push it into the elasticsearch. The command itself looks like this.
```
curl -XPUT "$1:$2/telegraf-out/_doc/_mapping?include_type_name=true" -H "Content-Type: application/json" -d' {"_doc"
: {"properties" : {"show processes cpu sort": {"properties":{"kernel_percent": {"type": "double"}}}}}}'
```
More detail regarding to the Mapping API can be found via link  
<https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-put-mapping.html>


## Run the code
The code has 4 different modes. The usage of these modes can be seen via the command
```
python3 start.py –help
```

Sample output as below:
```
Help Menu  
-s : Start  
-t : Terminate
-d : Deploy to remote server. Second argument "server_ip"
-u : Update Mapping API Binding. Make sure you update the script file under elasticsearch/update.sh beforehand. END
```
### Passowrdless login
generate an SSH Public Key
```
ssh-keygen -t rsa
```
Import to the remote deployment server.

### Start Up The Enviorment
```
python3 start.py -s
```
### Update the Mapping API for ElasticSearch for Dial Out
```
python3 start.py -u
```

### Terminate The Enviorment
```
python3 start.py -t
```


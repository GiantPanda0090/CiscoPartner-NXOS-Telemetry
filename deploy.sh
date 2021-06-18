#!/bin/bash
## -d Deploy Script

secs=$((10))
while [ $secs -gt 0 ]; do
   echo -ne "Code deploy towards $1 server in $secs\033[0K second\r"
   sleep 1
   : $((secs--))
done

printf "\n"

cat $HOME/.ssh/id_rsa.pub | ssh $2@$1 'cat >> .ssh/authorized_keys'

echo "Deploying code towards server $1"
ssh $2@$1 "rm -rf telemetry/telemetry"
scp -r $PWD $2@$1:telemetry/telemetry
ssh $2@$1 "rm -rf telemetry/telemetry/venv"

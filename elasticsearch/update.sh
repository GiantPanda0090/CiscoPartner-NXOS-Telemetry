secs=$((30))
while [ $secs -gt 0 ]; do
   echo -ne "Start update Mapping API towards $1:$2 in $secs\033[0K second\r"
   sleep 1
   : $((secs--))
done

echo "Mapping API query towards: $1:$2"

##Insert the parameter you would like to cast via Mapping API here
##For example

##Create Dataset
#curl -XPUT  "$1:$2/telegraf-out/" -H "Content-Type: application/json" -d '{ "settings" : { "index.mapping.total_fields.limit" : 1000000000, "number_of_shards" : 1, "number_of_replicas" : 1 } }'

##Unix time to Date Time
#curl -XPUT  "$1:$2/telegraf-out/_doc/_mapping?include_type_name=true" -H "Content-Type: application/json" -d' { "_doc" : { "properties" : { "sys/intf.postDate" : {"type" : "date", "format": "yyyy-MM-dd HH:mm:ss z||yyyy-MM-dd||epoch_millis||yyyy-MM-dd HH:mm:ss.SSS z" } } } }'

##Cast Data Structure
# curl -XPUT  "$1:$2/telegraf-out/_doc/_mapping?include_type_name=true" -H "Content-Type: application/json" -d' {"_doc" : {"properties" : {"show processes cpu sort": {"properties":{"user_percent": {"type": "double"}}}}}}'


echo -e "\nMapping API ENDED"




#!/usr/bin/env bash

# Run Python shoppingcart here
python shoppingcart/shopping_cart.py &
pid=$! 
echo "Start python shoppingcart user-function with pid $pid"
sleep 3

# The host network usually doesn't work on MacOS systems 
# so we should address this issue and use the docker's internal network when the system is Mac
echo "Starting Cloudstate proxy in development mode via docker"
docker run -d --name cloudstate-proxy --net=host -e USER_FUNCTION_PORT=8090 cloudstateio/cloudstate-proxy-dev-mode

echo "Starting TCK via docker"
docker run --rm --name cloudstate-tck --net=host cloudstateio/cloudstate-tck
status=$?

echo "Removing cloudstate-proxy docker image"
docker rm -f cloudstate-proxy

echo "Stopping Shoppingcart user-function"
kill -9 $pid

exit $status

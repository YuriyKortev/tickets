#!/bin/bash

set -e

host="neo4j"
port="7474"
cmd="$@"

>&2 echo "!!!!!!!! Check neo4j for available !!!!!!!!"

until curl http://"$host":"$port"; do
  >&2 echo "neo4j is unavailable - sleeping"
  sleep 5
done

>&2 echo "neo4j is up - executing command"

exec $cmd
#!/bin/bash
HASH=$(cat .pass | md5sum | cut -d ' ' -f 1)

while [ "$#" -gt 0 ]; do
  case "$1" in
    -e) email="$2"; shift 2;;

    --email=*) name="${1#*=}"; shift 1;;
  esac
done

EMAIL=$email

echo 'Obtaining token...'
accessToken=$(curl -X POST https://global-robot-api.unitree.com/login/email -d "email=$EMAIL&password=$HASH" | jq .data.accessToken | tr -d '"')
go2IP=$(getent ahostsv4 Unitree.local | awk '{print $1}' | sort | uniq)

echo -n "GO2_TOKEN=$accessToken" > app/src/.env
echo -e "\nGO2_IP=$go2IP" >> app/src/.env
export GO2_TOKEN=$accessToken

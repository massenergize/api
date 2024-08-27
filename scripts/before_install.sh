#!/bin/bash

while [ ! -f /webapps/server_is_ready ]; do
  sleep 5
done


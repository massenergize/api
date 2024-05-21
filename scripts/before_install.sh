#!/bin/bash

while [ ! -f /tmp/server_is_ready ]; do
  sleep 5
done


#!/bin/bash

# Ask for the user's confirmation
echo "Are you sure you want to execute the make command? (y/n)"
read confirm

# Convert the input to lower case
confirm=$(echo $confirm | tr '[:upper:]' '[:lower:]')

# Check if the user confirmed
if [[ $confirm == 'y' || $confirm == 'yes' ]]; then
    # Execute the make command
    make $@
else
    # Inform the user that the operation was cancelled
    echo "Operation cancelled."
fi
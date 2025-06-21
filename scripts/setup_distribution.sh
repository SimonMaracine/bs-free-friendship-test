#! /usr/bin/bash

KEY=$1
LOCK=../distribution.lock

if [[ $KEY = "" ]]; then
    echo "Please provide a key"
    exit 1
fi

if [[ -f $LOCK ]]; then
    echo "Cannot setup twice"
    exit 1
fi

echo "-- Creating environment..."
./create_environment.sh
source ../.env/bin/activate

echo "-- Installing dependencies..."
./install_dependencies.sh
./install_production_server.sh

echo "-- Configuring and initializing database..."
mkdir ../instance
echo "SECRET_KEY = '$KEY'" >> ../instance/configuration.py
./initialize_database.sh

echo "-- Done."
touch $LOCK

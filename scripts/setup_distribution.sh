#! /usr/bin/bash

./create_environment.sh
source ../.env/bin/activate

./install_dependencies.sh
./install_production_server.sh

mkdir ../instance
./generate_secret_key.py >> ../instance/configuration.py
./initialize_database.sh

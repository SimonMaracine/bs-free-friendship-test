#! /usr/bin/bash

cd ..

scripts/create_environment.sh
source .env/bin/activate

scripts/install_dependencies.sh
scripts/install_production_server.sh

mkdir instance
scripts/generate_secret_key.py >> instance/configuration.py
scripts/initialize_database.sh

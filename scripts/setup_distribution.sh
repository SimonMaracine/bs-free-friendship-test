#! /usr/bin/bash

echo "Creating environment..."
./create_environment.sh
source ../.env/bin/activate

echo "Installing dependencies..."
./install_dependencies.sh
./install_production_server.sh

echo "Configuring and initializing database..."
mkdir ../instance
./generate_secret_key.py >> ../instance/configuration.py
./initialize_database.sh

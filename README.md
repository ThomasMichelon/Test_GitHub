# Nabla Core cfdshaper Simulation

Docker image and scripts to run a cfdshaper simulation on AWS Batch.

To build image:
docker build -t nabla-core-cfdshaper-simulation .

To execute container:
docker-compose -f docker-compose.dev.yml up

To enter container (when setting docker-compose to tail -f ...):
docker exec -u 0 -it nabla-core-cfdshaper-simulation /bin/bash
source $NVM_DIR/nvm.sh

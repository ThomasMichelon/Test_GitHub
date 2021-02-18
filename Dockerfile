FROM ubuntu:bionic

# Set the env
ENV LANG=C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive
ENV NVM_VERSION v0.36.0
ENV NODE_VERSION v12.19.0
ENV NVM_DIR /usr/local/nvm

SHELL ["/bin/bash", "-c", "-l"]

RUN apt-get update; \
  apt-get full-upgrade -y; \
  apt-get install -y --no-install-recommends \
  curl \
  wget \
  gnupg2 \
  software-properties-common;

# Install the required packages
RUN curl -fsSL http://dl.openfoam.org/gpg.key | apt-key add -;\
  add-apt-repository http://dl.openfoam.org/ubuntu ;\
  apt-get install -y --no-install-recommends \
  openfoam7 \
  ca-certificates \
  vim \
  unzip \
  ssh \
  libboost-dev \
  libboost-all-dev \
  libblas-dev \
  liblapack-dev \
  libopenmpi-dev \
  openmpi-bin \
  openmpi-doc \
  xorg-dev \
  libmotif-dev \
  libgl1-mesa-dev \
  sudo \
  python3.8 \
  python3-pip \
  xvfb; \
  # Probably not needed
  # nfs-common; \
  apt-get clean; \
  rm -rf /var/lib/apt/lists/*;

# Add and run the disable hyperthreading script
COPY disable_hyperthreading.sh .
RUN ./disable_hyperthreading.sh

# Add the nabla user
RUN useradd -ms /bin/bash nabla

# Install nvm
RUN mkdir $NVM_DIR
RUN curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.33.11/install.sh | bash

# Add node and npm to path so the commands are available
ENV NODE_PATH $NVM_DIR/$NODE_VERSION/lib/node_modules
ENV PATH $NVM_DIR/versions/node/$NODE_VERSION/bin:$PATH

# Install nvm, node and yarn
RUN echo "source $NVM_DIR/nvm.sh && \
  nvm install $NODE_VERSION && \
  nvm alias default $NODE_VERSION && \
  nvm use default && \
  npm install -g yarn" | bash

# Install the aws-cli
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install

# Set the workdir to nabla home directory
WORKDIR /home/nabla

# Change user to nabla
USER nabla

# Install python packages
RUN python3.8 -m pip install pip &&\
  python3.8 -m pip install setuptools &&\
  python3.8 -m pip install vtk==9.0.1 numpy-stl matplotlib pyvista pygltflib

# Copy the OpenFoam folder
COPY OpenFoam/ /home/nabla/OpenFoam

# Copy the package.json and the replace script
COPY package.json /home/nabla/package.json
COPY replace.js /home/nabla/replace.js
COPY run.sh /home/nabla/run.sh

# Fetch the replace script dependencies
RUN yarn install

# Set the script as entrypoint
CMD ["./run.sh"]

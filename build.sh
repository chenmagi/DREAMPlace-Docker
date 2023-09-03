#!/bin/bash

if [ ! -f 'DREAMPlace/Dockerfile.org' ]; then
  mv DREAMPlace/Dockerfile DREAMPlace/Dockerfile.org
fi
cp Dockerfile DREAMPlace/Dockerfile
cp -avrf busydocker DREAMPlace/

pushd DREAMPlace/busydocker
if [ ! -f 'ssh_key_busydocker.pub' ]; then
  ssh-keygen -f ssh_key_busydocker -N ''
  echo 'Generated ssh-key for auto login'
  echo 'Remember to edit your ssh config file (~/.ssh/config)'
fi
popd
pushd DREAMPlace
docker build . --file Dockerfile --tag busydocker/dreamplace:cuda
popd

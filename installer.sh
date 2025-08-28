#!/bin/bash

amass_ver="https://github.com/owasp-amass/amass/releases/download/v3.20.0/amass_linux_amd64.zip"
amass_path=$(which amass)
dnsrecon_ver="https://github.com/darkoperator/dnsrecon/archive/refs/tags/1.1.3.zip"
dnsrecon_dir=$(readlink -f $(which dnsrecon) | rev | sed 's-^[^/]*--' | rev)
path="$(which ls | rev | sed 's-^[^/]*--' | rev)"

echo "##############################################################"
echo "  Copying .openpipes folder to your \$HOME ... "
echo "##############################################################"

cp -r .openpipes/ $HOME
cp -r .openpipes_cache/ $HOME

echo "##############################################################"
echo "  Copying scripts to folder $path ... "
echo "  Please enter sudo credentials ... "
echo "##############################################################"

sudo cp $HOME/.openpipes/scripts/*.sh $path

echo "##############################################################"
echo "  Fixing amass and dnsrecon versions ... "
echo "##############################################################"

wget $amass_ver && unzip amass_linux_amd64.zip && sudo cp amass_linux_amd64/amass $amass_path
wget $dnsrecon_ver && unzip 1.1.3.zip && sudo rm -rf $dnsrecon_dir && sudo mkdir -p $dnsrecon_dir && sudo cp -r dnsrecon-1.1.3/* $dnsrecon_dir

# dependencies=("")
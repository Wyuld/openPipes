#!/bin/bash

read -p "Please, enter the path to your \$PATH (or press [ENTER] to use $(echo $PATH | cut -d ":" -f1)): " path
path=${path:-$(echo $PATH | cut -d ":" -f1)}

if [ '$path' = 'NULL' ]; then
    path=$(echo $PATH | cut -d ":" -f1)
fi

echo $path

amass_ver="https://github.com/owasp-amass/amass/releases/download/v3.20.0/amass_linux_amd64.zip"
dnsrecon_ver="https://github.com/darkoperator/dnsrecon/archive/refs/tags/1.1.3.zip"
dnsrecon_dir="$(which dnsrecon)"

echo "##############################################################"
echo "  Copying .openpipes folder to your \$HOME ... "
echo "##############################################################"

cp ./.openpipes $HOME

echo "##############################################################"
echo "  Copying scripts to folder $path ... "
echo "  Please enter sudo credentials ... "
echo "##############################################################"

sudo cp $HOME/.openpipes/scripts/* $path

echo "##############################################################"
echo "  Fixing amass and dnsrecon versions    "
echo "##############################################################"

wget $amass_ver && unzip amass_linux_amd64.zip && sudo cp amass_linux_x_amd64/amass $path
wget $dnsrecon_ver && unzip && 1.1.3.zip && sudo rm -rf $dnsrecon_dir && sudo cp -r 1.1.3/* $dnsrecon_dir

# dependencies=("")
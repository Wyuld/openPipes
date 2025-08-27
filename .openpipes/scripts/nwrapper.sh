#!/bin/bash

if [ "$1" == "" ]
then
	echo "|--------------------------------------------------|"
	echo "|-- Execute o script e informe o IP do Alvo. ------|"
	echo "|-- Ex.: $0 192.168.0.1 ---|"
	echo "|--------------------------------------------------|"

else
mkdir nmap-$1
cd nmap-$1
sudo nmap -PR -vv --script=whois-ip -sS --min-rate=1000 -p- $1 -oN initial
cat initial | grep open | cut -d "/" -f1 > openports.txt
sudo nmap -PR -vv -O -sC -sV -p $(sed -z 's/\n/,/g;s/,$/\n/' openports.txt) $1 -oA nmap
rm -rf openports.txt
fi

for host in $(ll | sed 's/ \{1,\}/ /g' | cut -d " " -f 10 | grep nmap);do httpx -p $(cat $host/nmap.nmap | grep tcp | cut -d "/" -f1 | tr ' ' -d | sed -z 's/\n/,/g;s/,$//g') -title -tech-detect -status-code -probe -ip -ss -o $host/httpx;done

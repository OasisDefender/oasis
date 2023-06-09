# Oasis Defender
<div id="badges" align="center">
  <a href="https://oasisdefender.com">
    <img src="https://img.shields.io/badge/oasisdefender.com-2A7B87?style=for-the-badge&logoColor=white" alt="oasisdefender.com"/>
  </a>
  <a href="https://twitter.com/OasisDefender">
    <img src="https://img.shields.io/badge/twitter-blue?style=for-the-badge&logo=twitter&logoColor=white" alt="Twitter:OasisDefender"/>
  </a>
  <a href="https://www.linkedin.com/company/oasisdefender/">
    <img src="https://img.shields.io/badge/linkedin-blue?style=for-the-badge&logo=linkedin&logoColor=white" alt="contact@oasisdefender.com"/>
  </a>
  <a href="mailto:contact@oasisdefender.com">
    <img src="https://img.shields.io/badge/@contact_us-2A7B87?style=for-the-badge&logoColor=white" alt="contact@oasisdefender.com"/>
  </a>
</div>


## Overview

Oasis Defender is an advanced solution for creating unified cross-cloud security environment.

# Installation

## For Docker users

``` bash
# Pull last docker image
# See last version at https://github.com/OasisDefender/oasis/pkgs/container/oasis-main
$ docker pull ghcr.io/oasisdefender/oasis-main:<tag>

# Load docker image
$ mkdir -p /home/$USER/.db && docker run -d --name oasis --restart always -p 127.0.0.1:5000:5000 -v /home/$USER/.db:/app/db --user $UID:$UID --hostname=$USER@oasis ghcr.io/oasisdefender/oasis-main:<tag>

# Note: Database placed to directory - /home/$USER/.db. Database conteins autentification params for cloud connection. We recommend that you protect this directory from unauthorized users. For example:
$ chmod 0700 /home/$USER/.db

# Oasis is ready to use. Launch your browser and follow the link: http://127.0.0.1:5000
```

## Manual installation
Download software archive from https://github.com/OasisDefender/oasis/releases/latest. For example:
``` bash
# Download ZIP file
$ wget https://github.com/OasisDefender/oasis/archive/refs/tags/v0.0.1.zip

# Extract archive
$ unzip oasis-0.0.1.zip

# Go to sources directory
$ cd oasis-0.0.1

# Install requirements
$ pip3.10 install -r requirements.txt

# Run oasis server
$ python3.10 app.py

# Oasis is ready to use. Launch your browser and follow the link: http://127.0.0.1:5000
```


# Usage

Once properly installed, you will be presented with startup screen at http://127.0.0.1:5000.

<p align="center">
<img alt="Oasis Defender Startup Screen" src="screenshots/cloud_start.png"/>
</p>


## Clouds Registration

You can register your clouds (currently supported are Amazon AWS and Microsoft Azure)

<p align="center">
<img alt="Oasis Defender cloud registration" src="screenshots/cloud_reg.gif"/>
</p>

## Automatic Inventory

The resource information of the registered clouds (external network resources, virtual networks, virtual machines, existing filtering rules) will be collected.

<p align="center">
<img alt="Oasis Defender inventorization" src="screenshots/cloud_inv.gif"/>
</p>


## Connections

You can create a visual connections between resources in your clouds, including cross-cloud connections.

<p align="center">
<img alt="Oasis Defender Overview" src="screenshots/cloud_conn.gif"/>
</p>

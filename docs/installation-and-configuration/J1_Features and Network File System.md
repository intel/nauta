# Features and Network File System
Intel DL Studio features include NFS and Redsocks*. 

## Features list

* [NFS](Z_examples/NFS) - default: enabled
* [redsocks](Z_examples/redsocks) - default: disabled 

## How to Enable Features

Additional features can be enabled using `features` object in configuration, as shown below.

Example:
```yaml
features:
   redsocks: False
```

## Feature Plugin Configuration

Configuration for features should be placed under `features_config`.

Example:
```yaml
features:
  redsocks: True
features_config:
  redsocks:
    IP: my-socks5-proxy
    Port: 1080
```

## Network File System Overview
The Network File System, or NFS allows a system to share directories and files with others over a network. The advantage of using NFS is that end-users as well as programs can access files on remote systems in the same way as local files. In addition, NFS uses less disk space, as it can be store data on a single machine while remaining accessible to others over a network.

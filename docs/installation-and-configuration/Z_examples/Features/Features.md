# Features
## Features list

* [NFS](Z_examples/NFS) - default: enabled
* [redsocks](Z_examples/redsocks) - default: disabled

## How to Enable Features

Additional features can be enabled using `features` object in configuration, as shown below.

Example:
```yaml
features:
  nfs: True
  redsocks: False
```

## Feature Plugin Configuration

Configuration for features should be placed under: `features_config`.

Example:
```yaml
features:
  redsocks: True
features_config:
  redsocks:
    IP: my-socks5-proxy
    Port: 1080
```


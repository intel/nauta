# Features
## Features list

* [NFS](nfs.md) - default: enabled
* [redsocks](redsocks.md) - default: disabled

## How to enable feature

Additional feature can be enabled using `features` object in configuration.

Example:
```yaml
features:
  nfs: True
  redsocks: False
```

## Feature plugins configuration

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

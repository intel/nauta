# version Command

Use the ` version` command to review the Nauta software version, as desired. 

## Synopsis

Returns the version of Nauta software. Also refer to the [nctl Verify Command ](../actions/verify.md) for Nauta installation verification information. 

`nctl version`

## Options

| Name | Required | Description | 
|:--- |:--- |:--- |
|`-f, --force`| No | Force command execution by ignoring (most) confirmation prompts |
|`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
|`-h, --help` | No | Displays help messaging information. |
 

## Returns

The version command returns the currently installed `nctl` application version of both client platform and server.  

## Example

```
| Component        | Version                  |
|------------------+--------------------------|
| nctl application | 1.0.0-ent-20190403020148 |
| nauta platform   | 1.0.0-ent-20190403020148 |

```

----------------------

## Return to Start of Document

* [README](../README.md)
----------------------

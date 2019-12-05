# verify Command

Use the `verify` command to check whether all prerequisites required by nctl are installed and have proper versions. 

## Synopsis

Checks whether all prerequisites required by `nctl` are installed and have proper versions. Also refer to the [Version Command ](../actions/version.md) for Nauta Version information. 

## Syntax

`nctl verify`

## Options

| Name | Required | Description | 
|:--- |:--- |:--- |
|`-f, --force`| No | Force command execution by ignoring (most) confirmation prompts. |
|`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
|`-h, --help` | No | Displays help messaging information. |


## Returns

In the case of any installation issues, the command returns information about their cause (which application should be installed and in which version). If no issues are found, a message indicates checks were successful. 

## Example

`nctl verify`

```
This OS is supported.
kubectl verified successfully.
helm client verified successfully.
git verified successfully.
helm server verified successfully.
kubectl server verified successfully.
packs resources' correctness verified successfully.
```

----------------------

## Return to Start of Document

* [README](../README.md)
----------------------

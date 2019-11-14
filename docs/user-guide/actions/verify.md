# verify Command

## Synopsis

Checks whether all prerequisites required by `nctl` are installed and have proper versions.  

## Syntax

`nctl verify`

## Options

| Name | Required | Description | 
|:--- |:--- |:--- |
|`-f, --force`| No | Ignore (most) confirmation prompts during command execution |
|`-v, --verbose`| No | Set verbosity level: <br>`-v` for INFO, <br>`-vv` for DEBUG |
|`-h, --help` | No | Displays help messaging information. |



## Returns

In the case of any installation issues, the command returns information about their cause (which application should be installed and in which version). If no issues are found, a message indicates checks were successful. 

## Example

`nctl verify`


```
This OS is supported.
draft verified successfully.
kubectl verified successfully.
kubectl server verified successfully.
helm client verified successfully.
helm server verified successfully.
```


----------------------

## Return to Start of Document

* [README](../README.md)

----------------------
 

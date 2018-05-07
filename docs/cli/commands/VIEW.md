# view - exposes web interfaces to a user

- [Synopsis](#synopsis)  
- [Arguments](#arguments)  
- [Returns](#returns)
- [Notes](#notes)  
- [Examples](#examples)  
- [Status](#status)

## Synopsis

Launches and exposes to a user a DLS4E web frontend. Format of the command is as follows:

_dlsctl launch <app_name>_

## Arguments

| Name | Obligatory | Description |
|:--- |:--- |:--- |
|_<app_name>_ | Yes | Name of an application that should be deployed to a customer. Available values are:<br> - _webUI_ - exposes web interface for tracking experiments |

## Returns

Link to an exposed application. Example link might look like that:
<!-- language: lang-none -->

    http://127.0.0.1/dls-gui/token=AB123CA27F  

## Notes

Notes concerning this command

## Examples

_dlsctl launch webUI_

## Status

Under development

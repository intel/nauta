# Build process

## Run
`make yum-build` 

## Requirements

For build process few resources is required:
* Access to docker
* Access to dev-3 instance in catalog /opt/repository

## Targets

### venv

Virtualenv build process

## Environment variales

Example: `MY_VARIABLE=SOME make <target>`

### VERSION_MAJOR

Major build version

Default: 0

### VERSION_MINOR

Minor build version

Default: 0

### VERSION_NO

Build number

Default: 0

### BUILD_ID

Build package ID - it is used as build in rpm and repository versions
Jenkins should use `<build id>.jenkins`

Default: 0

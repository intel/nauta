# Requirements
* Go 1.10.2 https://golang.org/doc/install
* Glide 0.13.1 https://github.com/Masterminds/glide
    * Linux/MacOs: `curl https://glide.sh/get | sh`
    * MacOs: `brew install glide`
    * Windows: use binary from https://github.com/Masterminds/glide/releases

# Prepare Go project environment
If `$GOPATH` is not set, Go will use following location as the default one: `$HOME/go`
This project should be placed under `$HOME/go/src/github.com/NervanaSystems/carbon`

If you are using different location you can fix it by calling following instructions:
```
export REPO=<YOUR_PATH_TO_REPO>/carbon/applications/experiment-service

cd $HOME
mkdir -p $HOME/go/src/github.com/NervanaSystems/carbon/applications/
ln -s $REPO $HOME/go/src/github.com/NervanaSystems/carbon/applications/experiment-service
```

# Build & Run
Build & run:
```
cd $HOME/go/src/github.com/NervanaSystems/carbon/applications/experiment-service

glide update --strip-vendor
go build
./experiment-service
```

Verify:
```
curl localhost:8080/Janusz
```
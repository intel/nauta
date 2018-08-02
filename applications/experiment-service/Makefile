fmt:
	go fmt ./...

build:
	./hack/update-codegen.sh
	CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -tags netgo -ldflags '-w' -o dist/apiserver ./cmd/apiserver
	CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -tags netgo -ldflags '-w' -o dist/controller-manager ./cmd/controller

docker:
	docker build .

test:
	go test -v ./...

test_coverage:
	go test -v ./...

dep_update:
	dep ensure -v

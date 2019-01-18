fmt:
	go fmt ./...

build: fmt dep_update
	./hack/update-codegen.sh
	CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -tags netgo -ldflags '-w' -o dist/apiserver ./cmd/apiserver
	CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -tags netgo -ldflags '-w' -o dist/controller-manager ./cmd/controller

docker:
	docker build .

test: dep_update
	go test -v ./...

test_coverage:
	./code_coverage.sh

dep_update:
	dep ensure -v

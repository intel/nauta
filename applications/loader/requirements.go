package main

import (
	_ "io"
	_ "os"
	_ "fmt"
	_ "errors"

	_ "github.com/docker/docker/api/types"
	_ "github.com/docker/docker/api/types/container"
	_ "github.com/docker/docker/client"
	_ "golang.org/x/net/context"
)

package main

import (
	"io"
	"bufio"
	"os"
	"fmt"
	"errors"

	"github.com/docker/docker/api/types"
	"github.com/docker/docker/client"
	"golang.org/x/net/context"
)

func main() {
    fmt.Printf("Starting loader\n")

    if len(os.Args) < 2 {
        panic("At least command name is required")
    }

    command := os.Args[1]

    if command == "check" {
        check()
    }

    if command == "load" {
        load()
    }
}

func check() {
    if len(os.Args) < 3 {
        panic("Image name is required")
    }
    image := os.Args[2]
    err := check_image_exists(image)
    if err != nil {
        panic(err)
    }
}

func load() {
    if len(os.Args) < 3 {
        panic("Image name is required")
    }

    image := os.Args[2]

    file, err := load_stdin_to_tmp()
    if err != nil {
        panic(err)
    }

    error := load_image(image, file)

    if error != nil {
        panic(error)
    }


}

func load_stdin_to_tmp() (string, error) {
    fmt.Println("Saving image")
    fh, err := os.Create("/tmp_image")
    if err != nil {
        return "", err
    }
    _, err = io.Copy(fh, os.Stdin)
    if err != nil {
        return "", err
    }

    if err := fh.Close(); err != nil {
        return "", err
    }
    fmt.Println("Image saved")

    return "/tmp_image", nil
}

func load_image(name string, file string) (error) {
    ctx := context.Background()
    cli, err := client.NewEnvClient()
    if err != nil {
        return err
    }

    fmt.Println("Loading input")
    fh, err := os.Open(file)
    if err != nil {
        return err
    }
    reader := bufio.NewReader(fh)

    fmt.Println("Loading image")
    response, error := cli.ImageLoad(ctx, reader, false)

    scanner := bufio.NewScanner(response.Body)
    scanner.Split(bufio.ScanWords)
    for scanner.Scan() {
        m := scanner.Text()
        fmt.Println(m)
    }

    fmt.Println("Image loaded")

    return error
}

func check_image_exists(name string) error {
    ctx := context.Background()
    cli, err := client.NewEnvClient()
    if err != nil {
        return err
    }

    images, err := cli.ImageList(ctx, types.ImageListOptions{})
	if err != nil {
		return err
	}

	for _, image := range images {
		for _, tag := range image.RepoTags {
		    if tag == name {
		        return nil
		    }
		}
	}

	return errors.New("Unable to find image")
}

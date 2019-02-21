package main

import (
	"io"
	"os"
)

func main() {
	//bs, err := ioutil.ReadFile(os.Args[len(os.Args)-1])
	//if err != nil {
	//	os.Stderr.Write([]byte("Error:" + err.Error()))
	//	os.Exit(1)
	//}
	//os.Stdout.Write(bs)

	f, err := os.Open(os.Args[len(os.Args)-1])
	if err != nil {
		panic(err)
	}
	_, err = io.Copy(os.Stdout, f)
	if err != nil {
		panic(err)
	}
}

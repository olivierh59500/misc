package main

import (
    "fmt"
    "os"
    "time"
)

type ExampleStruct struct {
    Epoch int64
    Name  string
}

func (p *ExampleStruct) Test() {
    fmt.Printf("This is %v's first Golang code! However, it's currently %d. Time for more programming!\n", p.Name, p.Epoch)
}

func main() {
    p := ExampleStruct {
        Name:  "misterpeguero",
        Epoch: (time.Now().Unix()),
    }

    p.Test()
    os.Exit(1234)
}

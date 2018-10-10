package main

import (
	"fmt"
	"remcall/schema"
)

func main() {
	enum := schema.Enum{"Hello", []schema.Name{"Opt1", "Opt2"}}
	fmt.Println(enum)
}

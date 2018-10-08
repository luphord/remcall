package schema

import (
	"bytes"
	"fmt"
)

type Enum struct {
	Name   Name
	Values []Name
}

func (enum Enum) TypeName() string {
	return string(enum.Name)
}

func (enum Enum) Resolve(lookup map[TypeRef]Type) error {
	return nil
}

func (enum Enum) String() string {
	buffer := bytes.Buffer{}
	for _, name := range enum.Values {
		buffer.WriteString("  ")
		buffer.WriteString(string(name))
		buffer.WriteString(",\n")
	}
	return fmt.Sprintf("enum %s {\n%s}", enum.Name, buffer.String())
}

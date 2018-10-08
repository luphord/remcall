package schema

import (
	"bytes"
	"fmt"
)

type NameTypePair struct {
	Name Name
	Type Type
}

func (ntp NameTypePair) String() string {
	return fmt.Sprintf("%s %s", ntp.Type.TypeName(), ntp.Name)
}

type Record struct {
	Name   Name
	Fields []NameTypePair
}

func (record Record) TypeName() string {
	return string(record.Name)
}

func (record Record) Resolve(lookup map[TypeRef]Type) error {
	for i, ntp := range record.Fields {
		switch tr := ntp.Type.(type) {
		case TypeRef:
			resolvedType, err := Resolve(lookup, tr)
			if err != nil {
				return err
			}
			record.Fields[i] = NameTypePair{ntp.Name, resolvedType}
		}
	}
	return nil
}

func (record Record) String() string {
	buffer := bytes.Buffer{}
	for _, nameTypePair := range record.Fields {
		buffer.WriteString("  ")
		buffer.WriteString(nameTypePair.String())
		buffer.WriteString(",\n")
	}
	return fmt.Sprintf("record %s {\n%s}", record.Name, buffer.String())
}

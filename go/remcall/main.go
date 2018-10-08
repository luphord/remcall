package main

import (
	"fmt"
	"remcall/schema"
)

func main() {
	enum := schema.Enum{"Hello", []schema.Name{"Opt1", "Opt2"}}
	fmt.Println(enum)
	var x schema.Type = schema.TypeRef(2)
	lookup := make(map[schema.TypeRef]schema.Type)
	lookup[schema.TypeRef(2)] = enum
	fmt.Println(x)
	fmt.Println(schema.TypeRef(-1))
	i := schema.Interface{}
	fmt.Println(i)
	rec := schema.Record{"MyRecord", []schema.NameTypePair{schema.NameTypePair{Name: "MyField", Type: enum}}}
	rec.Fields = append(rec.Fields, schema.NameTypePair{"Self", rec})
	rec.Fields = append(rec.Fields, schema.NameTypePair{"Multiple", schema.Array{enum}})
	rec.Fields = append(rec.Fields, schema.NameTypePair{"ToResolve", schema.TypeRef(2)})
	fmt.Println(rec)
	fmt.Println(rec.Fields[2])
	fmt.Println(rec.Resolve(lookup))
	fmt.Println(rec)
}

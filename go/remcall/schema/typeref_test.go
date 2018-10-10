package schema

import (
	"testing"
)

var myEnum = Enum{"Hello", []Name{"Opt1", "Opt2"}}

func TestTypeRefResolving(t *testing.T) {
	lookup := make(map[TypeRef]Type)
	lookup[TypeRef(2)] = &myEnum
	rec := Record{"MyRecord", []NameTypePair{NameTypePair{Name: "MyField", Type: &myEnum}}}
	rec.Fields = append(rec.Fields, NameTypePair{"Self", &rec}) // DO NOT DO THIS!
	rec.Fields = append(rec.Fields, NameTypePair{"Multiple", Array{&myEnum}})
	rec.Fields = append(rec.Fields, NameTypePair{"ToResolve", TypeRef(2)})
	rec.Resolve(lookup)
	AssertEqual(t, &myEnum, rec.Fields[3].Type)
}

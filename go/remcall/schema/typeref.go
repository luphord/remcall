package schema

import "fmt"

type TypeRef int32

func (tr TypeRef) TypeName() string {
	return fmt.Sprintf("<Type reference to %d>", tr)
}

func (tr TypeRef) Resolve(lookup map[TypeRef]Type) error {
	panic("cannot resolve typeref")
}

func (tr TypeRef) String() string {
	return tr.TypeName()
}

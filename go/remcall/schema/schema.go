package schema

import "fmt"

type Type interface {
	TypeName() string
	Resolve(lookup map[TypeRef]Type) error
}

type Name string

type TypeNotFound struct {
	ref TypeRef
}

func (err TypeNotFound) Error() string {
	return fmt.Sprintf("Could not resolve type reference %d", err.ref)
}

func Resolve(lookup map[TypeRef]Type, ref TypeRef) (Type, error) {
	isArray := false
	if ref < 0 {
		isArray = true
		ref = -ref
	}
	tp, exists := lookup[ref]
	if !exists {
		return nil, TypeNotFound{ref}
	}
	if isArray {
		return Array{tp}, nil
	} else {
		return tp, nil
	}
}

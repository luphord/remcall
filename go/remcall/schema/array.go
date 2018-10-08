package schema

import "fmt"

type Array struct {
	Underlying Type
}

func (array Array) TypeName() string {
	return fmt.Sprintf("%s[]", array.Underlying.TypeName())
}

func (array Array) Resolve(lookup map[TypeRef]Type) error {
	switch tr := array.Underlying.(type) {
	case TypeRef:
		resolvedType, err := Resolve(lookup, tr)
		if err != nil {
			return err
		}
		array.Underlying = resolvedType
	}
	return nil
}

func (array Array) String() string {
	return array.TypeName()
}

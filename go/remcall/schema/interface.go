package schema

type Method struct {
	Name       Name
	Arguments  []NameTypePair
	ReturnType Type
}

type Interface struct {
	Name Name
}

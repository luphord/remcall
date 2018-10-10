package schema

import (
	"fmt"
	"testing"
)

func AssertEqual(t *testing.T, expected interface{}, actual interface{}) {
	if expected != actual {
		t.Errorf("Expected '%s' got '%s'", expected, actual)
	}
}

var printed_enum = `enum Hello {
  Opt1,
  Opt2,
}`

func TestEnumPrinting(t *testing.T) {
	enum := Enum{"Hello", []Name{"Opt1", "Opt2"}}
	AssertEqual(t, printed_enum, fmt.Sprint(&enum))
}

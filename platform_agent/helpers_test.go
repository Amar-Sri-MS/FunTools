package main

import "testing"

func testMarshalSingle(t *testing.T, input interface{}, expected string) {
	data, err := textMarshal(input)
	if err != nil {
		t.Errorf("%v\n", err)
	}
	if string(data) != expected {
		t.Errorf("%s != %v\n", string(data), expected)
	}
}

func TestMarshallText(t *testing.T) {
	testMarshalSingle(t, "temperature/dpu", "=temperature/dpu\n")
	testMarshalSingle(t, initRequest{"123"}, "/url=123\n")
	m := make(map[string]interface{})
	m["a"] = "b"
	m["c"] = "d"
	testMarshalSingle(t, m, "/a=b\n/c=d\n")
}

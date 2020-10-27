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
	testMarshalSingle(t, messageResponse{true, ""}, "/success=true\n")
	testMarshalSingle(t, messageResponse{false, "abcd"}, "/success=false\n/message=abcd\n")
	testMarshalSingle(t, map[string]interface{}{"a": "b", "c": "d"}, "/a=b\n/c=d\n")
}

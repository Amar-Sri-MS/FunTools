package dpcclient

import (
	"io/ioutil"
	"strings"
	"testing"
)

func testCommand(verb string, params []interface{}, serverReply string) (interface{}, error) {
	reader := strings.NewReader(serverReply)
	dpc, err := NewDpcExecutor(reader, ioutil.Discard, ioutil.NopCloser(reader))
	if err != nil {
		return nil, err
	}
	defer dpc.Close()

	return dpc.Execute(verb, params)
}

// TestPositive testing for basic sanity
func TestPositive(t *testing.T) {
	result, err := testCommand("test", nil, "{\"result\": true, \"tid\":1}\n")
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	value, ok := result.(bool)
	if !ok {
		t.Errorf("unexpected result type: %v", value)
	}
	if !value {
		t.Errorf("unexpected result value: %v", value)
	}
}

func TestNegative(t *testing.T) {
	if res, err := testCommand("test", nil, "{\"result\": true}\n"); err == nil {
		t.Errorf("error is expected, got result: %v", res)
	}
	if res, err := testCommand("test", nil, "{\"result\": true, \"tid\": 33}\n"); err == nil {
		t.Errorf("error is expected, got result: %v", res)
	}
	if res, err := testCommand("test", nil, "{\"result\": true,\n"); err == nil {
		t.Errorf("error is expected, got result: %v", res)
	}
	if res, err := testCommand("test", nil, "{\"tid\":1}\n"); err == nil {
		t.Errorf("error is expected, got result: %v", res)
	}
	if res, err := testCommand("test", nil, "{\"tid\":1, \"result\":true, \"error\": \"Custom exception\"}\n"); err == nil {
		t.Errorf("error is expected, got result: %v", res)
	}
}

package main

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestTemperature(t *testing.T) {
	response, err := http.Get("http://localhost:9332/temperature/dpu/")
	if err != nil {
		t.Errorf("Unexpected error %v\n", err)
		return
	}
	checkResponseCode(t, http.StatusOK, response.StatusCode)

	buf := new(bytes.Buffer)
	buf.ReadFrom(response.Body)

	var data map[string]interface{}
	if err = json.Unmarshal(buf.Bytes(), &data); err != nil {
		t.Errorf("Invalid JSON returned %v\n", err)
		return
	}

	if _, ok := data["dpu"]; !ok {
		t.Errorf("Response has no \"dpu\" field: %v\n", data)
		return
	}

	if _, ok := data["dpu"].(map[string]interface{}); !ok {
		t.Errorf("Response \"dpu\" field is not a dictionary: %v\n", data)
		return
	}
}

func executeRequest(req *http.Request) *httptest.ResponseRecorder {
	rr := httptest.NewRecorder()
	return rr
}

func checkResponseCode(t *testing.T, expected, actual int) {
	if expected != actual {
		t.Errorf("Expected response code %d. Got %d\n", expected, actual)
	}
}

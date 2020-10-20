package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"testing"
)

func TestTemperature(t *testing.T) {
	data, err := checkHealthy("temperature/dpu/")
	if err != nil {
		t.Errorf("%v\n", err)
	}

	dataMap, ok := data.(map[string]interface{})

	if !ok {
		t.Errorf("Response type is incorrect: %v\n", data)
		return
	}

	if _, ok := dataMap["dpu"]; !ok {
		t.Errorf("Response has no \"dpu\" field: %v\n", dataMap)
		return
	}

	if _, ok := dataMap["dpu"].(map[string]interface{}); !ok {
		t.Errorf("Response \"dpu\" field is not a dictionary: %v\n", data)
		return
	}
}

func checkHealthy(endpoint string) (interface{}, error) {
	response, err := http.Get("http://localhost:9332/" + endpoint)
	if err != nil {
		return nil, fmt.Errorf("unexpected error %v", err)
	}
	if http.StatusOK != response.StatusCode {
		return nil, fmt.Errorf("expected response code %d, got %d", http.StatusOK, response.StatusCode)
	}

	buf := new(bytes.Buffer)
	buf.ReadFrom(response.Body)

	var data interface{}
	if err = json.Unmarshal(buf.Bytes(), &data); err != nil {
		return nil, fmt.Errorf("invalid JSON returned %v", err)
	}
	return data, nil
}

func TestAllHealthy(t *testing.T) {
	healthylist := []string{"temperature/dpu/", "images", "link_status",
		"port/mgmt", "port/0", "memory_info/0", "processor_info", "chip_info",
		"version", "boot_defaults", "ssd/0"}

	for _, path := range healthylist {
		_, err := checkHealthy(path)
		if err != nil {
			t.Errorf("While checking %s, error %v\n", path, err)
		}
	}
}

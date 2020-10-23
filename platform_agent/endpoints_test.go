package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"
	"testing"
	"time"
)

const (
	testURL             = "http://localhost:9332/"
	upgradeScenarioBase = "http://dochub.fungible.local/doc/platform_agent/"
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
	response, err := http.Get(testURL + endpoint)
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

func postJSON(endpoint string, jsonStr string) (*http.Response, error) {
	return http.Post(testURL+endpoint, "application/json", bytes.NewBuffer([]byte(jsonStr)))
}

func checkStatus(t *testing.T, number int, status string) {
	response, err := http.Get(testURL + "upgrade/" + strconv.Itoa(number) + "/status")
	if err != nil {
		t.Errorf("unexpected error %v", err)
		return
	}

	buf := new(bytes.Buffer)
	buf.ReadFrom(response.Body)

	var dataMap map[string]interface{}
	if err = json.Unmarshal(buf.Bytes(), &dataMap); err != nil {
		t.Errorf("invalid JSON returned %v", err)
		return
	}

	if _, ok := dataMap["status"]; !ok {
		t.Errorf("response has no \"process_id\" field: %v\n", dataMap)
		return
	}

	actualStatus, ok := dataMap["status"].(string)
	if !ok {
		t.Errorf("incorrect type for \"status\" field: %v\n", dataMap)
		return
	}

	if actualStatus != status {
		t.Errorf("actual status does not match %s != %s\n", actualStatus, status)
	}
}

func checkSuccess(t *testing.T, err error, response *http.Response) {
	if err != nil {
		t.Errorf("unexpected error %v", err)
		return
	}

	buf := new(bytes.Buffer)
	buf.ReadFrom(response.Body)

	var dataMap map[string]interface{}
	if err = json.Unmarshal(buf.Bytes(), &dataMap); err != nil {
		t.Errorf("invalid JSON returned %v", err)
		return
	}

	if _, ok := dataMap["success"]; !ok {
		t.Errorf("response has no \"success\" field: %v\n", dataMap)
		return
	}

	actualSuccess, ok := dataMap["success"].(bool)
	if !ok {
		t.Errorf("incorrect type for \"success\" field: %v\n", dataMap)
		return
	}

	if !actualSuccess {
		message, _ := dataMap["message"]
		t.Errorf("success is false, message: %v", message)
	}
}

func initUpgrade(scenario string) (int, error) {
	jsonStr := "{\"url\":\"" + upgradeScenarioBase + scenario + "\"}"
	response, err := postJSON("upgrade/init", jsonStr)
	if err != nil {
		return 0, fmt.Errorf("unexpected error %v", err)
	}

	buf := new(bytes.Buffer)
	buf.ReadFrom(response.Body)

	var dataMap map[string]interface{}
	if err = json.Unmarshal(buf.Bytes(), &dataMap); err != nil {
		return 0, fmt.Errorf("invalid JSON returned %v", err)
	}

	if _, ok := dataMap["process_id"]; !ok {
		return 0, fmt.Errorf("response has no \"process_id\" field: %v", dataMap)
	}

	floatPid, ok := dataMap["process_id"].(float64)
	if !ok {
		return 0, fmt.Errorf("incorrect type for \"process_id\" field: %v", dataMap)
	}

	return int(floatPid), nil
}

func TestUpgradeSuccess(t *testing.T) {
	intPid, err := initUpgrade("test_positive.sh")
	if err != nil {
		t.Error(err)
		return
	}

	checkStatus(t, intPid, "initialized")

	response, err := postJSON("upgrade/"+strconv.Itoa(intPid)+"/start", "")
	checkSuccess(t, err, response)

	checkStatus(t, intPid, "started")
	time.Sleep(2 * time.Second)

	checkStatus(t, intPid, "done")

	_, err = http.Get(testURL + "upgrade/" + strconv.Itoa(intPid) + "/file/output")
	if err != nil {
		t.Errorf("unexpected error %v", err)
		return
	}

	response, err = postJSON("upgrade/"+strconv.Itoa(intPid)+"/complete", "")
	checkSuccess(t, err, response)
}

func TestUpgradeFailure(t *testing.T) {
	intPid, err := initUpgrade("test_negative.sh")
	if err != nil {
		t.Error(err)
		return
	}

	checkStatus(t, intPid, "initialized")

	response, err := postJSON("upgrade/"+strconv.Itoa(intPid)+"/start", "")
	checkSuccess(t, err, response)
	time.Sleep(time.Second)

	checkStatus(t, intPid, "failed")

	_, err = http.Get(testURL + "upgrade/" + strconv.Itoa(intPid) + "/file/error")
	if err != nil {
		t.Errorf("unexpected error %v", err)
		return
	}

	response, err = postJSON("upgrade/"+strconv.Itoa(intPid)+"/complete", "")
	checkSuccess(t, err, response)
}

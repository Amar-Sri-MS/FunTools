// File: helpers.go
package main

import (
	"encoding/json"
	"log"
	"net/http"

	"github.com/fungible-inc/FunTools/dpcclient"
)

type errorStatusResponse struct {
	ErrorMessage string `json:"error"`
}

func internalServerError(w http.ResponseWriter) {
	http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
	log.Println(http.StatusText(http.StatusInternalServerError))
}

func errorResponse(w http.ResponseWriter, message string) {
	d := errorStatusResponse{message}
	respBody, err := json.MarshalIndent(d, "", "  ")
	if err != nil {
		log.Println("marshal:", err)
		log.Println(d)
		return
	}

	if *verbose {
		log.Println(string(respBody))
	}

	_, err = w.Write(respBody)
	if err != nil {
		log.Println("write:", err)
	}
}

func dataResponse(w http.ResponseWriter, d interface{}) {
	respBody, err := json.MarshalIndent(d, "", "  ")
	if err != nil {
		log.Println("marshal:", err)
		log.Println(d)
		return
	}

	if *verbose {
		log.Println(string(respBody))
	}

	_, err = w.Write(respBody)
	if err != nil {
		log.Println("write:", err)
	}
}

func peekDPC(client *dpcclient.DpcClient, path string) (interface{}, error) {
	p := make([]interface{}, 1)
	p[0] = path
	return client.Execute("peek", p)
}

func temperatureDPC(client *dpcclient.DpcClient, kind string, numbers []int) (interface{}, error) {
	p := make([]interface{}, 1+len(numbers))
	p[0] = kind
	for i := 0; i < len(numbers); i++ {
		p[i+1] = numbers[i]
	}
	return client.Execute("temperature", p)
}

func addValue(data *map[string]interface{}, category string, sub string, value interface{}) {
	if _, ok := (*data)[category]; !ok {
		(*data)[category] = make(map[string]interface{})
	}
	subMap, ok := (*data)[category].(map[string]interface{})
	if !ok {
		log.Println("Invalid datatype for category", category, (*data)[category])
		return
	}
	subMap[sub] = value
}

func allDeviceIds(kind string) []int {
	switch kind {
	case "ssd":
		return []int{1, 2, 3, 4, 5, 6, 7, 8}
	case "dpu":
		return []int{0}
	case "optics":
		return []int{1, 2}
	default:
		return nil
	}
}

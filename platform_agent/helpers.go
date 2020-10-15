// File: helpers.go
package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strconv"
	"strings"

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

func serveResponse(w http.ResponseWriter) func(interface{}, error) {
	return func(d interface{}, err error) {
		if err != nil {
			internalServerError(w)
			return
		}
		dataResponse(w, d)
	}
}

func serveSingleFunction(state *agentState, w http.ResponseWriter, r *http.Request, f func() (interface{}, error)) {
	if r.Method != "GET" {
		log.Println("Unknown method")
		http.Error(w, "Bad Request", http.StatusBadRequest)
		return
	}

	serveResponse(w)(f())
}

func mapFunc(vs []int64, f func(int64) string) []string {
	vsm := make([]string, len(vs))
	for i, v := range vs {
		vsm[i] = f(v)
	}
	return vsm
}

func normalizeMac(data interface{}) (string, error) {
	floatData, ok := data.(float64)
	if !ok {
		return "", fmt.Errorf("Incorrect datatype")
	}
	intData := int64(floatData)
	parts := make([]int64, 6)
	for i := 0; i < len(parts); i++ {
		parts[i] = intData % 256
		intData = intData / 256
	}
	return strings.Join(mapFunc(parts, func(a int64) string { return fmt.Sprintf("%X", a) }), ":"), nil
}

func servePeek(path string) httpHandlerWithState {
	return func(state *agentState, w http.ResponseWriter, r *http.Request) {
		serveSingleFunction(state, w, r, func() (interface{}, error) { return peekDPC(state.dpc, path) })
	}
}

func validateGetWithNumber(r *http.Request) (int, error) {
	if r.Method != "GET" {
		return 0, fmt.Errorf("Unknown method")
	}

	parts := strings.Split(r.URL.Path, "/")

	if len(parts) != 3 {
		return 0, fmt.Errorf("Unknown path")
	}

	number, err := strconv.Atoi(parts[2])
	if err != nil {
		return 0, fmt.Errorf("Unknown path")
	}
	return number, nil
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

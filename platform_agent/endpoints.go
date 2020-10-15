package main

import (
	"fmt"
	"log"
	"net/http"
	"strconv"
	"strings"
)

func serveTemperature(state *agentState, w http.ResponseWriter, r *http.Request) {
	if r.Method != "GET" {
		log.Println("Unknown method")
		http.Error(w, "Bad Request", http.StatusBadRequest)
		return
	}

	parts := strings.Split(r.URL.Path, "/")

	if len(parts) < 3 || len(parts) > 4 {
		log.Println("Unknown path")
		http.Error(w, "Bad Request", http.StatusBadRequest)
	}

	if parts[2] == "ssd" || parts[2] == "optics" || parts[2] == "dpu" || parts[2] == "dimm" {
		response := make(map[string]interface{})
		allIds := allDeviceIds(parts[2])
		var deviceIds []int

		if len(parts) == 4 && parts[3] != "" {
			number, err := strconv.Atoi(parts[3])
			if err != nil || !contains(allIds, number) {
				log.Println("Invalid ID", parts[3])
				http.Error(w, "Bad Request", http.StatusBadRequest)
				return
			}
			deviceIds = []int{number}
		} else {
			deviceIds = allIds
		}
		for _, id := range deviceIds {
			params := []int{id}
			if parts[2] == "dimm" {
				params = []int{id / 2, id % 2}
			}
			data, err := temperatureDPC(state.dpc, parts[2], params)
			if err != nil {
				internalServerError(w)
				return
			}
			addValue(&response, parts[2], strconv.Itoa(id), data)
		}
		dataResponse(w, response)
		return
	}
	log.Println("Unknown path")
	http.Error(w, "Bad Request", http.StatusBadRequest)
}

func serveLinkStatus(state *agentState, w http.ResponseWriter, r *http.Request) {
	serveSingleFunction(state, w, r, func() (interface{}, error) { return state.dpc.Execute("port", []interface{}{"linkstatus"}) })
}

func serveMgmtPortInfo(state *agentState, w http.ResponseWriter, r *http.Request) {
	data, err := state.dpc.Execute("port", []interface{}{"mgmt", "macaddrget"})
	if err != nil {
		internalServerError(w)
		return
	}

	macaddrStr, err := normalizeMac(data)
	if err != nil {
		log.Println(err)
		internalServerError(w)
		return
	}

	response := make(map[string]interface{})
	response["macaddr"] = macaddrStr
	dataResponse(w, response)
}

func servePort(state *agentState, w http.ResponseWriter, r *http.Request) {
	if r.Method != "GET" {
		log.Println("Unknown method")
		http.Error(w, "Bad Request", http.StatusBadRequest)
		return
	}

	parts := strings.Split(r.URL.Path, "/")

	if len(parts) != 3 {
		log.Println("Unknown path")
		http.Error(w, "Bad Request", http.StatusBadRequest)
	}

	if parts[2] == "mgmt" {
		serveMgmtPortInfo(state, w, r)
		return
	}

	number, err := strconv.Atoi(parts[2])
	if err != nil {
		log.Println("Unknown path")
		http.Error(w, "Bad Request", http.StatusBadRequest)
		return
	}

	params := make(map[string]int)
	params["shape"] = 0
	params["portnum"] = number

	macaddr, err := state.dpc.Execute("port", []interface{}{"macaddrget", params})
	if err != nil {
		internalServerError(w)
		return
	}

	mtu, err := state.dpc.Execute("port", []interface{}{"mtuget", params})
	if err != nil {
		internalServerError(w)
		return
	}

	macaddrStr, err := normalizeMac(macaddr)
	if err != nil {
		log.Println(err)
		internalServerError(w)
		return
	}

	response := make(map[string]interface{})
	response["macaddr"] = macaddrStr
	response["mtu"] = mtu
	dataResponse(w, response)
}

func serveMemoryInfo(state *agentState, w http.ResponseWriter, r *http.Request) {
	number, err := validateGetWithNumber(r)
	if err != nil {
		log.Println(err)
		http.Error(w, "Bad Request", http.StatusBadRequest)
		return
	}

	serveResponse(w)(peekDPC(state.dpc, fmt.Sprintf("config/memory_info/Memory/%d", number)))
}

func serveSSD(state *agentState, w http.ResponseWriter, r *http.Request) {
	number, err := validateGetWithNumber(r)
	if err != nil {
		log.Println(err)
		http.Error(w, "Bad Request", http.StatusBadRequest)
		return
	}

	data1, err := peekDPC(state.dpc, fmt.Sprintf("storage/devices/nvme/ssds/%d", number))
	if err != nil {
		internalServerError(w)
		return
	}

	data2, err := peekDPC(state.dpc, fmt.Sprintf("nvme/ssds/info/%d", number))
	if err != nil {
		internalServerError(w)
		return
	}

	dataResponse(w, []interface{}{data1, data2})
}

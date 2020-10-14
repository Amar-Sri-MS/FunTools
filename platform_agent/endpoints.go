package main

import (
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

	if parts[2] == "ssd" || parts[2] == "optics" || parts[2] == "dpu" {
		response := make(map[string]interface{})
		var deviceIds []int

		if len(parts) == 4 && parts[3] != "" {
			number, err := strconv.Atoi(parts[3])
			if err != nil {
				log.Println("Number is not an integer", parts[3])
				http.Error(w, "Bad Request", http.StatusBadRequest)
				return
			}
			deviceIds = []int{number}
		} else {
			deviceIds = allDeviceIds(parts[2])
		}
		for _, id := range deviceIds {
			data, err := temperatureDPC(state.dpc, parts[2], []int{id})
			if err != nil {
				internalServerError(w)
				return
			}
			addValue(&response, parts[2], strconv.Itoa(id), data)
		}
		dataResponse(w, response)
		return
	}

}

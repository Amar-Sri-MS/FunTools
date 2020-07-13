// Copyright 2020 Fungible Inc

package main

import (
	"encoding/json"
	"flag"
	"log"
	"net/http"
)

var (
	serviceAddr               = flag.String("service_addr", "localhost:8080", "http service address")
	dpcProto                  = flag.String("dpc_protocol", "tcp", "DPC proxy protocol")
	dpcAddr                   = flag.String("dpc_addr", "localhost:40221", "DPC proxy address")
	client         *DpcClient = nil
	requestsServed            = 0
)

type storageCommandParams struct {
	BlockSize int    `json:"block_size"`
	Capacity  int    `json:"capacity"`
	GroupID   int    `json:"group_id"`
	Name      string `json:"name"`
	Type      string `json:"type"`
	UUID      string `json:"uuid"`
}

type storageCommand struct {
	Class  string               `json:"class"`
	OpCode string               `json:"opcode"`
	Params storageCommandParams `json:"params"`
}

func serveHome(w http.ResponseWriter, r *http.Request) {
	if r.Method != "GET" {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}
	// useful code here
	params := storageCommand{"volume", "VOL_ADMIN_OPCODE_CREATE", storageCommandParams{4096, 8589934592, 1, "test1", "VOL_TYPE_BLK_LOCAL_THIN", "a8c6820a8b0b3ef1"}}
	response, err := client.Execute("echo", []interface{}{params})

	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}
	jsonStr, err := json.Marshal(response)
	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}
	w.Write(jsonStr)
	requestsServed++
	if requestsServed%1000 == 0 {
		log.Println(r.URL)
		log.Printf("Served %d requests", requestsServed)
	}
}

func main() {
	flag.Parse()
	log.SetFlags(0)
	var err error
	client, err = NewClient(*dpcProto, *dpcAddr)
	if err != nil {
		log.Fatal(err)
		return
	}
	http.HandleFunc("/", serveHome)
	log.Fatal(http.ListenAndServe(*serviceAddr, nil))
}

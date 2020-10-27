// Copyright 2020 Fungible Inc

package main

import (
	"flag"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"strconv"
	"sync"

	"github.com/fungible-inc/FunTools/dpcclient"
)

const (
	upgradeFolder          = "/tmp/upgrades/"
	upgradeInitialized     = iota
	upgradeStarted         = iota
	upgradeFinishedSuccess = iota
	upgradeFinishedFailure = iota
)

var (
	serviceAddr = flag.String("service_addr", ":9332", "http service address")
	dpcProto    = flag.String("dpc_protocol", "tcp", "DPC proxy protocol")
	dpcAddr     = flag.String("dpc_addr", "localhost:40221", "DPC proxy address")
	certFile    = flag.String("cert_file", "cert.pem", "TLS certificate")
	keyFile     = flag.String("key_file", "key.pem", "TLS key")
	tlsEnable   = flag.Bool("tls_enable", false, "Enable TLS")
	verbose     = flag.Bool("verbose", false, "Output debug information to log")
)

type agentState struct {
	dpc            *dpcclient.DpcClient
	upgrade        sync.Mutex
	upgradeStatus  map[int]int
	requestsServed int
}

type httpHandler func(http.ResponseWriter, *http.Request)
type httpHandlerWithState func(*agentState, http.ResponseWriter, *http.Request)

func (state *agentState) With(handler httpHandlerWithState) httpHandler {
	return func(w http.ResponseWriter, r *http.Request) {
		if *verbose {
			log.Println(r.Method, r.URL.Path)
		}
		handler(state, w, r)
	}
}

func newAgentState() *agentState {
	s := new(agentState)
	s.upgradeStatus = make(map[int]int)

	_ = os.Mkdir(upgradeFolder, 0744)
	files, err := ioutil.ReadDir(upgradeFolder)
	if err != nil {
		log.Fatal(err)
	}

	for _, f := range files {
		number, err := strconv.Atoi(f.Name())
		if err != nil {
			continue
		}
		if _, err := os.Stat(outputName(number)); err == nil {
			s.upgradeStatus[number] = upgradeFinishedSuccess
			continue
		}
		if _, err := os.Stat(errorName(number)); err == nil {
			s.upgradeStatus[number] = upgradeFinishedFailure
			continue
		}
		s.upgradeStatus[number] = upgradeInitialized
	}

	return s
}

func serveDefault(w http.ResponseWriter, r *http.Request) {
	log.Println("Unknown method is called", r.URL.Path, r.Method)
	http.Error(w, "Forbidden", http.StatusNotFound)
}

func main() {
	flag.Parse()
	log.SetFlags(log.Ltime | log.Lmicroseconds | log.Lshortfile)
	var err error
	state := newAgentState()
	state.dpc, err = dpcclient.NewNetDpcExecutor(*dpcProto, *dpcAddr)
	if err != nil {
		log.Fatal(err)
		return
	}
	state.dpc.SetVerbose(*verbose)

	http.HandleFunc("/", serveDefault)

	http.HandleFunc("/temperature/", state.With(serveTemperature))
	http.HandleFunc("/images", state.With(servePeek("config/chip_info/images", nil)))
	http.HandleFunc("/link_status", state.With(serveLinkStatus))
	http.HandleFunc("/port/", state.With(servePort))
	http.HandleFunc("/memory_info/", state.With(serveMemoryInfo))
	http.HandleFunc("/processor_info", state.With(servePeek("config/processor_info", nil)))
	http.HandleFunc("/chip_info", state.With(servePeek("config/chip_info", nil)))
	http.HandleFunc("/version", state.With(servePeek("config/version", nil)))
	http.HandleFunc("/boot_defaults", state.With(servePeek("config/boot_defaults", map[string]interface{}{"config-args": nil, "feature_set": nil})))
	http.HandleFunc("/ssd/", state.With(serveSSD))
	http.HandleFunc("/upgrade/", state.With(serveUpgrade))

	if *tlsEnable {
		log.Fatal(http.ListenAndServeTLS(*serviceAddr, *certFile, *keyFile, nil))
	} else {
		log.Fatal(http.ListenAndServe(*serviceAddr, nil))
	}
}

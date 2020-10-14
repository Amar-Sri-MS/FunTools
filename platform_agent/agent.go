// Copyright 2020 Fungible Inc

package main

import (
	"flag"
	"log"
	"net/http"

	"github.com/fungible-inc/FunTools/dpcclient"
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

func serveDefault(w http.ResponseWriter, r *http.Request) {
	log.Println("Unknown method is called", r.URL.Path, r.Method)
	http.Error(w, "Forbidden", http.StatusNotFound)
}

func main() {
	flag.Parse()
	log.SetFlags(log.Ltime | log.Lmicroseconds | log.Lshortfile)
	var err error
	state := new(agentState)
	state.dpc, err = dpcclient.NewNetDpcExecutor(*dpcProto, *dpcAddr)
	if err != nil {
		log.Fatal(err)
		return
	}
	state.dpc.SetVerbose(*verbose)

	http.HandleFunc("/", serveDefault)

	http.HandleFunc("/temperature/", state.With(serveTemperature))

	if *tlsEnable {
		log.Fatal(http.ListenAndServeTLS(*serviceAddr, *certFile, *keyFile, nil))
	} else {
		log.Fatal(http.ListenAndServe(*serviceAddr, nil))
	}
}

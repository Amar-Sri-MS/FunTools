// Copyright 2020 Fungible Inc

package main

import (
	"bufio"
	"encoding/json"
	"log"
	"net"
)

// DpcClient is the Main Structure Holding all client state
type DpcClient struct {
	transactionID int
	connection    net.Conn
}

type dpcCommand struct {
	Tid       int           `json:"tid"`
	Verb      string        `json:"verb"`
	Arguments []interface{} `json:"arguments"`
}

// NewClient is the factory function to make a DPC client
// network examples are "tcp", "unix"
func NewClient(network string, address string) (*DpcClient, error) {
	c, err := net.Dial(network, address)
	if err != nil {
		return nil, err
	}
	return &DpcClient{0, c}, nil
}

// Execute function runs verb with given params
func (c *DpcClient) Execute(verb string, params []interface{}) (interface{}, error) {
	c.transactionID++
	jsonStr, err := json.Marshal(dpcCommand{c.transactionID, verb, params})
	if err != nil {
		log.Fatal(err)
	}
	if _, err := c.connection.Write([]byte(jsonStr)); err != nil {
		log.Fatal(err)
	}
	if _, err := c.connection.Write([]byte("\n")); err != nil {
		log.Fatal(err)
	}
	responseBytes, err := bufio.NewReader(c.connection).ReadString('\n')
	if err != nil {
		log.Fatal(err)
	}
	var data map[string]interface{}
	if err := json.Unmarshal([]byte(responseBytes), &data); err != nil {
		log.Fatal(err)
	}
	if int(data["tid"].(float64)) != c.transactionID {
		log.Fatal("Transaction id mismatch")
	}
	if _, ok := data["result"]; !ok {
		log.Fatal("Response has no result field")
	}
	return data["result"], nil
}

// Copyright 2020 Fungible Inc

package dpcclient

import (
	"bufio"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net"
	"strings"
	"sync"
)

// DpcExecutor synchronously runs DPC verbs
type DpcExecutor interface {
	SetVerbose(bool)
	Execute(string, []interface{}) (interface{}, error)
}

// DpcClient is the Main Structure Holding all client state
type DpcClient struct {
	transactionID int
	verbose       bool
	mutex         sync.Mutex
	reader        io.Reader
	writer        io.Writer
	closer        io.Closer
}

type dpcCommand struct {
	Tid       int           `json:"tid"`
	Verb      string        `json:"verb"`
	Arguments []interface{} `json:"arguments"`
}

// NewNetDpcExecutor is the factory function to make a DPC synchronous executor
// network examples are "tcp", "unix"
func NewNetDpcExecutor(network string, address string) (*DpcClient, error) {
	c, err := net.Dial(network, address)
	if err != nil {
		return nil, err
	}
	return NewDpcExecutor(c, c, c)
}

// NewDpcExecutor is the factory function to make a DPC synchronous executor
// which works with abstract reader, writer and closer
func NewDpcExecutor(reader io.Reader, writer io.Writer, closer io.Closer) (*DpcClient, error) {
	return &DpcClient{0, false, sync.Mutex{}, reader, writer, closer}, nil
}

// SetVerbose function enables logging for DPC commands and responses
func (c *DpcClient) SetVerbose(v bool) {
	c.verbose = v
}

// Execute function runs verb with given params
func (c *DpcClient) Execute(verb string, params []interface{}) (interface{}, error) {
	c.mutex.Lock()
	defer c.mutex.Unlock()
	c.transactionID++
	jsonBytes, err := json.Marshal(dpcCommand{c.transactionID, verb, params})
	if err != nil {
		log.Println("DPC marshal error", err)
		return nil, err
	}
	if c.verbose {
		log.Println("Sending DPC:", string(jsonBytes))
	}
	if _, err := c.writer.Write(jsonBytes); err != nil {
		log.Println("DPC write error", err)
		return nil, err
	}
	if _, err := c.writer.Write([]byte("\n")); err != nil {
		log.Println("DPC write error", err)
		return nil, err
	}
	responseStr, err := bufio.NewReader(c.reader).ReadString('\n')
	if err != nil {
		log.Println("DPC read response error", err)
		return nil, err
	}
	if c.verbose {
		log.Println("DPC response:", strings.TrimSuffix(responseStr, "\n"))
	}
	var data map[string]interface{}
	if err := json.Unmarshal([]byte(responseStr), &data); err != nil {
		log.Println("DPC unmarshal error", err)
		return nil, err
	}
	if _, ok := data["tid"].(float64); !ok {
		err = fmt.Errorf("Transaction id is missing")
		log.Println(err)
		return nil, err
	}
	if int(data["tid"].(float64)) != c.transactionID {
		err = fmt.Errorf("Transaction id mismatch")
		log.Println(err)
		return nil, err
	}
	if _, ok := data["error"]; ok {
		err = fmt.Errorf("DPC exception: %s", data["error"].(string))
		log.Println(err)
		return nil, err
	}
	if _, ok := data["result"]; !ok {
		err = fmt.Errorf("Response has no result field")
		log.Println(err)
		return nil, err
	}
	return data["result"], nil
}

// Close DPC connection
func (c *DpcClient) Close() {
	c.closer.Close()
}

package main

import (
	"bytes"
	"fmt"
	"io/ioutil"
	"log"
	"math/rand"
	"os"
	"os/exec"
	"strconv"
)

func bundleName(processID int) string {
	return tempFolderPath(processID) + "/bundle"
}

func errorName(processID int) string {
	return tempFolderPath(processID) + "/error"
}

func outputName(processID int) string {
	return tempFolderPath(processID) + "/output"
}

func setUpgradeState(state *agentState, number int, newState int) {
	state.upgrade.Lock()
	defer state.upgrade.Unlock()
	state.upgradeStatus[number] = newState
}

func emitOutput(state *agentState, number int, fileName string, message string, newState int) {
	setUpgradeState(state, number, newState)
	err := ioutil.WriteFile(fileName, []byte(message), 0644)
	if err != nil {
		log.Println("Failed to write output", err)
	}
}

func upgrade(state *agentState, number int) {
	cmd := exec.Command(bundleName(number))
	var out bytes.Buffer
	cmd.Stdout = &out
	err := cmd.Run()
	if err != nil {
		log.Println("error running upgrade", err)
		emitOutput(state, number, errorName(number), fmt.Sprint(err), upgradeFinishedFailure)
		return
	}
	emitOutput(state, number, outputName(number), out.String(), upgradeFinishedSuccess)
}

func tempFolderPath(number int) string {
	return upgradeFolder + strconv.Itoa(number)
}

func allocateID(state *agentState) int {
	state.upgrade.Lock()
	defer state.upgrade.Unlock()
	for {
		number := rand.Intn(9999999)
		path := tempFolderPath(number)
		if _, err := os.Stat(path); err != nil {
			if os.IsNotExist(err) {
				os.Mkdir(path, 0755)
				state.upgradeStatus[number] = upgradeInitialized
				return number
			}
		}
	}
}

func upgradeStatusToString(status int) string {
	switch status {
	case upgradeInitialized:
		return "initialized"
	case upgradeStarted:
		return "started"
	case upgradeFinishedFailure:
		return "failed"
	case upgradeFinishedSuccess:
		return "done"
	default:
		return "unknown"
	}
}

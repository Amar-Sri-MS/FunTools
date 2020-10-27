package main

import (
	"io"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"
)

type initRequest struct {
	URL string `json:"url"`
}

type initResponse struct {
	ProcessID int `json:"process_id"`
}

type messageResponse struct {
	Success bool   `json:"success"`
	Message string `json:"message,omitempty"`
}

type statusResponse struct {
	Status string `json:"status"`
}

func serveInitUpgrade(state *agentState, w http.ResponseWriter, r *http.Request) {
	var params initRequest
	err := decodeJSONBody(w, r, &params)
	if err != nil {
		malformedRequestResponse(w, err)
		return
	}
	processID := allocateID(state)

	response, e := http.Get(params.URL)
	if err != nil {
		log.Println("error downloading bundle", err)
		internalServerError(w)
		return
	}
	defer response.Body.Close()

	file, err := os.OpenFile(bundleName(processID), os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0744)
	if err != nil {
		log.Println("error creating a file", e)
		internalServerError(w)
		return
	}
	defer file.Close()

	_, err = io.Copy(file, response.Body)
	if err != nil {
		log.Println("error piping out file contents", e)
		internalServerError(w)
		return
	}

	dataResponse(w, initResponse{processID}, isTextRequested(r))
}

func serveUpgradeStart(state *agentState, w http.ResponseWriter, r *http.Request, number int) {
	state.upgrade.Lock()
	defer state.upgrade.Unlock()
	if state.upgradeStatus[number] == upgradeInitialized {
		go upgrade(state, number)
		state.upgradeStatus[number] = upgradeStarted
		dataResponse(w, messageResponse{true, ""}, isTextRequested(r))
		return
	}
	dataResponse(w, messageResponse{false, "Already started"}, isTextRequested(r))
}

func serveUpgradeStatus(state *agentState, w http.ResponseWriter, r *http.Request, number int) {
	dataResponse(w, statusResponse{upgradeStatusToString(state.upgradeStatus[number])}, isTextRequested(r))
}

func serveUpgradeApply(state *agentState, w http.ResponseWriter, r *http.Request, number int) {
	if state.upgradeStatus[number] != upgradeFinishedSuccess {
		dataResponse(w, messageResponse{false, "cannot apply an upgrade which was not finished with success"}, isTextRequested(r))
		return
	}

	// add reboot and other apply-related commands
	dataResponse(w, messageResponse{false, "not implemented"}, isTextRequested(r))
}

func serveUpgradeComplete(state *agentState, w http.ResponseWriter, r *http.Request, number int) {
	state.upgrade.Lock()
	defer state.upgrade.Unlock()
	if state.upgradeStatus[number] == upgradeFinishedSuccess || state.upgradeStatus[number] == upgradeFinishedFailure {
		delete(state.upgradeStatus, number)

		err := os.RemoveAll(tempFolderPath(number))
		if err != nil {
			log.Println("Cannot remove upgrade folder", err)
		}

		dataResponse(w, messageResponse{true, ""}, isTextRequested(r))
		return
	}
	dataResponse(w, messageResponse{false, "Cannot complete, not finished"}, isTextRequested(r))
}

func serveUpgrade(state *agentState, w http.ResponseWriter, r *http.Request) {
	parts := strings.Split(r.URL.Path, "/")
	if parts[len(parts)-1] == "" {
		parts = parts[:len(parts)-1]
	}

	if len(parts) == 3 && parts[2] == "init" && r.Method == "POST" {
		serveInitUpgrade(state, w, r)
		return
	}

	if len(parts) < 4 {
		log.Println("Unknown path")
		http.Error(w, "Bad Request", http.StatusBadRequest)
		return
	}

	number, err := strconv.Atoi(parts[2])

	if err != nil {
		log.Println("Can't convert process id to int", err)
		http.Error(w, "Bad Request", http.StatusBadRequest)
		return
	}

	if _, err := os.Stat(tempFolderPath(number)); err != nil {
		log.Println("Path does not exist", err)
		http.Error(w, "Bad Request", http.StatusBadRequest)
		return
	}

	if len(parts) == 4 && parts[3] == "start" && r.Method == "POST" {
		serveUpgradeStart(state, w, r, number)
		return
	}

	if len(parts) == 4 && parts[3] == "status" && r.Method == "GET" {
		serveUpgradeStatus(state, w, r, number)
		return
	}

	if len(parts) == 4 && parts[3] == "apply" && r.Method == "POST" {
		serveUpgradeApply(state, w, r, number)
		return
	}

	if len(parts) == 5 && parts[3] == "file" && r.Method == "GET" {
		// we remove all slashes from the name to make sure it doesn't escape its folder
		cleanName := strings.ReplaceAll(parts[4], "/", "")
		serveFile(w, tempFolderPath(number), cleanName)
		return
	}

	if len(parts) == 4 && parts[3] == "complete" && r.Method == "POST" {
		serveUpgradeComplete(state, w, r, number)
		return
	}

	log.Println("Unknown path")
	http.Error(w, "Bad Request", http.StatusBadRequest)
}

// File: helpers.go
package main

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"math"
	"net/http"
	"os"
	"reflect"
	"strconv"
	"strings"

	"github.com/fungible-inc/FunTools/dpcclient"
)

type errorStatusResponse struct {
	ErrorMessage string `json:"error"`
}

type malformedRequest struct {
	status int
	msg    string
}

func (mr *malformedRequest) Error() string {
	return mr.msg
}

func decodeJSONBody(w http.ResponseWriter, r *http.Request, dst interface{}) error {
	r.Body = http.MaxBytesReader(w, r.Body, 1048576)

	dec := json.NewDecoder(r.Body)
	dec.DisallowUnknownFields()

	err := dec.Decode(&dst)
	if err != nil {
		var syntaxError *json.SyntaxError
		var unmarshalTypeError *json.UnmarshalTypeError

		switch {
		case errors.As(err, &syntaxError):
			msg := fmt.Sprintf("Request body contains badly-formed JSON (at position %d)", syntaxError.Offset)
			return &malformedRequest{status: http.StatusBadRequest, msg: msg}

		case errors.Is(err, io.ErrUnexpectedEOF):
			msg := fmt.Sprintf("Request body contains badly-formed JSON")
			return &malformedRequest{status: http.StatusBadRequest, msg: msg}

		case errors.As(err, &unmarshalTypeError):
			msg := fmt.Sprintf("Request body contains an invalid value for the %q field (at position %d)", unmarshalTypeError.Field, unmarshalTypeError.Offset)
			return &malformedRequest{status: http.StatusBadRequest, msg: msg}

		case strings.HasPrefix(err.Error(), "json: unknown field "):
			fieldName := strings.TrimPrefix(err.Error(), "json: unknown field ")
			msg := fmt.Sprintf("Request body contains unknown field %s", fieldName)
			return &malformedRequest{status: http.StatusBadRequest, msg: msg}

		case errors.Is(err, io.EOF):
			msg := "Request body must not be empty"
			return &malformedRequest{status: http.StatusBadRequest, msg: msg}

		case err.Error() == "http: request body too large":
			msg := "Request body must not be larger than 1MB"
			return &malformedRequest{status: http.StatusRequestEntityTooLarge, msg: msg}

		default:
			return err
		}
	}

	if *verbose {
		logBody, err := json.Marshal(dst)
		if err != nil {
			log.Println("Decoded", dst)
		} else {
			log.Println("Decoded", string(logBody))
		}
	}

	err = dec.Decode(&struct{}{})
	if err != io.EOF {
		msg := "Request body must only contain a single JSON object"
		return &malformedRequest{status: http.StatusBadRequest, msg: msg}
	}

	return nil
}

func malformedRequestResponse(w http.ResponseWriter, err error) {
	if err == nil {
		http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
		return
	}
	var mr *malformedRequest
	if errors.As(err, &mr) {
		log.Println(mr.msg)
		http.Error(w, mr.msg, mr.status)
	} else {
		log.Println(err.Error())
		http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
	}
}

func serveFile(w http.ResponseWriter, folder string, fileName string) {
	fullName := folder + "/" + fileName
	f, err := os.Open(fullName)
	defer f.Close()
	if err != nil {
		log.Println("Unknown file is requested", fullName)
		http.Error(w, "File not found.", 404)
		return
	}

	header := make([]byte, 512)
	f.Read(header)
	contentType := http.DetectContentType(header)

	stat, err := f.Stat()
	if err != nil {
		log.Println("Cannot stat", fullName, err)
		http.Error(w, "File not found.", 404)
		return
	}

	fileSize := strconv.Itoa(int(stat.Size()))

	w.Header().Set("Content-Disposition", "attachment; filename="+fileName)
	w.Header().Set("Content-Type", contentType)
	w.Header().Set("Content-Length", fileSize)

	f.Seek(0, 0)
	io.Copy(w, f)
}

func isTextRequested(r *http.Request) bool {
	_, ok := r.URL.Query()["text"]
	return ok
}

func internalServerError(w http.ResponseWriter) {
	http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
	log.Println(http.StatusText(http.StatusInternalServerError))
}

func errorResponse(w http.ResponseWriter, message string) {
	d := errorStatusResponse{message}
	respBody, err := json.Marshal(d)
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

func structToMap(item interface{}) map[string]interface{} {
	res := map[string]interface{}{}
	if item == nil {
		return res
	}
	v := reflect.TypeOf(item)
	reflectValue := reflect.ValueOf(item)
	reflectValue = reflect.Indirect(reflectValue)

	if v.Kind() == reflect.Ptr {
		v = v.Elem()
	}
	for i := 0; i < v.NumField(); i++ {
		tag := v.Field(i).Tag.Get("json")
		field := reflectValue.Field(i).Interface()
		if tag != "" && tag != "-" {
			if v.Field(i).Type.Kind() == reflect.Struct {
				res[tag] = structToMap(field)
			} else {
				res[tag] = field
			}
		}
	}
	return res
}

func textMarshalInterface(b *bytes.Buffer, d interface{}, path string) {
	if v := reflect.ValueOf(d); v.Kind() == reflect.Struct {
		textMarshalInterface(b, structToMap(d), path)
		return
	}

	switch d.(type) {
	case map[string]interface{}:
		for key, val := range d.(map[string]interface{}) {
			textMarshalInterface(b, val, path+"/"+key)
		}
	case []interface{}:
		for i, val := range d.([]interface{}) {
			textMarshalInterface(b, val, path+"/"+strconv.Itoa(i))
		}
	case float64:
		floatVal := d.(float64)
		if floatVal == math.Trunc(floatVal) {
			b.WriteString(fmt.Sprintf("%s=%d\n", path, int64(floatVal)))
			return
		}
		b.WriteString(fmt.Sprintf("%s=%v\n", path, floatVal))
	default:
		b.WriteString(fmt.Sprintf("%s=%v\n", path, d))
	}
}

func textMarshal(d interface{}) ([]byte, error) {
	b := bytes.NewBuffer(nil)
	textMarshalInterface(b, d, "")
	return b.Bytes(), nil
}

func dataResponse(w http.ResponseWriter, d interface{}, asText bool) {
	marshal := json.Marshal

	if asText {
		marshal = textMarshal
	}

	respBody, err := marshal(d)
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

func serveResponse(w http.ResponseWriter, r *http.Request) func(interface{}, error) {
	return func(d interface{}, err error) {
		if err != nil {
			internalServerError(w)
			return
		}
		dataResponse(w, d, isTextRequested(r))
	}
}

func serveSingleFunction(state *agentState, w http.ResponseWriter, r *http.Request, f func() (interface{}, error)) {
	if r.Method != "GET" {
		log.Println("Unknown method")
		http.Error(w, "Bad Request", http.StatusBadRequest)
		return
	}

	serveResponse(w, r)(f())
}

func contains(s []int, e int) bool {
	for _, a := range s {
		if a == e {
			return true
		}
	}
	return false
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
	return strings.Join(mapFunc(parts, func(a int64) string { return fmt.Sprintf("%02X", a) }), ":"), nil
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
		return []int{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11}
	case "dpu":
		return []int{0, 1, 2, 3, 4, 5, 6, 7, 8}
	case "optics":
		return []int{0, 4, 8, 12, 16, 20}
	case "dimm":
		return []int{0, 1, 2, 3}
	default:
		return nil
	}
}

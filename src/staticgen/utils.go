package main

import (
	"bytes"
	"encoding/json"
	"io/ioutil"
	"log"
	"os"
	"text/template"
)

type (
	// Initialize filewalk channel
	fileWalk chan string

	// Context for templates
	Context struct {
		Name        string `json:"name"`
		Description string `json:"description"`
		Domain      string `json:"domain"`
		Phone       string `json:"phone"`
		Address     string `json:"address"`
		Email       string `json:"email"`
	}
)

// Walk through folder
func (f fileWalk) Walk(path string, info os.FileInfo, err error) error {
	if err != nil {
		return err
	}
	if !info.IsDir() {
		f <- path
	}
	return nil
}

// Parse html templates
func parse(path, rel string) *bytes.Reader {
	file, err := os.Open(path)
	if err != nil {
		log.Println("Failed opening html file", path, err)
	}
	defer file.Close()
	jsonfile, _ := ioutil.ReadFile("data.json")
	context := Context{}

	_ = json.Unmarshal([]byte(jsonfile), &context)

	t, _ := template.ParseFiles(path)

	buffer := &bytes.Buffer{}

	t.Execute(buffer, context)

	return bytes.NewReader(buffer.Bytes())
}

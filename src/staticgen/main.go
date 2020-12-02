package main

import (
	"encoding/json"
	"fmt"
	"html/template"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"
)

// Route ...
type Route struct {
	source      string
	destination string
}

// Page ...
type Page struct {
	Title   string `json:"title"`
	Content string `json:"content"`
}

// copy an entire directory
func (r *Route) copy(path string, info os.FileInfo, err error) error {
	relPath := strings.Replace(path, r.source, "", 1)
	fmt.Println(filepath.Join(r.destination, relPath))

	switch ext := strings.ToLower(filepath.Ext(relPath)); ext {
	case ".html":
		file, _ := ioutil.ReadFile("data.json")
		page := Page{}

		_ = json.Unmarshal([]byte(file), &page)

		distFile, err := os.Create(filepath.Join(r.destination, relPath))
		if err != nil {
			return err
		}
		defer distFile.Close()

		t := template.Must(template.ParseFiles(filepath.Join(r.source, relPath)))
		t.Execute(distFile, page)
		return nil
	default:
		if relPath == "" {
			return nil
		}
		if info.IsDir() {
			return os.Mkdir(filepath.Join(r.destination, relPath), 0755)
		}
		data, err := ioutil.ReadFile(filepath.Join(r.source, relPath))
		if err != nil {
			return err
		}
		return ioutil.WriteFile(filepath.Join(r.destination, relPath), data, 0777)
	}
}

// generate static files
func generate(source, destination string) error {
	if _, err := os.Stat(destination); os.IsNotExist(err) {
		os.Mkdir(destination, 0755)
	}

	r := Route{source, destination}
	err := filepath.Walk(source, r.copy)
	return err
}

// WebsiteHandler recieves post requests
func WebsiteHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method == "GET" {
		err := generate("template", "public")
		if err != nil {
			fmt.Println(err)
		}
	} else {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
	}
}

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("/website/", WebsiteHandler)

	log.Println("listening on port 8000")
	log.Fatal(http.ListenAndServe(":8000", mux))
}

package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"staticgen/aws"
	"strings"
)

// HealthCheckHandler returns a simple message if the app is live.
func HealthCheckHandler(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "GoLang Template Generator is Healthy!")
}

// GenerateHandler generates website files from template files in s3
func GenerateHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	query := r.URL.Query()
	category := query.Get("category")
	domain := query.Get("domain")

	route := aws.Route{Category: category, Dir: domain}
	if r.Method == "POST" {
		// Download template files from s3
		route.FileDownload()
		log.Println("Downloaded files")

		// Generate content from template and context data
		context := aws.Context{}
		decoder := json.NewDecoder(r.Body)
		decoder.Decode(&context)
		route.Generate(&context, aws.WebsiteBucket, "template")

		// Remove local temp files
		err := os.RemoveAll("tmp/" + category)
		if err != nil {
			log.Println(err)
		}
	}
}

// TemplateHandler manages template files in s3
func TemplateHandler(w http.ResponseWriter, r *http.Request) {
	query := r.URL.Query()
	category := query.Get("category")
	route := aws.Route{Category: category, Dir: category}
	if r.Method == "POST" {
		// Recieve and unzip file
		foldername, err := Receive(r, category)
		if err != nil {
			log.Println(err)
			http.Error(w, "staticgen: uploaded zipfile failed", 400)
		}

		// Check if required files exist
		path := filepath.Join("tmp", category, foldername)
		if _, err := os.Stat(path + "/base.html"); os.IsNotExist(err) {
			http.Error(w, "Template incompatible, the required base.html file does not exist", 400)
			return
		} else if _, err = os.Stat(path + "/home.html"); os.IsNotExist(err) {
			http.Error(w, "Template incompatible, the required home.html file does not exist", 400)
			return
		} else if _, err = os.Stat(path + "/data.json"); os.IsNotExist(err) {
			http.Error(w, "Template incompatible, the required data.json file does not exist", 400)
			return
		}

		// Upload to S3
		route.Upload(foldername, aws.TemplateBucket)

		// Generate preview from context data and template
		data, _ := ioutil.ReadFile(filepath.Join(strings.Join([]string{"tmp", category, foldername}, "/"), "data.json"))
		context := aws.Context{}

		// Validate context data
		err = json.Unmarshal([]byte(data), &context)
		if err != nil {
			log.Println(err)
			http.Error(w, "staticgen: json file failed", 400)
		}

		route.Generate(&context, aws.TemplateBucket, foldername)

		// Remove local temp files
		err = os.RemoveAll("tmp/" + category)
		if err != nil {
			log.Println(err)
		}

	} else if r.Method == "GET" {
		w.Header().Set("Content-Type", "application/zip")
		w.Header().Set("Content-Disposition", fmt.Sprintf("attachment; filename=\"%s.zip\"", category))
		route.BufferDownload(w, aws.TemplateBucket)
	} else if r.Method == "DELETE" {
		route.Delete(aws.TemplateBucket)
	} else {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
	}
}

// WebsiteHandler generates static websites from templates
func WebsiteHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	query := r.URL.Query()
	domain := query.Get("domain")
	category := query.Get("category")

	route := aws.Route{Category: category, Dir: domain}
	if r.Method == "POST" {
		// Recieve and unzip file
		foldername, err := Receive(r, category)
		if err != nil {
			log.Println(err)
			http.Error(w, "staticgen: uploaded zipfile failed", 400)
		}

		// Check if required files exist
		if _, err := os.Stat(filepath.Join("tmp", category, foldername, "home.html")); os.IsNotExist(err) {
			http.Error(w, "Website content incompatible, the required home.html file does not exist", 400)
			return
		}

		// Upload to S3
		route.Upload(foldername, aws.WebsiteBucket)

		// Remove local temp files
		err = os.RemoveAll("tmp/" + category)
		if err != nil {
			log.Println(err)
		}
	} else if r.Method == "GET" {
		w.Header().Set("Content-Disposition", fmt.Sprintf("attachment; filename=\"%s.zip\"", "Website"))
		route.BufferDownload(w, aws.WebsiteBucket)
	} else if r.Method == "DELETE" {
		route.Delete(aws.WebsiteBucket)
	} else {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
	}
}

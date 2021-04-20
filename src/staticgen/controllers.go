package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"staticgen/aws"
)

type TemplateResp struct {
	IsGoTemplate bool `json:"is_go_template"`
}

// HealthCheckHandler returns a simple message if the app is live.
func HealthCheckHandler(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "Live and healthy")
}

// GenerateHandler generates website files from template files in s3
func GenerateHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	query := r.URL.Query()
	templateName := query.Get("template_name")
	domain := query.Get("domain")
	isTemplate := query.Get("is_template")

	route := aws.Route{TemplateName: templateName, Dir: domain}
	if r.Method == "POST" {
		// Download template files from s3
		route.FileDownload()
		log.Println("Downloaded files")

		// Generate content from template and context data
		context := aws.Context{}
		decoder := json.NewDecoder(r.Body)
		decoder.Decode(&context)
		route.Generate(&context, aws.WebsiteBucket, isTemplate, "template")

		// Remove local temp files
		err := os.RemoveAll("tmp/" + templateName)
		if err != nil {
			log.Println(err)
		}
	}
}

// TemplateHandler manages template files in s3
func TemplateHandler(w http.ResponseWriter, r *http.Request) {
	query := r.URL.Query()
	templateName := query.Get("template_name")
	route := aws.Route{TemplateName: templateName, Dir: templateName}
	if r.Method == "POST" {
		// Recieve and unzip file
		foldername, err := Receive(r, templateName)
		if err != nil {
			log.Println(err)
			http.Error(w, "staticgen: uploaded zipfile failed", 400)
		}

		// Check if required files exist
		path := filepath.Join("tmp", templateName, foldername)
		if _, err := os.Stat(path + "/home.html"); os.IsNotExist(err) {
			http.Error(w, "Template incompatible, the required home.html file does not exist", 400)
			return
		}

		// Upload website content if base.html is missing
		if _, err = os.Stat(path + "/base.html"); os.IsNotExist(err) {
			// Upload to S3
			route.Upload(foldername, aws.TemplateBucket)

			// Return IsGoTemplate as false
			resp := TemplateResp{
				IsGoTemplate: false,
			}

			err = json.NewEncoder(w).Encode(resp)
			if err != nil {
				http.Error(w, "Internal Server Error", http.StatusInternalServerError)
				return
			}
			return
		}

		// Upload to S3
		route.Upload(foldername, aws.TemplateBucket)

		// Generate preview from preview data and template
		context := aws.Context{
			CompanyName:   "{{ .CompanyName }}",
			Domain:        "{{ .Domain }}",
			Phone:         "{{ .Phone }}",
			StreetAddress: "{{ .StreetAddress }}",
			City:          "{{ .City }}",
			State:         "{{ .State }}",
			ZipCode:       "{{ .ZipCode }}",
			Email:         "{{ .Email }}",
		}

		route.Generate(&context, aws.TemplateBucket, "true", foldername)

		// Remove local temp files
		err = os.RemoveAll("tmp/" + templateName)
		if err != nil {
			log.Println(err)
		}

		// Return IsGoTemplate as true
		resp := TemplateResp{
			IsGoTemplate: true,
		}

		err = json.NewEncoder(w).Encode(resp)
		if err != nil {
			http.Error(w, "Internal Server Error", http.StatusInternalServerError)
			return
		}

	} else if r.Method == "GET" {
		w.Header().Set("Content-Type", "application/zip")
		w.Header().Set("Content-Disposition", fmt.Sprintf("attachment; filename=\"%s.zip\"", templateName))
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
	templateName := query.Get("template_name")

	route := aws.Route{TemplateName: templateName, Dir: domain}
	if r.Method == "POST" {
		// Recieve and unzip file
		foldername, err := Receive(r, templateName)
		if err != nil {
			log.Println(err)
			http.Error(w, "staticgen: uploaded zipfile failed", 400)
		}

		// Check if required files exist
		if _, err := os.Stat(filepath.Join("tmp", templateName, foldername, "home.html")); os.IsNotExist(err) {
			http.Error(w, "Website content incompatible, the required home.html file does not exist", 400)
			return
		}

		// Upload to S3
		route.Upload(foldername, aws.WebsiteBucket)

		// Remove local temp files
		err = os.RemoveAll("tmp/" + templateName)
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

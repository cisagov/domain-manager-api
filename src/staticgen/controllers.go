package main

import (
	"encoding/json"
	"net/http"
	"os"
)

// Set S3 bucket URL
var bucket = os.Getenv("TEMPLATE_BUCKET")

// WebsiteHandler generates static websites from templates
func WebsiteHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	query := r.URL.Query()
	category := query.Get("category")
	domain := query.Get("domain")

	route := Route{bucket, category, domain}
	if r.Method == "POST" {
		context := Context{}
		decoder := json.NewDecoder(r.Body)
		decoder.Decode(&context)
		route.generate(&context)
	} else if r.Method == "GET" {
		route.download()
	} else if r.Method == "DELETE" {
		route.delete()
	} else {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
	}
}

// TemplateHandler manages template files in s3
func TemplateHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	query := r.URL.Query()
	category := query.Get("category")
	route := Route{bucket, category, "template"}
	if r.Method == "POST" {
		route.upload()
	} else if r.Method == "GET" {
		route.download()
	} else if r.Method == "DELETE" {
		route.delete()
	} else {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
	}
}

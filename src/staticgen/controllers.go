package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"staticgen/aws"
)

// Set S3 bucket URL
var bucket = os.Getenv("TEMPLATE_BUCKET")

// WebsiteHandler generates static websites from templates
func WebsiteHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	query := r.URL.Query()
	category := query.Get("category")
	domain := query.Get("domain")

	route := aws.Route{Bucket: bucket, Category: category, Dir: domain}
	if r.Method == "POST" {
		context := aws.Context{}
		decoder := json.NewDecoder(r.Body)
		decoder.Decode(&context)
		route.Generate(&context)
	} else if r.Method == "GET" {
		w.Header().Set("Content-Disposition", fmt.Sprintf("attachment; filename=\"%s.zip\"", "Website"))
		route.Download(w)
	} else if r.Method == "DELETE" {
		route.Delete()
	} else {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
	}
}

// TemplateHandler manages template files in s3
func TemplateHandler(w http.ResponseWriter, r *http.Request) {
	query := r.URL.Query()
	category := query.Get("category")
	route := aws.Route{Bucket: bucket, Category: category, Dir: "template"}
	if r.Method == "POST" {
		route.Upload()
	} else if r.Method == "GET" {
		w.Header().Set("Content-Type", "application/zip")
		w.Header().Set("Content-Disposition", fmt.Sprintf("attachment; filename=\"%s.zip\"", category))
		route.Download(w)
	} else if r.Method == "DELETE" {
		route.Delete()
	} else {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
	}
}

package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"staticgen/aws"
)

// Set S3 bucket URL
var templateBucket = os.Getenv("TEMPLATE_BUCKET")
var websiteBucket = os.Getenv("WEBSITE_BUCKET")

// GenerateHandler generates website files from template files in s3
func GenerateHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	query := r.URL.Query()
	category := query.Get("category")
	domain := query.Get("domain")

	route := aws.Route{WebsiteBucket: websiteBucket, TemplateBucket: templateBucket, Category: category, Dir: domain}
	if r.Method == "POST" {
		context := aws.Context{}
		decoder := json.NewDecoder(r.Body)
		decoder.Decode(&context)
		route.Generate(&context)
	}
}

// TemplateHandler manages template files in s3
func TemplateHandler(w http.ResponseWriter, r *http.Request) {
	query := r.URL.Query()
	category := query.Get("category")
	route := aws.Route{WebsiteBucket: websiteBucket, TemplateBucket: templateBucket, Category: category, Dir: category}
	if r.Method == "POST" {
		// Recieve and unzip file
		foldername, err := Receive(r)
		if err != nil {
			log.Println(err)
			http.Error(w, "uploaded zipfile failed", 400)
		}
		// Upload to S3
		route.Upload(foldername, route.TemplateBucket)
	} else if r.Method == "GET" {
		w.Header().Set("Content-Type", "application/zip")
		w.Header().Set("Content-Disposition", fmt.Sprintf("attachment; filename=\"%s.zip\"", category))
		route.Download(w, route.TemplateBucket)
	} else if r.Method == "DELETE" {
		route.Delete(route.TemplateBucket)
	} else {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
	}
}

// WebsiteHandler generates static websites from templates
func WebsiteHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	query := r.URL.Query()
	domain := query.Get("website")
	category := query.Get("category")

	route := aws.Route{WebsiteBucket: websiteBucket, TemplateBucket: templateBucket, Category: category, Dir: domain}
	if r.Method == "POST" {
		// Recieve and unzip file
		foldername, err := Receive(r)
		if err != nil {
			log.Println(err)
			http.Error(w, "uploaded zipfile failed", 400)
		}
		// Upload to S3
		route.Upload(foldername, route.WebsiteBucket)
	} else if r.Method == "GET" {
		w.Header().Set("Content-Disposition", fmt.Sprintf("attachment; filename=\"%s.zip\"", "Website"))
		route.Download(w, route.WebsiteBucket)
	} else if r.Method == "DELETE" {
		route.Delete(route.WebsiteBucket)
	} else {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
	}
}

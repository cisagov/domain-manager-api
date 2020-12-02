package main

import (
	"net/http"
	"os"
)

// WebsiteHandler generates static websites from templates
func WebsiteHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	query := r.URL.Query()
	bucket := os.Getenv("TEMPLATE_BUCKET")
	category := query.Get("category")
	domain := query.Get("domain")

	route := Route{bucket, category, domain}
	if r.Method == "GET" {
		route.upload()
	} else if r.Method == "DELETE" {
		route.delete()
	} else {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
	}
}

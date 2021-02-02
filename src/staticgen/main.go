package main

import (
	"log"
	"net/http"
)

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("/health/", HealthCheckHandler)
	mux.HandleFunc("/generate/", GenerateHandler)
	mux.HandleFunc("/template/", TemplateHandler)
	mux.HandleFunc("/website/", WebsiteHandler)

	log.Println("listening on port 8000")
	log.Println(http.ListenAndServe(":8000", mux))
}

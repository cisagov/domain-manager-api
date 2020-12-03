package main

import (
	"log"
	"net/http"
)

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("/website/", WebsiteHandler)

	log.Println("listening on port 8000")
	log.Fatal(http.ListenAndServe(":8000", mux))
}
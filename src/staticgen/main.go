package main

import (
	"context"
	"encoding/json"
	"fmt"
	"html/template"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/awserr"
	"github.com/aws/aws-sdk-go/aws/request"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3"
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
	Phone   string `json:"phone"`
	Address string `json:"address"`
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

// upload to s3 bucket
func upload(category, filename string) {
	timeout := 60 * time.Second
	bucket := os.Getenv("TEMPLATE_BUCKET")

	sess := session.Must(session.NewSession()) // initialize session
	svc := s3.New(sess)

	ctx := context.Background()

	var cancelFn func() // Ensure context is canceled to prevent leaking
	if timeout > 0 {
		ctx, cancelFn = context.WithTimeout(ctx, timeout)
	}
	if cancelFn != nil {
		defer cancelFn()
	}

	data, _ := os.Open(filename)

	// Upload objects to S3
	_, err := svc.PutObjectWithContext(ctx, &s3.PutObjectInput{
		Bucket: aws.String(bucket),
		Key:    aws.String(category + "/" + filename),
		Body:   data,
	})

	if err != nil {
		if aerr, ok := err.(awserr.Error); ok && aerr.Code() == request.CanceledErrorCode {
			fmt.Fprintf(os.Stderr, "upload canceled due to timeout, %v\n", err)
		} else {
			fmt.Fprintf(os.Stderr, "failed to upload object, %v\n", err)
		}
		os.Exit(1)
	}

	fmt.Printf("successfully uploaded file to %s/%s\n", bucket, category)
}

// WebsiteHandler generates static websites from templates
func WebsiteHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	if r.Method == "GET" {
		// err := generate("template", "public")
		// if err != nil {
		// 	fmt.Println(err)
		// }
		query := r.URL.Query()
		category := query.Get("category")
		filename := query.Get("filename")

		upload(category, filename)
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

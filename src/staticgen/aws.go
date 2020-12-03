package main

import (
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strings"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3"
	"github.com/aws/aws-sdk-go/service/s3/s3manager"
)

// Route for s3 bucket
type Route struct {
	bucket   string
	category string
	domain   string
}

// upload to s3 bucket
func (r *Route) upload() {
	walker := make(fileWalk)
	go func() {
		// Gather the files to upload by walking the path recursively
		if err := filepath.Walk("templates/", walker.Walk); err != nil {
			log.Fatalln("Walk failed:", err)
		}
		close(walker)
	}()

	// For each file found walking, upload it to S3
	uploader := s3manager.NewUploader(session.New())
	for path := range walker {
		rel, err := filepath.Rel("templates/", path)
		if err != nil {
			log.Fatalln("Unable to get relative path:", path, err)
		}

		var contenttype string
		var file *os.File

		ext := strings.ToLower(filepath.Ext(path))
		if ext == ".html" {
			contenttype = "text/html"
			file = parse(path, rel)
		} else if ext == ".css" {
			contenttype = "text/css"
			file, err = os.Open(path)
			if err != nil {
				log.Println("Failed opening css file", path, err)
				continue
			}
		} else {
			contenttype = "text/css"
			file, err = os.Open(path)
			if err != nil {
				log.Println("Failed opening file", path, err)
				continue
			}
		}

		defer file.Close()

		_, err = uploader.Upload(&s3manager.UploadInput{
			Bucket:      &r.bucket,
			ContentType: &contenttype,
			Key:         aws.String(filepath.Join(r.category, r.domain, rel)),
			Body:        file,
		})
		if err != nil {
			log.Fatalln("Failed to upload", path, err)
		}

		fmt.Printf("successfully uploaded %s/%s/%s/%s\n", r.bucket, r.category, r.domain, rel)
	}
}

// delete from s3 bucket
func (r *Route) delete() {
	sess, _ := session.NewSession()
	svc := s3.New(sess)

	iter := s3manager.NewDeleteListIterator(svc, &s3.ListObjectsInput{
		Bucket: aws.String(r.bucket),
		Prefix: aws.String(filepath.Join(r.category, r.domain)),
	})

	if err := s3manager.NewBatchDeleteWithClient(svc).Delete(aws.BackgroundContext(), iter); err != nil {
		fmt.Printf("Unable to delete objects from bucket %q, %v", r.bucket, err)
		os.Exit(1)
	}

	fmt.Printf("successfully deleted staticfiles from %s/%s/%s\n", r.bucket, r.category, r.domain)
}

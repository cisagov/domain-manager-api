package aws

import (
	"fmt"
	"io"
	"log"
	"os"
	"path/filepath"
	"strings"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3/s3manager"
)

// Upload files to s3 bucket
func (r *Route) Upload(foldername string, bucket string) {
	walker := make(fileWalk)
	go func() {
		// Gather the files to upload by walking the path recursively
		if err := filepath.Walk(filepath.Join("tmp/"+foldername), walker.Walk); err != nil {
			log.Println("Walk failed:", err)
		}
		close(walker)
	}()

	// For each file found walking, upload it to S3
	uploader := s3manager.NewUploader(session.New())
	for path := range walker {
		rel, err := filepath.Rel("tmp/"+foldername, path)
		if err != nil {
			log.Println("Unable to get relative path:", path, err)
		}
		rel = strings.Replace(rel, "\\", "/", -1)
		var contenttype string
		var file io.Reader

		ext := strings.ToLower(filepath.Ext(path))
		if ext == ".html" {
			contenttype = "text/html"
		} else if ext == ".css" {
			contenttype = "text/css"
		} else {
			contenttype = "text/plain"
		}

		file, err = os.Open(path)
		if err != nil {
			log.Println("Failed opening file", path, err)
			continue
		}

		uploadKey := []string{r.Dir, rel}
		_, err = uploader.Upload(&s3manager.UploadInput{
			Bucket:      &bucket,
			ContentType: &contenttype,
			Key:         aws.String(strings.Join(uploadKey, "/")),
			Body:        file,
		})
		if err != nil {
			log.Println("Failed to upload", path, err)
		}

		fmt.Printf("successfully uploaded %s/%s/%s\n", bucket, r.Dir, rel)
	}

	// Remove local temp files
	err := os.RemoveAll("tmp/" + foldername)
	if err != nil {
		log.Println(err)
	}
}

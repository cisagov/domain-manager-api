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
func (r *Route) Upload() {
	walker := make(fileWalk)
	go func() {
		// Gather the files to upload by walking the path recursively
		if err := filepath.Walk(r.Dir, walker.Walk); err != nil {
			log.Fatalln("Walk failed:", err)
		}
		close(walker)
	}()

	// For each file found walking, upload it to S3
	uploader := s3manager.NewUploader(session.New())
	for path := range walker {
		rel, err := filepath.Rel(r.Dir, path)
		if err != nil {
			log.Fatalln("Unable to get relative path:", path, err)
		}
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

		_, err = uploader.Upload(&s3manager.UploadInput{
			Bucket:      &r.Bucket,
			ContentType: &contenttype,
			Key:         aws.String(filepath.Join(r.Category, "template", rel)),
			Body:        file,
		})
		if err != nil {
			log.Fatalln("Failed to upload", path, err)
		}

		fmt.Printf("successfully uploaded %s/%s/%s/%s\n", r.Bucket, r.Category, "template", rel)
	}
}

package aws

import (
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
func (r *Route) Upload(foldername, bucket string) {
	walker := make(fileWalk)
	go func() {
		// Gather the files to upload by walking the path recursively
		if err := filepath.Walk(filepath.Join("tmp/"+r.TemplateName+"/"+foldername), walker.Walk); err != nil {
			log.Println("Walk failed:", err)
		}
		close(walker)
	}()

	// For each file found walking, upload it to S3
	sess := session.Must(session.NewSession())
	uploader := s3manager.NewUploader(sess)
	for path := range walker {
		rel, err := filepath.Rel("tmp/"+r.TemplateName+"/"+foldername, path)
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

		var key []string
		if bucket == TemplateBucket {
			key = []string{r.Dir, "template", rel}
		} else {
			key = []string{r.Dir, rel}
		}

		uploadKey := strings.Join(key, "/")
		_, err = uploader.Upload(&s3manager.UploadInput{
			Bucket:      &bucket,
			ContentType: &contenttype,
			Key:         aws.String(uploadKey),
			Body:        file,
		})
		if err != nil {
			log.Println("Failed to upload", path, err)
		}

		log.Printf("successfully uploaded %s/%s\n", bucket, uploadKey)
	}
}

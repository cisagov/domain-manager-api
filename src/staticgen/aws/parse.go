package aws

import (
	"bytes"
	"fmt"
	"html/template"
	"io"
	"log"
	"os"
	"path/filepath"
	"strings"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3/s3manager"
)

// Generate static files and upload static to s3 bucket
func (r *Route) Generate(ctx *Context) {
	walker := make(fileWalk)
	go func() {
		// Gather the files to upload by walking the path recursively
		if err := filepath.Walk("template/", walker.Walk); err != nil {
			log.Fatalln("Walk failed:", err)
		}
		close(walker)
	}()

	// For each file found walking, upload it to S3
	uploader := s3manager.NewUploader(session.New())
	for path := range walker {
		if !strings.Contains(path, "base.html") {
			rel, err := filepath.Rel("template/", path)
			if err != nil {
				log.Fatalln("Unable to get relative path:", path, err)
			}
			var contenttype string
			var file io.Reader

			ext := strings.ToLower(filepath.Ext(path))
			if ext == ".html" {
				contenttype = "text/html"
				file = parse(path, rel, ctx)
			} else if ext == ".css" {
				contenttype = "text/css"
				file, err = os.Open(path)
				if err != nil {
					log.Println("Failed opening css file", path, err)
					continue
				}
			} else {
				contenttype = "text/plain"
				file, err = os.Open(path)
				if err != nil {
					log.Println("Failed opening file", path, err)
					continue
				}
			}

			_, err = uploader.Upload(&s3manager.UploadInput{
				Bucket:      &r.Bucket,
				ContentType: &contenttype,
				Key:         aws.String(filepath.Join(r.Category, r.Dir, rel)),
				Body:        file,
			})
			if err != nil {
				log.Fatalln("Failed to upload", path, err)
			}

			fmt.Printf("successfully uploaded %s/%s/%s/%s\n", r.Bucket, r.Category, r.Dir, rel)
		}
	}
}

// Parse html templates
func parse(path, rel string, ctx *Context) *bytes.Reader {
	file, err := os.Open(path)
	if err != nil {
		log.Println("Failed opening html file", path, err)
	}
	defer file.Close()

	t := template.Must(template.ParseFiles(filepath.Dir(path)+"/base.html", path))
	if err != nil {
		log.Println("Failed to parse html files", err)
	}
	buffer := &bytes.Buffer{}

	t.ExecuteTemplate(buffer, "base", ctx)

	return bytes.NewReader(buffer.Bytes())
}

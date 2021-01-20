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
	"github.com/aws/aws-sdk-go/service/s3"
	"github.com/aws/aws-sdk-go/service/s3/s3manager"
)

// Generate static files and upload static to s3 bucket
func (r *Route) Generate(ctx *Context, bucket, foldername string) {
	// Gather the files to upload by walking the path recursively
	walker := make(fileWalk)
	// Run concurrently
	go func() {
		if err := filepath.Walk(strings.Join([]string{"tmp", r.Category, foldername}, "/"), walker.Walk); err != nil {
			log.Println("Walk failed:", err)
		}
		close(walker)
	}()

	// For each file found walking, upload it to S3
	uploader := s3manager.NewUploader(session.New())
	for path := range walker {
		if !strings.Contains(path, "base.html") {

			// set tmp folder prefix
			rel, err := filepath.Rel(strings.Join([]string{"tmp", r.Category, foldername}, "/"), path)
			if err != nil {
				log.Println("Unable to get relative path:", path, err)
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

			var key []string
			if bucket == TemplateBucket {
				key = []string{r.Dir, "preview", rel}
			} else {
				key = []string{r.Dir, rel}
			}

			uploadKey := strings.Replace(strings.Join(key, "/"), "\\", "/", -1)
			_, err = uploader.Upload(&s3manager.UploadInput{
				Bucket:      &bucket,
				ContentType: &contenttype,
				Key:         aws.String(uploadKey),
				Body:        file,
			})
			if err != nil {
				log.Println("Failed to upload", path, err)
			}

			fmt.Printf("successfully uploaded %s/%s\n", bucket, uploadKey)
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

// FileDownload downloads from s3 bucket to temp folder
func (r *Route) FileDownload() {
	manager := s3manager.NewDownloader(session.New())

	directory := filepath.Join("tmp/", r.Category)
	d := Downloader{bucket: TemplateBucket, dir: directory, Downloader: manager}
	client := s3.New(session.New())

	bucketPrefix := strings.Join([]string{r.Category, "template"}, "/")
	params := &s3.ListObjectsInput{Bucket: &TemplateBucket, Prefix: &bucketPrefix}
	client.ListObjectsPages(params, d.eachPage)
}

// eachPage ...
func (d *Downloader) eachPage(page *s3.ListObjectsOutput, more bool) bool {
	for _, obj := range page.Contents {
		d.downloadToFile(*obj.Key)
	}

	return true
}

// download to file
func (d *Downloader) downloadToFile(key string) {
	// Create the directories in the path
	file := filepath.Join("tmp/" + key)

	if err := os.MkdirAll(filepath.Dir(file), 0775); err != nil {
		panic(err)
	}

	// Set up the local file
	fd, err := os.Create(file)
	if err != nil {
		panic(err)
	}
	defer fd.Close()

	// Download the file using the AWS SDK for Go
	fmt.Printf("Downloading s3://%s/%s to %s...\n", d.bucket, key, file)
	params := &s3.GetObjectInput{Bucket: &d.bucket, Key: &key}
	d.Download(fd, params)
}

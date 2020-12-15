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
func (r *Route) Generate(ctx *Context) {
	// Download template files from s3
	download(r.Bucket, r.Category, r.Dir)

	// Gather the files to upload by walking the path recursively
	walker := make(fileWalk)
	// Run concurrently
	go func() {
		if err := filepath.Walk(filepath.Join("tmp/", r.Category), walker.Walk); err != nil {
			log.Fatalln("Walk failed:", err)
		}
		close(walker)
	}()

	// For each file found walking, upload it to S3
	uploader := s3manager.NewUploader(session.New())
	for path := range walker {
		if !strings.Contains(path, "base.html") {
			rel, err := filepath.Rel("tmp/"+r.Category, path)
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
	// Remove local temp files
	err := os.RemoveAll("tmp/" + r.Category)
	if err != nil {
		log.Fatal(err)
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

// download from s3 bucket
func download(bucket, category, dir string) {
	manager := s3manager.NewDownloader(session.New())
	directory := filepath.Join("tmp/", category)
	d := Downloader{bucket: bucket, dir: directory, Downloader: manager, category: category}
	client := s3.New(session.New())
	params := &s3.ListObjectsInput{Bucket: &bucket, Prefix: &category}
	client.ListObjectsPages(params, d.eachPage)

	// Remove local temp files
	err := os.RemoveAll("tmp/" + dir)
	if err != nil {
		log.Fatal(err)
	}
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
	rel, _ := filepath.Rel(d.category+"/template/", key)
	file := filepath.Join("tmp/" + d.category + "/" + rel)

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

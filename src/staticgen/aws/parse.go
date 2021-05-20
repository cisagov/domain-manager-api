package aws

import (
	"bytes"
	"fmt"
	"html/template"
	"io"
	"io/fs"
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
func (r *Route) Generate(ctx *Context, bucket, isTemplate, foldername string) {
	// Gather the files to upload by walking the path recursively
	walker := make(fileWalk)
	// Run concurrently
	go func() {
		if err := filepath.Walk(strings.Join([]string{"tmp", r.TemplateName, foldername}, "/"), walker.Walk); err != nil {
			log.Println("Walk failed:", err)
		}
		close(walker)
	}()

	// get path for base.html
	var basePath string
	_ = filepath.Walk(".", func(path string, info fs.FileInfo, err error) error {
		if err != nil {
			fmt.Println(err)
		}
		if !info.IsDir() && info.Name() ==
			"base.html" {
			basePath = path
		}
		return nil
	})

	// For each file found walking, upload it to S3
	for path := range walker {
		if path != basePath {
			var contenttype string
			var file io.Reader
			var err error

			ext := strings.ToLower(filepath.Ext(path))
			if ext == ".html" && isTemplate == "true" {
				contenttype = "text/html"
				file = parse(path, basePath, ctx)
			} else if ext == ".html" {
				log.Println("opening as html file")
				contenttype = "text/html"
				file, err = os.Open(path)
				if err != nil {
					log.Println("Failed opening html file", path, err)
					continue
				}
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

			// set tmp folder prefix
			rel, err := filepath.Rel(strings.Join([]string{"tmp", r.TemplateName, foldername}, "/"), path)
			if err != nil {
				log.Println("Unable to get relative path:", path, err)
			}

			var key []string
			if bucket == TemplateBucket {
				key = []string{r.Dir, "preview", rel}
			} else {
				key = []string{r.Dir, rel}
			}

			// initialize s3 uploader
			sess := session.Must(session.NewSession())
			uploader := s3manager.NewUploader(sess)
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
func parse(path, base string, ctx *Context) *bytes.Reader {
	file, err := os.Open(path)
	if err != nil {
		log.Println("Failed opening html file", path, err)
	}
	defer file.Close()

	t := template.Must(template.ParseFiles(base, path))
	if err != nil {
		log.Println("Failed to parse html files", err)
	}
	buffer := &bytes.Buffer{}

	t.ExecuteTemplate(buffer, "base", ctx)

	return bytes.NewReader(buffer.Bytes())
}

// FileDownload downloads from s3 bucket to temp folder
func (r *Route) FileDownload() {
	sess := session.Must(session.NewSession())
	manager := s3manager.NewDownloader(sess)

	directory := filepath.Join("tmp/", r.TemplateName)
	d := Downloader{bucket: TemplateBucket, dir: directory, Downloader: manager}
	client := s3.New(sess)

	bucketPrefix := strings.Join([]string{r.TemplateName, "template"}, "/")
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

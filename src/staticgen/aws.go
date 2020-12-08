package main

import (
	"fmt"
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

// Route for s3 bucket
type Route struct {
	bucket   string
	category string
	dir      string
}

// Downloader for s3 bucket
type Downloader struct {
	*s3manager.Downloader
	bucket, dir string
}

// generate static files and upload static to s3 bucket
func (r *Route) generate(ctx *Context) {
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
				Bucket:      &r.bucket,
				ContentType: &contenttype,
				Key:         aws.String(filepath.Join(r.category, r.dir, rel)),
				Body:        file,
			})
			if err != nil {
				log.Fatalln("Failed to upload", path, err)
			}

			fmt.Printf("successfully uploaded %s/%s/%s/%s\n", r.bucket, r.category, r.dir, rel)
		}
	}
}

// upload files to s3 bucket
func (r *Route) upload() {
	walker := make(fileWalk)
	go func() {
		// Gather the files to upload by walking the path recursively
		if err := filepath.Walk(r.dir, walker.Walk); err != nil {
			log.Fatalln("Walk failed:", err)
		}
		close(walker)
	}()

	// For each file found walking, upload it to S3
	uploader := s3manager.NewUploader(session.New())
	for path := range walker {
		rel, err := filepath.Rel(r.dir, path)
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
			Bucket:      &r.bucket,
			ContentType: &contenttype,
			Key:         aws.String(filepath.Join(r.category, "template", rel)),
			Body:        file,
		})
		if err != nil {
			log.Fatalln("Failed to upload", path, err)
		}

		fmt.Printf("successfully uploaded %s/%s/%s/%s\n", r.bucket, r.category, "template", rel)
	}
}

// delete files from s3 bucket
func (r *Route) delete() {
	sess, _ := session.NewSession()
	svc := s3.New(sess)

	iter := s3manager.NewDeleteListIterator(svc, &s3.ListObjectsInput{
		Bucket: aws.String(r.bucket),
		Prefix: aws.String(filepath.Join(r.category, r.dir)),
	})

	if err := s3manager.NewBatchDeleteWithClient(svc).Delete(aws.BackgroundContext(), iter); err != nil {
		fmt.Printf("Unable to delete objects from bucket %q, %v", r.bucket, err)
		os.Exit(1)
	}

	fmt.Printf("successfully deleted staticfiles from %s/%s/%s\n", r.bucket, r.category, r.dir)
}

// download from s3 bucket
func (r *Route) download() {
	manager := s3manager.NewDownloader(session.New())
	dir := filepath.Join(r.category, r.dir)
	d := Downloader{bucket: r.bucket, dir: dir, Downloader: manager}

	client := s3.New(session.New())
	params := &s3.ListObjectsInput{Bucket: &r.bucket, Prefix: &dir}
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
	file := filepath.Join(d.dir, key)
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

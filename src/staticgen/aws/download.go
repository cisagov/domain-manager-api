package aws

import (
	"archive/zip"
	"bytes"
	"fmt"
	"io"
	"log"
	"net/http"
	"path/filepath"

	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3"
	"github.com/aws/aws-sdk-go/service/s3/s3manager"
)

// Downloader for s3 bucket
type Downloader struct {
	*s3manager.Downloader
	bucket, dir string
	writer      http.ResponseWriter
}

// FakeWriterAt fakes AWS NewWriter Struct
type FakeWriterAt struct {
	w io.Writer
}

// WriteAt fakes AWS write at method
func (fw FakeWriterAt) WriteAt(p []byte, offset int64) (n int, err error) {
	// ignore 'offset' because we forced sequential downloads
	return fw.w.Write(p)
}

// Download from s3 bucket
func (r *Route) Download(w http.ResponseWriter, bucket string) {
	manager := s3manager.NewDownloader(session.New())
	dir := filepath.Join(r.Dir)
	d := Downloader{bucket: bucket, dir: dir, Downloader: manager, writer: w}

	client := s3.New(session.New())
	params := &s3.ListObjectsInput{Bucket: &bucket, Prefix: &dir}
	client.ListObjectsPages(params, d.toZip)
}

// toZip downloads all files in the specified bucket prefix to zip
func (d *Downloader) toZip(page *s3.ListObjectsOutput, more bool) bool {
	buff := new(bytes.Buffer)
	writer := zip.NewWriter(buff)
	for _, obj := range page.Contents {
		d.downloadToBuffer(*obj.Key, writer)
	}

	err := writer.Close()
	if err != nil {
		log.Println(err)
	}
	io.Copy(d.writer, buff)

	return true
}

// download to buffer
func (d *Downloader) downloadToBuffer(key string, writer *zip.Writer) {
	// Create file in memory
	f, err := writer.Create(key)
	if err != nil {
		log.Println(err)
	}

	// Download object using the AWS SDK
	fmt.Printf("Downloading s3://%s/%s...\n", d.bucket, key)
	params := &s3.GetObjectInput{Bucket: &d.bucket, Key: &key}
	d.Download(FakeWriterAt{f}, params)
	d.Concurrency = 1
}

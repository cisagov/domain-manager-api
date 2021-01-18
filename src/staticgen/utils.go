package main

import (
	"archive/zip"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"
)

// Receive a zip file from a post request
func Receive(reader *http.Request, category string) (string, error) {
	err := reader.ParseMultipartForm(10 << 20)
	if err != nil {
		panic(err)
	}

	file, _, err := reader.FormFile("zip")
	if err != nil {
		log.Println(err)
		return "", err
	}

	defer file.Close()

	// create tmp folder if it doesn't exist
	if _, err := os.Stat("tmp"); os.IsNotExist(err) {
		os.Mkdir("tmp", 0775)
	}
	tempFile, err := ioutil.TempFile("tmp", "upload-*.zip")
	if err != nil {
		log.Println(err)
		return "", err
	}
	defer tempFile.Close()
	fileBytes, err := ioutil.ReadAll(file)
	if err != nil {
		log.Println(err)
		return "", err
	}
	tempFile.Write(fileBytes)

	// Unzip Tempfile
	foldername, err := Unzip(tempFile.Name(), "tmp/"+category)
	if err != nil {
		log.Println(err)
		return "", err
	}

	// Remove Tempfile
	os.Remove(tempFile.Name())

	return foldername, nil
}

// Unzip will decompress a zip archive
func Unzip(src string, dest string) (string, error) {

	var foldername string

	r, err := zip.OpenReader(src)
	if err != nil {
		return foldername, err
	}
	defer r.Close()

	foldername = filepath.Dir(r.File[0].Name)

	for _, f := range r.File {
		// Store filename/path for returning and using later on
		fpath := filepath.Join(dest, f.Name)

		// Check for ZipSlip. More Info: http://bit.ly/2MsjAWE
		if !strings.HasPrefix(fpath, filepath.Clean(dest)+string(os.PathSeparator)) {
			return foldername, fmt.Errorf("%s: illegal file path", fpath)
		}

		if f.FileInfo().IsDir() {
			// Make Folder
			os.MkdirAll(fpath, os.ModePerm)
			continue
		}

		// Make File
		if err = os.MkdirAll(filepath.Dir(fpath), os.ModePerm); err != nil {
			return foldername, err
		}

		outFile, err := os.OpenFile(fpath, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, f.Mode())
		if err != nil {
			return foldername, err
		}

		rc, err := f.Open()
		if err != nil {
			return foldername, err
		}

		_, err = io.Copy(outFile, rc)

		// Close the file without defer to close before next iteration of loop
		outFile.Close()
		rc.Close()

		if err != nil {
			return foldername, err
		}
	}
	return foldername, nil
}

package main

import (
	"bytes"
	"log"
	"os"
	"path/filepath"
	"text/template"
)

type (
	// Initialize filewalk channel
	fileWalk chan string

	// Context for templates
	Context struct {
		Name        string `json:"name"`
		Description string `json:"description"`
		Domain      string `json:"domain"`
		Phone       string `json:"phone"`
		Address     string `json:"address"`
		Email       string `json:"email"`
	}
)

// Walk through folder
func (f fileWalk) Walk(path string, info os.FileInfo, err error) error {
	if err != nil {
		return err
	}

	if !info.IsDir() {
		f <- path
	}
	return nil
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

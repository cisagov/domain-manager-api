package main

import (
	"os"
)

// fileWalk ...
type fileWalk chan string

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

// Context for templates
type Context struct {
	Title   string `json:"title"`
	Content string `json:"content"`
	Phone   string `json:"phone"`
	Address string `json:"address"`
}

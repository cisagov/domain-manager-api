package main

import (
	"os"
)

type (
	// Initialize filewalk channel
	fileWalk chan string

	// Context for templates
	Context struct {
		Name        string `json:"name"`
		Description string `json:"description"`
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

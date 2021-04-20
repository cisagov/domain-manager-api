package aws

import (
	"os"
)

var (
	// TemplateBucket sets S3 template bucket URL
	TemplateBucket = os.Getenv("TEMPLATE_BUCKET")

	// WebsiteBucket sets S3 website bucket URL
	WebsiteBucket = os.Getenv("WEBSITE_BUCKET")
)

type (
	// Initialize filewalk channel
	fileWalk chan string

	// Route for s3 bucket
	Route struct {
		TemplateName string
		Dir          string
	}

	// Context for templates
	Context struct {
		CompanyName string `json:"CompanyName"`
		Description string `json:"Description"`
		Domain      string `json:"Domain"`
		Phone       string `json:"Phone"`
		Address     string `json:"Address"`
		City        string `json:"City"`
		State       string `json:"State"`
		Email       string `json:"Email"`
		Zip         []byte `json:"Zip"`
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

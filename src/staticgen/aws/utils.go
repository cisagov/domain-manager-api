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
		CompanyName string `json:"company_name"`
		Description string `json:"description"`
		Domain      string `json:"domain"`
		Phone       string `json:"phone"`
		Address     string `json:"address"`
		City        string `json:"city"`
		State       string `json:"state"`
		Email       string `json:"email"`
		Zip         []byte `json:"zip"`
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

package aws

import (
	"fmt"
	"os"
	"path/filepath"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3"
	"github.com/aws/aws-sdk-go/service/s3/s3manager"
)

// Delete files from s3 bucket
func (r *Route) Delete() {
	sess, _ := session.NewSession()
	svc := s3.New(sess)

	iter := s3manager.NewDeleteListIterator(svc, &s3.ListObjectsInput{
		Bucket: aws.String(r.Bucket),
		Prefix: aws.String(filepath.Join(r.Category, r.Dir)),
	})

	if err := s3manager.NewBatchDeleteWithClient(svc).Delete(aws.BackgroundContext(), iter); err != nil {
		fmt.Printf("Unable to delete objects from bucket %q, %v", r.Bucket, err)
		os.Exit(1)
	}

	fmt.Printf("successfully deleted staticfiles from %s/%s/%s\n", r.Bucket, r.Category, r.Dir)
}

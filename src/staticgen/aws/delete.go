package aws

import (
	"log"
	"path/filepath"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3"
	"github.com/aws/aws-sdk-go/service/s3/s3manager"
)

// Delete files from s3 bucket
func (r *Route) Delete(bucket string) {
	sess, _ := session.NewSession()
	svc := s3.New(sess)

	iter := s3manager.NewDeleteListIterator(svc, &s3.ListObjectsInput{
		Bucket: aws.String(bucket),
		Prefix: aws.String(filepath.Join(r.Dir)),
	})

	if err := s3manager.NewBatchDeleteWithClient(svc).Delete(aws.BackgroundContext(), iter); err != nil {
		log.Printf("Unable to delete objects from bucket %q, %v", bucket, err)
	}

	log.Printf("successfully deleted staticfiles from %s/%s\n", bucket, r.Dir)
}

aws ecr create-repository --repository-name grayscaler --region us-west-2 && aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 591864715973.dkr.ecr.us-west-2.amazonaws.com && docker build -t grayscaler ./grayscaling && docker tag grayscaler 591864715973.dkr.ecr.us-west-2.amazonaws.com/grayscaler && docker push 591864715973.dkr.ecr.us-west-2.amazonaws.com/grayscaler && sam package --template-file template.yaml --output-template-file package.yml --s3-bucket iv-alex-oregon-bucket1 --image-repository 591864715973.dkr.ecr.us-west-2.amazonaws.com/grayscaler && sam deploy --template-file ./package.yml --stack-name grayscaler --image-repository 591864715973.dkr.ecr.us-west-2.amazonaws.com/grayscaler --capabilities CAPABILITY_IAM --parameter-overrides destBucket=iv-alex-oregon-bucket1
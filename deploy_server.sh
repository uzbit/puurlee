#!/bin/bash
cd server
docker build --platform=linux/amd64 -f chat/Dockerfile -t gcr.io/puurlee/chat .
docker push gcr.io/puurlee/chat
docker build --platform=linux/amd64 -f file_to_nosql/Dockerfile -t gcr.io/puurlee/file_to_nosql .
docker push gcr.io/puurlee/file_to_nosql
docker build --platform=linux/amd64 -f embeddings/Dockerfile -t gcr.io/puurlee/embeddings .
docker push gcr.io/puurlee/embeddings
docker build --platform=linux/amd64 -f clear_user_data/Dockerfile -t gcr.io/puurlee/clear_user_data .
docker push gcr.io/puurlee/clear_user_data

docker system prune




<img src="http://cdn2.hubspot.net/hubfs/143457/docker_and_kubernetes.jpg" alt="" data-canonical-src="http://cdn2.hubspot.net/hubfs/143457/docker_and_kubernetes.jpg" width="170" height="80" /><a href="https://www.mabl.com/?utm_campaign=gcp&utm_source=gh&utm_medium=k8demos"><img src="http://www.mabl.com/wp-content/uploads/2017/05/logo.png" alt="" data-canonical-src="http://www.mabl.com/wp-content/uploads/2017/05/logo.png" width="80" height="80" /></a>

## Kubernetes Job Submission Demo

Simple demo to send a lot of sat imagery analysis off to a Kubernetes cluster.

Part of (insert slideshare link here) [Boston Google Cloud Meetup](https://www.meetup.com/Boston-Google-Cloud-Meetup/) [September Presentation](https://www.meetup.com/Boston-Google-Cloud-Meetup/events/242964121/) @ [mabl](https://www.mabl.com/?utm_campaign=gcp&utm_source=gh&utm_medium=k8demos).

**WARNING** this demo uses GCP resources. This may run up a bill. Be aware of your resource usage.

## Setup:

1. Place your Firebase ServiceAcount.json key into `docker/firebase-service-account.json`
2. Let the winged monkeys fly


```bash

# Configs
PROJECT_ID='your-project-id'
CLUSTER_NAME='whaler-captain'
CLUSTER_ZONE='us-central1-a'
IMAGE_TAG"gcr.io/${PROJECT_ID}/sat-cruncher:v1"

# Build Docker file
docker build -f docker/Dockerfile -t ${IMAGE_TAG} .

# Push image to GCR
gcloud docker -- push ${IMAGE_TAG}

# Open a proxy to the cluster
gcloud container clusters get-credentials ${CLUSTER_NAME} --zone ${CLUSTER_ZONE} --project ${PROJECT_ID}
kubectl proxy

# Run the submitter script
./submit_jobs.py ${IMAGE_TAG}

```

## Monitor the Jobs

Visit [localhost:8001/ui](http://localhost:8001/ui) or

```bash

# Show all nodes
kubectl get nodes

# Show all pods (jobs)
kubectl get pods
``` 



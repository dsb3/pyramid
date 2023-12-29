# pyramid
Horst


# Running in container

podman build -t whatever .
podman run -ti -p 5000:5000 --rm --name pyramid whatever


# Running in GAE

gcloud auth login
gcloud config set project whatever
gcloud app deploy -v v1




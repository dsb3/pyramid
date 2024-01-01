# pyramid
Horst


# Running in container

podman build -t whatever .
podman run -ti -p 5000:5000 --rm --name pyramid whatever


# Running in GAE

cd ./app/
gcloud auth login
gcloud config set project whatever
gcloud app deploy -v v1


# Running in local debug mode (reload app on code changes)

cd ./app/
export FLASK_DEBUG=1
flask run



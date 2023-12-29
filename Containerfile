FROM python:3.11-alpine
MAINTAINER Dave Baker <dave@dsb3.com>

EXPOSE 5000

# bash is not needed but just makes diags more comfortable
RUN apk update && \
    apk upgrade && \
    apk add bash


# Creates /rsync directory where we'll drop our configs
RUN adduser -h /app -u 1000 -D app
WORKDIR /app

# Copy reqs and install first; means we cache result and don't rebuild on any other app change
#
# -- TODO: pipenv, not pip install as root
COPY app/requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt


COPY app /app
RUN chown -R 1000 /app



USER 1000


## CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
CMD [ "gunicorn", "-b", ":5000", "-w", "1", "wsgi:application" ]



FROM python:3

RUN apt-get update

RUN apt-get install git

ENV GYC_DATABASE=/githubYearCommits/database

RUN git clone https://github.com/strifel/githubYearCommits
# ADD . githubYearCommits <- I do not do this here, because of the other files (like database, venv and more) I have in this dir.

RUN pip install -r githubYearCommits/requirements.txt

RUN pip install gunicorn

EXPOSE 80

ENTRYPOINT [ "sh", "-c", "python githubYearCommits/install.py admin --continue-dev ; gunicorn  --chdir githubYearCommits -w 4 -b 0.0.0.0:80 app:app" ]

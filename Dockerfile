FROM python:3

ENV GYC_DATABASE=/githubYearCommits/database

ADD . githubYearCommits

RUN pip install -r githubYearCommits/requirements.txt

RUN pip install gunicorn

EXPOSE 80

ENTRYPOINT [ "sh", "-c", "python githubYearCommits/install.py admin --continue-dev ; gunicorn  --chdir githubYearCommits -w 4 -b 0.0.0.0:80 app:app" ]

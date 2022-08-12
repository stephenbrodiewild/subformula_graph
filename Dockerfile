FROM continuumio/miniconda3

WORKDIR /usr/src/app

COPY . ./
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt
CMD [ "python", "app.py" ]
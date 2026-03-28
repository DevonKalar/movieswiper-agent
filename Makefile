IMAGE     = ms-agent
CONTAINER = ms-agent

.PHONY: install test dev build run stop rebuild logs

install:
	poetry install

test:
	poetry run pytest

dev:
	flask --app wsgi run

build:
	docker build -t $(IMAGE) .

run:
	docker run -d --name $(CONTAINER) -p 8000:8000 --env-file .env $(IMAGE)

stop:
	docker stop $(CONTAINER) || true
	docker rm $(CONTAINER) || true

rebuild: stop build run

logs:
	docker logs -f $(CONTAINER)

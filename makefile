.PHONY: build

install:
	npm install
	pip install --upgrade pip setuptools wheel && pip install -r requirements-dev.txt && pip install -r requirements.txt
	pre-commit install

clean:
	rm -rf ./build

build:
	npm run build
	python manage.py collectstatic -l --noinput

watch:
	npm run watch

serve:
	python manage.py runserver 127.0.0.1:8000

fmt:
	pre-commit run -a

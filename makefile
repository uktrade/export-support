install:
	npm install
	pip install --upgrade pip setuptools wheel && pip install -r requirements.txt

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
	isort --line-width=90 --multi-line=3 --combine-as --trailing-comma .
	black export_support
	npm run fmt

deploy: clean
	npm run build
	cf target -o dit-staging -s export-support-dev
	cf push export-support-dev

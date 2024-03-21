

all: build

build:
	# @sudo mkdir ./postgres
	@docker compose up --build
	@docker compose exec django python manage.py migrate
	# @docker compose exec django python manage.py createsuperuser

run:
	@docker compose up

stop:
	@docker compose down

clean: stop
	@docker rmi -f $$(docker images -qa);
	@docker rm -f $$(docker ps -a -q);
	@docker volume rm -f $$(docker volume ls);

re: clean all

.PHONY: build run stop clean
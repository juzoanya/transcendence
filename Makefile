
all: build

build:
	@docker compose up -d --build

exec:
	@docker exec django python manage.py migrate

run:
	@docker compose up -d

stop:
	@docker compose down

restart: stop run

clean: stop
	@docker rmi -f $$(docker images -qa);
	@docker rm -f $$(docker ps -a -q);
	@docker volume rm $$(docker volume ls -q);

re: clean all

.PHONY: build run stop clean
# Default goal
.DEFAULT_GOAL := help

# Paths (relative)
FRONTEND_DIR := ./frontend
TEMPLATES_DIR := ./f1sim/templates

# Detect environment
ifeq ($(OS),Windows_NT)
    # Development (Windows)
    PYTHON := ..\venv\Scripts\python.exe
else
    # Production (Linux)
    VENV := ../venv/bin/activate
endif

# PHONY targets
.PHONY: help deploy frontend copy collect restart run-frontend run-backend

# Help (default)
help:
	@echo ""
	@echo "Available commands:"
	@echo ""
	@echo "  make deploy --------> Build frontend, copy files, collect static, restart services (PROD)"
	@echo "  make frontend ------> Install & build frontend (React)"
	@echo "  make copy ----------> Copy frontend build into Django templates"
	@echo "  make collect -------> Django collectstatic (PROD)"
	@echo "  make restart -------> Restart gunicorn + nginx (PROD)"
	@echo ""
	@echo "Development (Windows):"
	@echo "  make run-frontend --> Run React + SASS watcher"
	@echo "  make run-backend ---> Run Django dev server"
	@echo ""

# Production Deployment
deploy: frontend copy collect restart
	@echo "Production deployment completed"

frontend:
	cd $(FRONTEND_DIR) && npm install
	cd $(FRONTEND_DIR) && npm run build

copy:
	cp $(FRONTEND_DIR)/build/index.html $(TEMPLATES_DIR)/index.html

collect:
	. $(VENV) && python manage.py collectstatic --noinput

restart:
	sudo systemctl restart f1sim
	sudo systemctl restart nginx

# Development (Windows)
run-frontend:
ifeq ($(OS),Windows_NT)
	cd $(FRONTEND_DIR) && npx concurrently "npm start" "sass --watch src/css/styles.scss:src/css/styles.css"
else
	@echo "run-frontend target intended for Windows development environment."
endif

run-backend:
ifeq ($(OS),Windows_NT)
	$(PYTHON) manage.py makemigrations
	$(PYTHON) manage.py makemigrations backend
	$(PYTHON) manage.py migrate
	$(PYTHON) manage.py migrate backend
	$(PYTHON) manage.py runserver
else
	@echo "run-backend target intended for Windows development environment."
endif
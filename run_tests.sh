#!/bin/bash

flake8 .
isort --recursive --check-only .

coverage run -m unittest discover -p 'test*.py'
coverage html -d coverage/unittest
coverage run -m unittest discover -p 'integration_test*.py'
coverage html -d coverage/integration

#!/bin/bash

exec gunicorn --bind=0.0.0.0 --preload main:app

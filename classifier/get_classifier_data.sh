#!/usr/bin/env bash

[ -d "data" ] && echo "data folder already exists"
[ ! -d "data" ] && mkdir data && aws s3 sync --no-sign-request s3://bangladesh-flood-research/classifier/other_data/data ./data

[ -d "other_data" ] && echo "other_data folder already exists"
[ ! -d "other_data" ] && mkdir other_data && aws s3 sync --no-sign-request s3://bangladesh-flood-research/classifier/other_data/other_data ./other_data

[ -d "timeseries_data" ] && echo "timeseries_data folder already exists"
[ ! -d "timeseries_data" ] && mkdir timeseries_data && aws s3 sync --no-sign-request s3://bangladesh-flood-research/classifier/other_data/timeseries_data ./timeseries_data

ln -s ../article_scraping/all_papers.py ./
[ -d "../article_scraping/paper_data" ] && ln -s ../article_scraping/paper_data ./

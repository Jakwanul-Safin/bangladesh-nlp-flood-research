#!/usr/bin/env bash

[ -d "paper_data" ] && echo "paper_data folder already exists"
[ ! -d "paper_data" ] && mkdir paper_data && aws s3 sync --no-sign-request s3://bangladesh-flood-research/article_scraping/paper_data ./paper_data
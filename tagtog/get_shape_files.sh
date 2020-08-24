#!/usr/bin/env bash

[ -d "shammun_geography_dbf" ] && echo "shammun_geography_dbf already exists"
[ ! -d "shammun_geography_dbf" ] && mkdir shammun_geography_dbf && aws s3 sync --no-sign-request s3://bangladesh-flood-research/tagtog/shammun_geography_dbf ./shammun_geography_dbf
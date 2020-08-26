#!/usr/bin/env bash

[ -d "output" ] && echo "output folder already exists"
[ ! -d "output" ] && python tagtog_website.py download members_anncomplete:shammun OR anncomplete:true --user tvp2107 --project bangladesh_floods --owner ikhomyakov --output_folder output --member shammun
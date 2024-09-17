#!/bin/bash

cp database.db backups/temp_db.db
TIME=$(date +"%m-%d-%H")

mv backups/temp_db.db backups/db_$TIME.db
#!/bin/sh
set -e
mkdir -p /tmp/compiled
CP="/run/bahmni-lab/bahmni-lab/WEB-INF/classes:/run/bahmni-lab/bahmni-lab/WEB-INF/lib/*"
javac -cp "$CP" -d /tmp/compiled /tmp/java-custom/et/edu/uog/*.java
echo 'ET_COMPILED'
javac -cp "/tmp/compiled:$CP" -d /tmp/compiled /tmp/java-custom/us/mn/state/health/lims/test/action/*.java /tmp/java-custom/us/mn/state/health/lims/panel/action/*.java
echo 'ALL_COMPILED'

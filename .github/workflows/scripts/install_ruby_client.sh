#!/bin/bash

# WARNING: DO NOT EDIT!
#
# This file was generated by plugin_template, and is managed by it. Please use
# './plugin-template --github pulp_2to3_migration' to update this file.
#
# For more info visit https://github.com/pulp/plugin_template

set -euv

# make sure this script runs at the repo root
cd "$(dirname "$(realpath -e "$0")")"/../../..

export PULP_URL="${PULP_URL:-https://pulp}"

export REPORTED_VERSION=$(http $PULP_URL/pulp/api/v3/status/ | jq --arg plugin pulp_2to3_migration --arg legacy_plugin pulp_2to3_migration -r '.versions[] | select(.component == $plugin or .component == $legacy_plugin) | .version')
export DESCRIPTION="$(git describe --all --exact-match `git rev-parse HEAD`)"
if [[ $DESCRIPTION == 'tags/'$REPORTED_VERSION ]]; then
  export VERSION=${REPORTED_VERSION}
else
  export EPOCH="$(date +%s)"
  export VERSION=${REPORTED_VERSION}${EPOCH}
fi

export response=$(curl --write-out %{http_code} --silent --output /dev/null https://rubygems.org/gems/pulp_2to3_migration_client/versions/$VERSION)

if [ "$response" == "200" ];
then
  echo "pulp-2to3-migration client $VERSION has already been released. Installing from RubyGems.org."
  gem install pulp_2to3_migration_client -v $VERSION
  touch pulp_2to3_migration_client-$VERSION.gem
  tar cvf ruby-client.tar ./pulp_2to3_migration_client-$VERSION.gem
  exit
fi

cd ../pulp-openapi-generator
rm -rf pulp_2to3_migration-client
./generate.sh pulp_2to3_migration ruby $VERSION
cd pulp_2to3_migration-client
gem build pulp_2to3_migration_client
gem install --both ./pulp_2to3_migration_client-$VERSION.gem
tar cvf ../../pulp-2to3-migration/ruby-client.tar ./pulp_2to3_migration_client-$VERSION.gem

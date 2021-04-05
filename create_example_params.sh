#!/bin/bash

if [ -z "$1" ]; then
    >&2 echo "USAGE: build_or_deploy.sh [put|delete]"
    exit 1
fi

if [[ "$1" != "put" && "$1" != "delete" ]]; then
    >&2 echo "USAGE: build_or_deploy.sh [put|delete]"
    exit 1
fi

for NAME in \
  /apps/foo \
  /hosts/foo \
  /users/foo \
  /teams/myteam/accounts/github/username \
  /teams/myteam/accounts/github/password \
  /teams/myteam/accounts/github/email \
  /teams/myteam/accounts/github/pat/readonly \
  /teams/myteam/accounts/github/pat/all-permissions \
  /teams/myteam/accounts/trello/username \
  /teams/myteam/accounts/trello/password \
  /teams/myteam/accounts/trello/app-key \
  /teams/myteam/accounts/trello/token \
  /teams/myteam/accounts/slack/foo \
  /teams/myteam/accounts/sharepoint/foo \
  /teams/myteam/accounts/gmail/foo \
  /teams/myteam/accounts/pagerduty/foo \
  /teams/myteam/accounts/datadog/foo \
  /teams/myteam/accounts/newrelic/foo \
  /teams/myteam/accounts/gremlin/foo \
  /teams/myteam/accounts/statuspage/foo \
; do
  if [[ "$1" == "put" ]]; then
    aws ssm put-parameter --name "$NAME" --description "set by https://github.com/jantman/psread/blob/main/create_example_params.sh" --type SecureString --value "$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)"
  else
    aws ssm delete-parameter --name "$NAME"
  fi
done

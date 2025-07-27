#!/bin/bash
# git-credential-env.sh

# Read Git's request (protocol, host, etc.)
# Git sends these as key=value pairs on separate lines to stdin
while IFS='=' read -r key value; do
  case "$key" in
    protocol)
      protocol="$value"
      ;;
    host)
      host="$value"
      ;;
    # Add other fields if needed, like path, username, url
  esac
done < /dev/stdin

# Output the credentials
# For a GitHub Personal Access Token (PAT), 'x-oauth-basic' is a common dummy username.
# Adjust username if your API requires something specific.
echo "username=x-oauth-basic"
echo "password=$GITHUB_API_KEY"
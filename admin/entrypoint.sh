#!/bin/sh
set -e

# Sao chép SSH credentials từ thư mục mount sang /root/.ssh để owner/permission đúng.
if [ -d /host-ssh ]; then
  mkdir -p /root/.ssh
  cp -a /host-ssh/. /root/.ssh/
  chmod 700 /root/.ssh
  chown -R root:root /root/.ssh
  find /root/.ssh -type f -exec chmod 600 {} \;
fi

exec "$@"

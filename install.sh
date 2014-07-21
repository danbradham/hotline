#!/bin/bash

SRC="$HOME/Devel/HotLine/hotline"
DEST="$HOME/maya/2014-x64/scripts"

echo "Installing HotLine to $DEST..."

cp -ar $SRC $DEST

echo "Success!"

sleep 3

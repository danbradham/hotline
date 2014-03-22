#!/bin/bash

SRC="$HOME/Devel/HotLine/hotline"
DEST="$HOME/maya/2014-x64/scripts"

echo "Deploying HotLine"

if [ -d "$DEST/hotline" ]; then
    echo "Removing previous installation..."
    rm -rf "$DEST/hotline"
fi

echo "Copying HotLine to $DEST..."
cp -ar $SRC $DEST
echo "Success!"

sleep 3

#!/bin/bash

# Requires: apt-get install libmysqlclient-dev libffi-dev python-dev libjpeg-dev
CUR_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

LAST_COMMIT_HASH=`git rev-parse HEAD`

rm -Rf debian/usr/share/openalpr-gpsupdate

mkdir -p debian/usr/share/openalpr-gpsupdate/
mkdir -p debian/etc/init.d/



cp $CUR_DIR/openalprgps.py debian/usr/share/openalpr-gpsupdate/
cp $CUR_DIR/requirements.txt debian/usr/share/openalpr-gpsupdate/
cp $CUR_DIR/deploy/openalpr-gpsupdate debian/etc/init.d/

# Insert the git hash into settings.py
echo "$LAST_COMMIT_HASH" > debian/usr/share/openalpr-gpsupdate/githash

VERSION=`dpkg-parsechangelog -ldebian/DEBIAN/changelog --show-field Version`
VERSION_WITHOUT_BUILD=`echo $VERSION | sed 's/\-.*$//'`
#Swap in a build number based on the current date/time.
if [ -z "$BUILD_NUMBER" ]; then
    BUILD_NUMBER=`date "+%Y%m%d%H%M%S"`
fi
VER_WITH_BUILD="${VERSION_WITHOUT_BUILD}-${BUILD_NUMBER}"
sed -i "s/$VERSION/$VER_WITH_BUILD/" debian/DEBIAN/changelog
sed -i "s/^Version:.*/Version: $VER_WITH_BUILD/" debian/DEBIAN/control

fakeroot dpkg-deb --verbose --build debian || exit 1

DEB_FILE=openalpr-gpsupdate_${VER_WITH_BUILD}.deb

mkdir -p out/

mv debian.deb out/$DEB_FILE || exit 1



#!/bin/bash

# Run on an ubuntu/debian machine.

# Based on https://github.com/maltfield/cross-platform-python-gui/blob/af3aa35b671c7429c268ac09c7d4a80acf0ecbff/build/linux/buildAppImage.sh

# Upgrade system
sudo apt-get update
sudo apt-get upgrade -y

# Download python3.9 and dependencies
sudo apt-get install -y --no-install-recommends python3.9 python3-pip rsync fuse git

PYTHON_PATH=$(which python3.9)

mkdir ../build
cd ../build

# Setup a venv
$PYTHON_PATH -m venv venv
source ./venv/bin/activate

# Install nupack optional dependencies
pip install -U pip matplotlib jupyterlab

# Install nupack
git clone --depth 1 -b upstream/main https://github.com/genoswitch/NUPACK.git
pip install -U nupack -f NUPACK/src/package/

# Install kivy
pip install kivy[base]

wget https://github.com/niess/python-appimage/releases/download/python3.9/python3.9.18-cp39-cp39-manylinux2014_x86_64.AppImage
chmod +x ./python3.9.18-cp39-cp39-manylinux2014_x86_64.AppImage
./python3.9.18-cp39-cp39-manylinux2014_x86_64.AppImage --appimage-extract

# Copy installed dependencies from venv to kivy appdir
rsync -a ./venv/ ./squashfs-root/opt/python3.9/

# Add our code
rsync -a ../src ./squashfs-root/opt/

# change AppRun so it executes our app
mv ./squashfs-root/AppRun ./squashfs-root/AppRun.orig
cat > ./squashfs-root/AppRun <<'EOF'
#! /bin/bash

# Export APPRUN if running from an extracted image
self="$(readlink -f -- $0)"
here="${self%/*}"
APPDIR="${APPDIR:-${here}}"

# Export TCl/Tk
export TCL_LIBRARY="${APPDIR}/usr/share/tcltk/tcl8.5"
export TK_LIBRARY="${APPDIR}/usr/share/tcltk/tk8.5"
export TKPATH="${TK_LIBRARY}"

# Call the entry point
for opt in "$@"
do
    [ "${opt:0:1}" != "-" ] && break
    if [[ "${opt}" =~ "I" ]] || [[ "${opt}" =~ "E" ]]; then
        # Environment variables are disabled ($PYTHONHOME). Let's run in a safe
        # mode from the raw Python binary inside the AppImage
        "$APPDIR/usr/bin/python3.9 $APPDIR/opt/src/app.py" "$@"
        exit "$?"
    fi
done

# Get the executable name, i.e. the AppImage or the python binary if running from an
# extracted image
executable="${APPDIR}/usr/bin/python3.9 ${APPDIR}/opt/src/app.py"
if [[ "${ARGV0}" =~ "/" ]]; then
    executable="$(cd $(dirname ${ARGV0}) && pwd)/$(basename ${ARGV0})"
elif [[ "${ARGV0}" != "" ]]; then
    executable=$(which "${ARGV0}")
fi

# Wrap the call to Python in order to mimic a call from the source
# executable ($ARGV0), but potentially located outside of the Python
# install ($PYTHONHOME)
(PYTHONHOME="${APPDIR}/opt/python3.9" exec -a "${executable}" "$APPDIR/usr/bin/python3.9" "$APPDIR/opt/src/app.py" "$@")
exit "$?"
EOF

# make apprun executable
chmod +x ./squashfs-root/AppRun

# Section: build appImage

# Download AppImageTool
wget https://github.com/AppImage/AppImageKit/releases/download/13/appimagetool-x86_64.AppImage
chmod +x ./appimagetool-x86_64.AppImage

# artifact folder
mkdir dist
./appimagetool-x86_64.AppImage ./squashfs-root dist/genoswitch.AppImage


#!/usr/bin/env bash
set -e

echo "🚀 Starting Buildozer Android build..."

# Ensure Python & system dependencies
sudo apt-get update -y
sudo apt-get install -y \
  python3-pip python3-setuptools build-essential \
  git zip unzip openjdk-17-jdk wget \
  libffi-dev libssl-dev zlib1g libncurses6 libstdc++6 libsqlite3-dev libjpeg-dev

# Set up Android SDK environment
export ANDROID_HOME=$HOME/android-sdk
export PATH=$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH

mkdir -p $ANDROID_HOME
cd $ANDROID_HOME

if [ ! -d "cmdline-tools" ]; then
  echo "📦 Downloading Android commandline tools..."
  wget -q https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip -O cmdline-tools.zip
  unzip -q cmdline-tools.zip
  mkdir -p cmdline-tools/latest
  mv cmdline-tools/* cmdline-tools/latest/
fi

yes | sdkmanager --sdk_root=$ANDROID_HOME --licenses || true
yes | sdkmanager --sdk_root=$ANDROID_HOME \
  "platform-tools" \
  "platforms;android-34" \
  "build-tools;36.0.0" || true

# Return to project directory
cd $GITHUB_WORKSPACE

# Install Buildozer and Cython
pip install --upgrade pip
pip install buildozer cython

# Build APK
echo "🏗️ Building APK..."
buildozer -v android debug

# Check output
if [ -d "bin" ]; then
  echo "✅ APK built successfully. Files in bin/:"
  ls -lh bin/
else
  echo "❌ Build failed: No APK found in bin/"
  exit 1
fi

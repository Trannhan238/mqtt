@echo off

:: đồng bộ local = GitHub
git fetch origin
git reset --hard origin/main

echo PULL OK
echo
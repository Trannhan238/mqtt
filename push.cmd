@echo off

:: dọn lock nếu có
if exist .git\index.lock del .git\index.lock

:: add + commit
git add .
git commit -m "update %DATE% %TIME%"

:: ghi đè GitHub
git push -f origin main

if errorlevel 1 (
  echo PUSH FAILED
) else (
  echo PUSH OK
)
pause

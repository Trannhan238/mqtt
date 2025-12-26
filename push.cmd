cd /d D:\coding\Bell_production\mqtt
rmdir /s /q .git
git init
git add .
git commit -m "Reset repository"
git branch -M main
git remote add origin https://github.com/Trannhan238/mqtt.git
git push -f origin main

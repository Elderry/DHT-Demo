@echo off
d:
cd eclipse-SDK-3.7.2-win32-x86_64\eclipse\workspace\chord\src
start python chord.py -i ini
for /l %%a in (8001,1,8101) do (
	ping /n 60 127.0>nul
	start python chord.py -p %%a %%a
)
echo. & pause
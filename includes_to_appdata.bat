@echo off
IF NOT DEFINED INCLUDESDIR (echo "DO NOT RUN THIS FILE DIRECTLY" && PAUSE && EXIT)
IF NOT DEFINED APPDIR (EXIT)

:: dns needed for hardcoded dns updates only 
:: xcopy /Y /E "%INCLUDESDIR%\dns" "%APPDIR%\dns\"

xcopy /Y /E "%LOCALEDIR%" "%APPDIR%\locale\"
copy /Y "%INCLUDESDIR%\cacert_ovpn.pem" "%APPDIR%\"

echo copied includes to appdata '%APPDIR%'

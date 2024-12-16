@echo off
set name=Specter OBS Connector
title %name%
set name="%name%"
set ico=assets/icons/app-icon.ico
@echo on
pyinstaller -F -w --icon=%ico% --name=%name% main.py

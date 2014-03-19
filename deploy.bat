@echo off

SET DEST=%USERPROFILE%\Documents\maya\2014-x64\scripts\hotline
SET SRC=Z:\BNS_Pipeline\DEVELOPMENT\PROJECTS\HotLine\hotline
ECHO "Deploying HotLine to %DEST%"

XCOPY %SRC% %DEST%\* /E /Y

ECHO "SUCCESS!"

@echo on

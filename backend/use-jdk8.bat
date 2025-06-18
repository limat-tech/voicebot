@echo off
echo Setting environment for JDK 8...
set "JAVA_HOME=C:\Program Files\Zulu\zulu-8"
set "PATH=%JAVA_HOME%\bin;%PATH%"
echo JAVA_HOME is now set to:
echo %JAVA_HOME%
echo.
echo You can now start the MaryTTS server.

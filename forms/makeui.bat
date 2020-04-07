@echo off
call "C:\OSGeo4W64\bin\o4w_env.bat"
call "C:\OSGeo4W64\bin\qt5_env.bat"
call "C:\OSGeo4W64\bin\py3_env.bat"
rem pyrcc5 -o resources.py resources.qrc
rem pyuic5 -x %%i -o ui_%%~ni.py
@echo on
rem pyuic5 -o resources.py resources.qrc
for %%i in (*.ui) do (
	python -m PyQt5.uic.pyuic -x %%i -o %%~ni.py

)
pause 
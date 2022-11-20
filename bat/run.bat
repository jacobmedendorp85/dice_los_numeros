set PYTHONPATH=%PYTHONPATH%;../python
git pull
"C:\Program Files\Python311\python.exe" ../python/main.py
IF ERRORLEVEL 1 pause
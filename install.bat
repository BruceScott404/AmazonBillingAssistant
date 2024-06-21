@echo off
color 0a
title "Installer"

del input\.gitkeep
del output\.gitkeep

python3 --version
pip3 install pandas
pip3 install unidecode

pause
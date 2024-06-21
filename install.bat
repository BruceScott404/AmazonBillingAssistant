@echo off
color 0a
title "Installer"

del input\.gitkeep
del output\.gitkeep

pip3 install pandas
pip3 install unidecode

pause
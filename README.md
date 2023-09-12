# Fuzzer

## Description
An exploratory command line fuzz-testing tool made  used for finding weaknesses in a program by scanning its attack surface. Made as part of the SWEN-331 Class of Fall 2023 with Dr. Andy Meneely. 

## Installation
To get the environment ready:
1. Make sure you have ```python``` and ```dvwa``` (or any other web application) installed and running.
2. Clone the project using ssh ```git clone git@kgcoe-git.rit.edu:hm2310/fuzzer.git```.

## Usage
To run the discover command on DVWA or another web app, run the following commands in your terminal respectively:
- ```python3 fuzz.py discover http://localhost/ --custom-auth=dvwa```
- ```python3 fuzz.py discover http://127.0.0.1/fuzzer-tests```
You can replace ```http://localhost/``` or ```http://127.0.0.1/``` with whatever URL your web app is running. For example, in the windows portable, dvwa runs at ```http://localhost/dvwa/```.
<p>To test the code in the CI, commit and push to this repository using Git, and check your build in the Gitlab Project's "Pipelines" page for the output.</p>

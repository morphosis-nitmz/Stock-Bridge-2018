# Stock Bridge

A realtime Stock Market simulator.


## Instructions for setting up the project

1. Clone the repository  
`git clone https://github.com/morphosis-nitmz/Stock-Bridge`

2. Rename the file **.env-sample** to **.env** and replace the value of `SECRET_KEY` with the secret key of your own project. To generate a new secret key
	- Go to terminal and create a new django project `django-admin startproject <proj-name>`.
	- Now get the value of `SECRET_KEY` in *settings.py* and use that as the secret key for the **Stock-Bridge project**.
	- Now delete that new django project.

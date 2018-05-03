# Stock Bridge

Keeping in view the real thrill of the market monotony, we are here with the Virtual Simulation of the same thrill
and adrenaline rush through the event under the banner of **Morphosis, NIT Mizoram**. The virtual share market enables the participants
to trade, buy, sell mortgage and showcase their rationality, their mettle against competitive decision making under
pressure. The full time active virtual market will be a platform to showcase your inferential, pressure-handling
capability.


### Tools Used

- **Python** - Django, Django REST Framework
- **Javascript** - Chart.js
- **Bootstrap v4**


### Third Party Services Used

- **Amazon Web Services (AWS)**: Stores all static and media files.
- **Heroku**: Used to deploy the project in production environment.
- **sendgrid**: Used to send transactional emails like email-id verification, order completion etc.


## Instructions for setting up the project

1. Clone the repository  
`git clone https://github.com/morphosis-nitmz/Stock-Bridge`

2. Rename the file **.env-sample** to **.env** and replace the value of `SECRET_KEY` with the secret key of your own project. To generate a new secret key
	- Go to terminal and create a new django project `django-admin startproject <proj-name>`.
	- Now get the value of `SECRET_KEY` in *settings.py* and use that as the secret key for the **Stock-Bridge project**.
	- Now delete that new django project.

3. **Sendgrid setup**:
	- Create an account on [sendgrid](https://sendgrid.com/).
	- Add your sendgrid username and password to `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` in **.env** respectively.
	- Change the email and name in `DEFAULT_FROM_EMAIL` and `MANAGERS` in all *settings files* with your name and email.

4. **Amazon Web Services (AWS) setup**:  
	Follow this guide to setup AWS in the project: [AWS Setup](notes/aws_setup.md). After settings up AWS, add all the required values to **.env**

5. **Heroku setup**:  
	Follow this guide to setup Heroku in the project: [Heroku Setup](notes/heroku_setup.md).

6. Run the following commands  
`python manage.py makemigrations`  
`python manage.py migrate`  
`python manage.py collectstatic`

7. Now load the entries in **Company** model into the database  
`python manage.py loaddata market/fixtures/market.json`

<!-- PROJECT LOGO -->
<a name="readme-top"></a>
<br />
<div align="center">
  <a href="https://github.com/othneildrew/Best-README-Template">
    <img src="https://i.ibb.co/HnfJK9t/Collectiv-Logo.png" alt="Logo">
  </a>
  <p align="center">
     <b>Your Sanctuary for Community Events!</b>
    <br />
    <a href="https://collectiv-fe-display.vercel.app/"><strong>Check out the Web App »</strong></a>
  </p>
    <img src="https://github.com/The-Mud-Koalas/collectiv-fe-web/assets/70852167/f602728c-e2aa-4f46-8479-f7b4160f0b3c"></img>
  <br/>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-collectiv">About Collectiv</a>
      <ul>
        <li><a href="#the-problem">The Problem</a></li>
        <li><a href="#our-vision">Our Vision</a></li>
        <li><a href="#our-mission">Our Mission</a></li>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#environment-setup">Environment Setup</a></li>
      </ul>
    </li>
    <li><a href="#running-the-project">Running the project</a></li>
    <li><a href="#conventions">Conventions</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>


## About Collectiv
### The Problem:
Active engagement of community members to initiatives and/or ongoing projects is an essential component of a healthy communal space. However, there exists several obstacles that can hinder this, especially in a youth-dominated campus community. Lack of awareness of suitable opportunities to contribute is an important factor that discourages youth from participating in these events (Volunteering Queensland, 2021). Furthermore, inability to connect people affiliated to a common cause deprives the members of motivation to participate (Culp III & Schwartz, 1999). Therefore, it is necessary to motivate these members to  contribute more proactively to their communal space through informing members of any initiatives and/or projects and providing a medium for community members to connect with others sharing a common interest.

### Our Vision:

***Create a healthy community where everyone feels inspired to contribute, where diversity is celebrated, and where shared interests unite us in making every communal space a better place for all.***

### Our Mission:

***Cultivate an interactive and self-sustaining community around a specific shared communal space which is inclusive and allows people with diverse perspectives to contribute.***

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* [![Django]][Django-url]
* [![Postgres]][Postgres-url]
* [![Firebase][Firebase]][Firebase-url]
* [![Huggingface]][Huggingface-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started


### Prerequisites

You can choose to fork or clone this repository before you get started with development. The following demonstrates how to do the latter:
  ```
  git clone https://github.com/The-Mud-Koalas/collectiv-be
  ```
This will automatically create a `/collectiv-be` directory which contains the contents of this repository. You can then open that directory using the IDE of your choice i.e Visual Studio Code.

### Environment Setup

1. Once you have opened the project folder, open up a command prompt and setup a python virtual environment to isolate the dependencies. Venv and PyEnv are virtual environment managers that you can use. Here, we will be using pyenv
```
python -m pipenv shell
```
2. After a successful virtual environment setup, install all dependencies by using pip package manager as follows:
  ```
  python -r requirements.txt
  ```
4. The next step is to set up the environment variables. The application uses the following variable.
| Environment Variable             | Description                                                                                                                                                                                                                                                                                  |
|----------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| DATABASE_URL                     | URL to the database to persistently store application data. This project uses dj-database-url with database url format that can be seen here https://pypi.org/project/dj-database-url/ (for example postgres://postgres:postgres@localhost:5432/my_database)                                                                                                       |
| DJANGO_SECRET                    | The key used for cryptographic signing, value can be achieved here https://djecrety.ir/                                                                                                                                                                                                      |
| FIREBASE_ADMIN_CREDENTIAL_VALUES | The values of the firebase service account JSON file. This is used to provide configurations to the firebase authentication service used in the application. A documentation to setup your own firebase project can be seen here https://firebase.google.com/support/guides/service-accounts |
| GOOGLE_STORAGE_CREDENTIAL_VALUES | The values of the google storage application service account JSON file. A proper documentation to setup google bucket for python can be accessed here https://cloud.google.com/python/docs/reference/storage/latest.                                                                         |
| SERVER_EMAIL                     | The server that will be used to send the automated email, for example smtp.gmail.com.                                                                                                                                                                                                        |
| EMAIL_HOST                       | The server that will be used to send the automated email, for example smtp.gmail.com.                                                                                                                                                                                                        |
| EMAIL_PORT                       | Port to use for the SMTP server defined in EMAIL_HOST, for example 587 for smtp.gmail.com                                                                                                                                                                                                    |
| EMAIL_HOST_USER                  | Username to use for the SMTP server defined in EMAIL_HOST, i.e. the email address used to send the automated email.                                                                                                                                                                          |
| EMAIL_HOST_PASSWORD              | Password to use for the SMTP server defined in EMAIL_HOST, i.e. the password for the email address used to send the automated email.                                                                                                                                                         |
| DEFAULT_FROM_EMAIL               | Default email address to use for various automated correspondence from the site manager(s).                                                                                                                                                                                                  |
| SERVER_EMAIL                     | The email address that error messages come from, such as those sent to ADMINS and MANAGERS.                                                                                                                                                                                                  |
 Learn more about [Firebase Authentication](https://firebase.google.com/docs/auth/), [Django Email](https://docs.djangoproject.com/en/4.2/ref/settings/#std-setting-SERVER_EMAIL), and [Google Bucket](https://cloud.google.com/storage/docs)

6. The above environment variables need to be setup using an environment variable file. Create a `.env` file in the root directory of your project and set the following values:

   ```
   DATABASE_URL=XXXXXXXXXXXXXXXXXXXXXXXXXX
   DEFAULT_FROM_EMAIL=XXXXXXXXXXXXXXXXXXXXXXXXXX
   DJANGO_SECRET=XXXXXXXXXXXXXXXXXXXXXXXXXX
   DJANGO_SETTINGS_MODULE=XXXXXXXXXXXXXXXXXXXXXXXXXX
   EMAIL_HOST=XXXXXXXXXXXXXXXXXXXXXXXXXX
   EMAIL_HOST_PASSWORD=XXXXXXXXXXXXXXXXXXXXXXXXXX
   EMAIL_HOST_USER=XXXXXXXXXXXXXXXXXXXXXXXXXX
   EMAIL_PORT=XXXXXXXXXXXXXXXXXXXXXXXXXX
   ENVIRONMENT=XXXXXXXXXXXXXXXXXXXXXXXXXX
   SERVER_EMAIL=XXXXXXXXXXXXXXXXXXXXXXXXXX
   FIREBASE_ADMIN_CREDENTIAL_VALUES=XXXXXXXXXXXXXXXXXXXXXXXXXX
   GOOGLE_STORAGE_CREDENTIAL_VALUES=XXXXXXXXXXXXXXXXXXXXXXXXXX
   NEXT_PUBLIC_MAPS_API_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXX
    ```
    Learn more about [Firebase Authentication](https://firebase.google.com/docs/auth/) and how to get the [Google Maps API Key](https://developers.google.com/maps/documentation/javascript/get-api-key)
<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Running the project
If this is the first time running the application on a new local or remote database, you need to first perform database migration:
```
python manage.py migrate
```
Everytime a change is done to the structure of the application, perform makemigrations and migrate to implement the changes to the database. 
```
python manage.py makemigrations
python manage.py migrate
```

To run the application, run
```
python manage.py runserver
```
The application will now start on http://localhost:8000. You can open it in your browser.

<!-- CONTACT -->
### Contact

The Mud Koalas  - themudkoalas@gmail.com

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[Next.js]: https://img.shields.io/badge/next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white
[Next-url]: https://nextjs.org/
[React-query]: https://img.shields.io/badge/-React%20Query-FF4154?style=for-the-badge&logo=react%20query&logoColor=white
[React-query-url]: https://tanstack.com/query/v3/
[Django]: https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white
[Django-url]: https://www.djangoproject.com/
[Postgres]: https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white
[Postgres-url]: https://www.postgresql.org/
[Expo]: https://img.shields.io/badge/expo-1C1E24?style=for-the-badge&logo=expo&logoColor=#D04A37
[Expo-url]:https://expo.dev/
[React-native]: https://img.shields.io/badge/react_native-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB
[React-native-url]: https://reactnative.dev/
[React-hook-form]: https://img.shields.io/badge/React%20Hook%20Form-%23EC5990.svg?style=for-the-badge&logo=reacthookform&logoColor=white
[React-hook-form-url]: https://react-hook-form.com/
[Tailwind-css]: https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white
[Tailwind-css-url]: https://tailwindcss.com/
[Huggingface]: https://huggingface.co/datasets/huggingface/badges/resolve/main/powered-by-huggingface-light.svg
[Huggingface-url]: https://huggingface.co/
[Firebase]: https://img.shields.io/badge/Firebase-039BE5?style=for-the-badge&logo=Firebase&logoColor=white
[Firebase-url]: https://firebase.google.com/

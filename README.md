# Capstone Project  |   Koi Mods

> Capstone project for Springboard's Software Engineer Career Track

## Installation

- Install all packages listed in "requirements.txt"

```
pip install -r requirements.txt
```

- If everything is installed correctly, the homepage will appear as shown below

![Landing Screen](https://mod-page.s3-us-west-1.amazonaws.com/landing_page.png)

## API Used

- Amazon S3

## Features

- Users are able to register with a unique username
- Users are able to log in and out
- Registered and logged in users are able to upload their own mods with an image to accompany it
- Registered and logged in users are able to download mod files other users have posted.

## Under The Hood

- This project utilizes Amazon's S3 cloud storage for both images and archive files related to the mods
- The app relies heavily on Flask and Jinja in order to be dynamic and anticipate future features to be implemented
- When a file or image is uploaded a random number is generated and the name of the files/images are replaced in order to prevent mods or images with the same name from being overwritten

## User Flow

### Logging in/ Regstering

- When first landing on the page you will see the home screen which showcases mods from every supported game

- You are able to either explore the mods offered, or click on the "Games" link to select a game and view mods for your selection, but are not able to download without being a logged in user

- The option to login/register will be on the top left of the screen

- When you first select the login/register option you will be taken to a login screen

- There will be an option to register if you are not a current user. Clicking that will take you to the registration screen.

- The required information for registering is a unique username, your email address (must also be unique) and a password. The user profile image is optional, and if none is provided, a default is assigned.

### Downloading a Mod

- Once logged in you are able to download mods.

- Select the game you are wanting mods for. You will be taken to the main mods page.

- You can select from the available mods shown there.

- On the mod page, when you are logged in, there will be an download option. Selecting that will start the file download

### Uploading a mod

- To upload a mod you must be a registered user and logged in.

- Once logged in, there will be an option on the top right to upload

- Once selected you will be taken to a form page

- The required information to upload a mod is its title and the archive file the mod files are stored in.

  - All other fields are optional

  - If no mod image is provided a default is assigned

- Once the required fields are filled out and files selected, click "Upload"

- Once the upload has completed you will be taken to the page for your mod

### Important Notes

- At this time all planned features have not been implemented.

- To be implemented:

  - Mod update feature

  - User profile edit feature

  - Mod and user profile deletion

  - Mod search

- This project is proof of concept only. Please do not actually upload game mod information. The database is cleaned regularly and your data will not persist.

- All "Games" are fictional and creation of the author of this app. Any resemblence to real games or video game development companies is purely coincidential.

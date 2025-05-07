# BMTC-Visualisation
Using the BMTC API to visualise live bus routes on an LED board

## About this repository

This repository will be used to track all the scripts, instructions, and my overall process to create an LED board to visualise live BMTC bus routes.

I'm using the publicly accessible BMTC API, that I am currently in the process of reverse-engineering and documenting. You can check that out at [this](https://github.com/PratyushBalaji/BMTC-API) GitHub repository.

The final project will be an LED matrix with an LED controller and a processor (Likely a Raspberry Pi) which uses the internet to host a webserver where it will recieve instructions from the client, and make API calls to fetch relevant information, which it will then process to display on the LED matrix.

My goal is to make this project as open and accessible as possible so that others can integrate it with their own hardware, or even modify to make work with other transit systems worldwide!

## Requirements
- `requests` - To handle POST requests to the BMTC API
- `matplotlib` - To visualise on the LED grid

This list will be updated as and when I add more features.

Requirements are available in [requirements.txt](requirements.txt). You can install them directly using `pip3 install -r requirements.txt`
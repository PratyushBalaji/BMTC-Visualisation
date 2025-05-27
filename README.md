# BMTC-Visualisation
Using the BMTC API to visualise live bus routes on an LED board

## About this repository

This repository will be used to track all the scripts, instructions, and my overall process to create an LED board to visualise live BMTC bus routes.

I'm using the publicly accessible BMTC API, that I am currently in the process of reverse-engineering and documenting. You can check that out at [this](https://github.com/PratyushBalaji/BMTC-API) GitHub repository.

The final project will be an LED matrix with an LED controller and a processor (Likely a Raspberry Pi) which uses the internet to host a webserver where it will recieve instructions from the client, and make API calls to fetch relevant information, which it will then process to display on the LED matrix.

My goal is to make this project as open and accessible as possible so that others can integrate it with their own hardware, or even modify to make work with other transit systems worldwide!

## Disclaimer

This project is intended **strictly** for **educational and informational purposes**. The data and API usage demonstrated here are meant solely to help understand how BMTC services function and retrieve data. Any use of this information in personal or public applications may place unintended load on BMTC servers and disrupt official services.

**I do not accept any responsibility or liability for consequences arising from the misuse of this data or API. Use at your own discretion and respect the intended limits of the service.**

## Requirements
- `requests` - To handle POST requests to the BMTC API
- `matplotlib` - To visualise on the LED grid

This list will be updated as and when I add more features.

Requirements are available in [requirements.txt](requirements.txt). You can install them directly using `pip3 install -r requirements.txt`

## How to use

Currently, the python program is just a test to view how the GPS coordinates of stops and buses will be normalised on differently sized LED grids. It follows a basic user input flow and outputs a map. Regardless, here's how you can use it.

1. Run the file with `python3 LEDvis.py`
2. Enter the bus route you want to visualise ("exit" to exit)
   - This can even be partial text, as this step performs a search query
3. Select one of the options from the list (0 to search again)
4. View your matplotlib plot. Blue for stops, and red for buses
5. Close the matplotlib plot and repeat steps 2-5 to view more

Example flow : 

```
$ ls
LEDvis.py  README.md  requirements.txt
$ python3 LEDvis.py
Enter bus route (or type 'exit'): 
```
`> MF-23E`
```
Matching routes:
1. MF-23E
2. MF-23E D45-JHMS
3. MF-23E MSP-LGR
0. Search again
```
```
Select a route number:
```
`> 1`
```
Fetching route map for: MF-23E
```
![Map for MF-23E](https://github.com/user-attachments/assets/5583760d-0d34-4331-b432-d529b050cfca)
```
Enter bus route (or type 'exit'):
```
`> KIA-6`
```
Matching routes:
1. KIA-6
2. KIA-6A
3. KIA-6W
0. Search again
```
```
Select a route number:
```
`> 2`
```
Fetching route map for: KIA-6A
```
![Map for KIA-6A](https://github.com/user-attachments/assets/308c9c00-0aaf-426b-92a5-9ebf7cece339)
```
Enter bus route (or type 'exit'):
```
`> abcdefghijkl`
```
No Records Found.

Enter bus route (or type 'exit'):
```
`> MF-23E`
```
Matching routes:
1. MF-23E
2. MF-23E D45-JHMS
3. MF-23E MSP-LGR
0. Search again
```
```
Select a route number:
```
`> 5`
```
Invalid selection. Try again.
```
```
Enter bus route (or type 'exit'):
```
`> exit`
```
Goodbye!
```

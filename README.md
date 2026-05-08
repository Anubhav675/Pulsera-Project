Pulsera Heart Rate Monitoring Device 
Raspberry Pi Pico-Heart Rate Sensor
Pulsera is a micropython based heart rate and heart rate variability monitoring system running on a Raspberry Pi Pico W with a 128 X 64 pixel OLED display. It also supports Kubios cloud for advance HRV analysis.
Features:
1) Real-time heart rate monitor
2) HRV (RMSSD and SDNN) analysis locally as well as using Kubios cloud for advance analysis including SNS and PNS
3) Live PPG drawing on the OLED screen
4) Save the history locally on the pico
5) Wifi connection on the system for Kubios analysis and saving patient record in Kubios database
6) Adaptive peak algorithm

Running the Project:
1) Install micropython on the Pico W
2) Copy all the project files (including the libraries) to the Pico
3) change the wifi credentials in config.py 
4) if you are running kubios on a pi then also change the IP and port of the broker in config.py
5) Optional - You can change the name of the patient as well in config.py
6) Check the GPIO pins Oled pins ADC pins if it is as per the connection to your Pico
7) Run main.py
8) If you want to run standalone just unplug and plug the pico 


Project Architecture:
a) main.py --> Main application
b) comms.py --> Wifi + MQTT+ Kubios communication (both Kubios analysis and storing in the database)
c) config.py --> constant variables 
d) display.py --> OLED display rendering 
e) hardware.py --> Hardware initializing and IRQ handling 
f) menu.py --> Rotary encoder menu logic
g) my_icon.py --> Pulsera logo
h) processing.py --> Hear rate, RMSSD, SDNN, mean PPI processing algorithm
i) sampling.py --> ADC sampling using Piotimer
j) storage.py --> Local history creating logic

Hardwares:
a) Raspberry Pi Pico W
b) OLED Display (128x64 pixel) 
c) Crowtail Pulse sensor
d) Rotary encoder with push button
e) LED
f) Raspberry Pi with Kubios Proxy. MQTT communication between Pico and Pi for advance Kubios analysis and using kubios database.

Software:
a) Programming language --> Micropython
b) All the libraries in this project are to be copied too.

Heart Beat Measurement Algorithm used:
SMA filtering to smooth the raw data fed
Adaptive threshold creation
Rising Edge Pulse Detection

Menu Options/ Modes:
a) Measure HR:
- Live BPM monitoring 
- Real- time PPG waveform display

b) Basic HRV:
- 30 seconds of measurement
- Displays: BPM, RMSSD, mean ppi, SDNN

c) Kubios:
- sends ppi interval to the kubios and returns:
 a) Mean HR
 b) RMSSD
 c) SDNN
 d) SNS 
 e) PNS

 d) History:
 - Stores latest 5 measurements
 - Browse the history of measuurements on the screen

 Controls:
 Rotate encoder to select different options
 Press the encoder button to select the option and also to back to main menu from any other modes.( in history there is 'back' option which is to be pressed to back to main menu)

 Storage:
 Data are stored in history.json file locally






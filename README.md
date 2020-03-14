# d74_display
A script to connect to a Kenwood TH-D74 over USB and remotely display data on a 16x2 LCD

See http://kd8rtt.com/2020/03/08/remote-display-over-usb-for-kenwood-th-d74 for more details on the hardware used and operation of the program


d74_memory.hmk - This is my .hmk memory channel file from the Kenwood TH-D74A/E Memory Control Program MCP-D74. It is basically a csv file that the script uses to match a memory channel number (which it receives over the USB serial connection) to the memory channel name (which is not available over the USB serial connection). You are welcome to use it or just review it for background, but unless you have your memory frequencies programmed the same way with the same names, it won't match your programming.

d74_display.py - This is the script that runs the program to communicate with the TH-D74 over a USB serial connection and displays the frequency, mode, memory channel, date, and time on the 16x2 LCD display.

This work builds upon the commands found in https://github.com/LA3QMA/TH-D74-Kenwood

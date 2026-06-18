flashmain:
	exec sudo ./pyboard.py --device /dev/ttyACM0 -f cp ./ST7735.py :
	exec sudo ./pyboard.py --device /dev/ttyACM0 -f cp ./main.py :main.py
sendmain:
	exec sudo ./pyboard.py --device /dev/ttyACM0 main.py --follow
sendblink:
	exec sudo ./pyboard.py --device /dev/ttyACM0 blink.py
record:
	exec sudo ./pyboard.py --device /dev/ttyACM0 record.py --follow
import serial

port = serial.Serial("COM4", 115200)  # address for serial port is COM4 in this example. Change to match your machine.

def TestTriggerCode(generated, surprisal, position):
    if generated:
        cond = "2"
    else:
        cond = "1"
    if not surprisal:
        surp = "0"
    else:
        if surprisal == (True, True):
            surp = "1"
        elif surprisal == (False, False):
            surp = "2"
        elif surprisal == (False, True):
            surp = "3"
        elif surprisal == (True, False):
            surp = "4"
    pos = str(position)

    code = cond + surp + pos
    return(int(code))

print(TestTriggerCode(True, (False, True), 7))

def trigger(code, port):
    port.write(code.to_bytes(1, 'big'))
    print('trigger sent {}'.format(code))


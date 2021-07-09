import time
from socket import *
import datetime as dt

from DSP import Processor, SIGNAL_T, Filters


if __name__ == '__main__':
    processor = Processor()
    overflow_cnt = SIGNAL_T * Filters.FS * 2
    temp_buffer = b""

    server_socket = socket(AF_INET, SOCK_DGRAM)
    server_socket.bind(('', 12000))

    # last_sample_time = dt.datetime.now()

    try:
        while True:
            message, _ = server_socket.recvfrom(2048)
            if message.startswith(b"\x00" * 4):
                buff = message
                while not buff.endswith(b"\x11" * 4):
                    message, _ = server_socket.recvfrom(2048)
                    buff += message
                buff = buff[4:-4]
                # now = dt.datetime.now()
                # print(">> %s: %d samples with sequence number %d after %s " % (
                #     str(now.time()), len(buff) / 2, int(buff[-1] + buff[-2]), str((now - last_sample_time))))
                # last_sample_time = now

                temp_buffer += buff[:-2]
                if len(temp_buffer) >= overflow_cnt:
                    processor.new_data(temp_buffer[:overflow_cnt])
                    temp_buffer = temp_buffer[overflow_cnt:]
    except KeyboardInterrupt:
        pass

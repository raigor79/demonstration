import struct
#import numpy as np
#import matplotlib.pyplot as plt
#import matplotlib
import os
import argparse
import logging
import re
import math


class Par_Data():
    def __init__(self, file_name):
        self.par = {}
        self.data = []
        with open(file_name + '.par', mode='br') as f:
            self.code_str = f.read(20).decode('ascii')
            self.par['CodeString'] = self.code_str
            self.dev_name = f.read(17).decode('ascii')
            self.par['DeviceName'] = self.dev_name
            self.time_str = f.read(26).decode('ascii')
            self.par['TimeString'] = self.time_str
            self.chans_max = int.from_bytes(f.read(2), byteorder='little', signed=False)
            self.par['ChannelsMax'] = self.chans_max
            self.real_chan = int.from_bytes(f.read(2), byteorder='little', signed=False)
            self.par['RealChannelsQuantity'] = self.real_chan
            self.real_kadr = int.from_bytes(f.read(8 if self.code_str[16:17] == 'A' else 4), byteorder='little', signed=False)
            self.par['RealKadrsQuantity'] = self.real_kadr
            self.real_samp = int.from_bytes(f.read(8 if self.code_str[16:17] == 'A' else 4), byteorder='little', signed=False)
            self.par['RealSamplesQuantity'] = self.real_samp
            _tt = f.read(10 if self.code_str[16:17] == 'A' else 8)
            self.adc_rate = struct.unpack('<d', f.read(8 if self.code_str[16:17] == 'A' else 4))[0]
            self.par['AdcRate'] = self.adc_rate
            self.in_kadr_delay = struct.unpack('<d',f.read(8 if self.code_str[16:17] == 'A' else 4))[0]
            self.can_rate = struct.unpack('<d', f.read(8 if self.code_str[16:17] == 'A' else 4))[0]
            self.total_time = self.real_kadr/(self.adc_rate*1000)
            self.par['TotalTime'] = self.total_time
        with open(file_name + '.dat', mode='br') as f:
            try:
                while True:
                    data1 = f.read(2*self.real_chan)
                    if  not data1:
                        break
                    self.data.append(int.from_bytes(data1[0:2], byteorder='little', signed=True))
            except StopIteration:
                pass


parser = argparse.ArgumentParser(description="Demonstration")
parser.add_argument(
    '--range',
    type=int,
    default=5,
    help="Range integ"
)
parser.add_argument(
    '--dir',
    type=str,
    default='./data'
)
parser.add_argument(
    '--save',
    type=bool,
    default=False
)


def find_start(mas):
    start_val = sum(mas[0:10])/10
    for ti, tval in enumerate(mas):
        if tval < (start_val)*0.6:
            return ti


def main(opt):
    list_file_dir = os.listdir(os.path.join(opt.dir))
    for file_ in list_file_dir:
        atr_file = os.path.splitext(file_)
        if  atr_file[1] == '.par':
            c = Par_Data(os.path.join(opt.dir, atr_file[0]))
            pos_start = find_start(c.data)
            fon = sum(c.data[0:pos_start-100])/(pos_start-100)
            sum_int = 0
            item = 0
            pred_val = 0.00001
            for val in c.data[pos_start+2000:pos_start+10000]:
                sum_int += (math.log(fon/val) + math.log(fon/pred_val))/2/(c.adc_rate*1000)
                pred_val = val
                item += 1
            print(file_, '\t', str(sum_int/(item)*1000).ljust(20))

if __name__ == "__main__":
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.INFO, 
        format='[%(asctime)s] %(levelname).1s %(message)s', 
        datefmt='[%H:%M:%S]'
    )
    log = logging.getLogger()
    log.info('Start')
    main(args)
    log.info('Stop')


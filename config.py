import src.data_type

conf = src.data_type.AttribDict()

# setting serial port, default None
conf.serial_device = 'COM4'

# setting baudrate, default 9600
conf.serial_baudrate = 9600

# setting timeout, default 60
conf.serial_timeout = 60
class Manager():

    def __init__(self, control, serial):
        self._control = control
        self._serial = serial

        self.register(serial)
        self.register(control)


    def recv_serial(self, stream):
        """
        recv from serial, then notice to connections
        """
        self.send_control(stream)

    def send_serial(self, stream):
        """
        send to serial port, if recv from connections
        """
        self._serial.write_stream(stream)

    def recv_control(self, stream):
        """
        recv from connections, then notice to serial port
        """
        self.send_serial(stream)

    def send_control(self, stream):
        """
        send to connections, if recv from serial port
        """
        self._control.send(stream)

    def register(self, klass):
        """
        need register SerialPort and Control in Manager
        """
        klass.manager = self

    def add_connection(self, conn):
        """
        append a connection in Controlor
        """
        self._control.append(conn)
    
    def thread_start(self):
        self._serial.thread_run()


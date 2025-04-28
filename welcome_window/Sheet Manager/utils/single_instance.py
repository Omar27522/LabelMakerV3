import socket
import logging

class SingleInstanceApp:
    """Ensures only one instance of the application is running."""
    def __init__(self, port=23456, app_name="SheetsManager"):
        self.port = port
        self.app_name = app_name
        self.sock = None
        self.mutex_name = f'Global\\{app_name}SingleInstance'
        self.is_first_instance = self._check_instance()

    def _check_instance(self):
        try:
            import win32event
            import win32api
            import winerror
            self.mutex = win32event.CreateMutex(None, False, self.mutex_name)
            last_error = win32api.GetLastError()
            if last_error == winerror.ERROR_ALREADY_EXISTS:
                logging.info("Another instance is already running (detected by mutex)")
                return False
            logging.info("First instance of application started (mutex created)")
            return True
        except Exception as e:
            logging.error(f"Error using mutex approach: {e}")
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.sock.bind(('localhost', self.port))
                self.sock.listen(5)
                logging.info("First instance of application started (socket bound)")
                return True
            except socket.error as e:
                logging.info(f"Another instance is already running (socket in use): {e}")
                return False

    def set_app(self, app):
        self.app = app
        logging.info("App reference set in SingleInstanceApp")

    def cleanup(self):
        try:
            if hasattr(self, 'sock') and self.sock:
                try:
                    self.sock.close()
                    self.sock = None
                    logging.info("Socket closed during cleanup")
                except Exception as e:
                    logging.error(f"Error closing socket: {e}")
            if hasattr(self, 'mutex'):
                try:
                    import win32api
                    win32api.CloseHandle(self.mutex)
                except Exception as e:
                    logging.error(f"Error releasing mutex: {e}")
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")

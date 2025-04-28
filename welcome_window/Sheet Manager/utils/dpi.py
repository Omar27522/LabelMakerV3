import ctypes

def set_dpi_awareness():
    """Set process DPI awareness for high-DPI displays (Windows only)."""
    try:
        awareness = ctypes.c_int(2)  # PROCESS_PER_MONITOR_DPI_AWARE
        ctypes.windll.shcore.SetProcessDpiAwareness(awareness)
    except AttributeError:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception as e:
        print(f"Failed to set DPI awareness: {e}")

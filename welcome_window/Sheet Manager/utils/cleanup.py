import os
import logging

def cleanup():
    """Cleanup temporary files and resources before application exit."""
    logging.info("Application shutting down")
    try:
        temp_dir = os.path.join(os.environ.get('TEMP', os.getcwd()), 'sheetsmanager_temp')
        if os.path.exists(temp_dir):
            for file in os.listdir(temp_dir):
                try:
                    os.remove(os.path.join(temp_dir, file))
                except Exception:
                    pass
    except Exception as e:
        logging.error(f"Error during cleanup: {str(e)}")

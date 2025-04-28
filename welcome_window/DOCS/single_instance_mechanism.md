# Single Instance Mechanism Documentation

## Overview

The Label Maker application implements a single-instance mechanism to prevent multiple instances of the application from running simultaneously. This feature improves user experience by preventing confusion and potential performance issues that could arise from running multiple copies of the application.

## Implementation

The single-instance mechanism uses a combination of Windows mutex as the primary detection method with socket binding as a fallback approach. This dual approach ensures reliable detection across different Windows environments.

### Key Features

1. **Reliable Detection**: Uses Windows mutex as the primary method with socket binding as fallback
2. **Clear User Feedback**: Shows a warning message when a user tries to open a second instance
3. **Resource Management**: Properly cleans up resources when the application closes
4. **Performance Protection**: Prevents performance issues from multiple application instances running simultaneously

## Technical Implementation

The single-instance mechanism is implemented in the application's entry point:

```python
class SingleInstanceApp:
    def __init__(self, app_name="LabelMakerApp"):
        self.app_name = app_name
        self.mutex = None
        self.socket = None
        
    def is_already_running(self):
        """Check if another instance is already running using mutex and socket"""
        # Try Windows mutex first (primary method)
        try:
            import win32event
            import win32api
            import winerror
            
            self.mutex = win32event.CreateMutex(None, False, self.app_name)
            if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
                return True
        except ImportError:
            # Fall back to socket method if win32 modules are not available
            pass
            
        # Fallback: Try socket binding
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind(('localhost', 12345))  # Use a specific port for the app
            return False
        except socket.error:
            # Socket is already in use, another instance is running
            return True
            
        return False
        
    def cleanup(self):
        """Clean up resources when the application closes"""
        if self.socket:
            self.socket.close()
```

## Usage

The single-instance mechanism is used in the main application entry point:

```python
if __name__ == "__main__":
    single_instance = SingleInstanceApp()
    
    if single_instance.is_already_running():
        messagebox.showinfo("Label Maker", "Label Maker is already running")
        sys.exit(0)
    
    try:
        app = WelcomeWindow()
        app.protocol("WM_DELETE_WINDOW", lambda: (single_instance.cleanup(), app.destroy()))
        app.mainloop()
    finally:
        single_instance.cleanup()
```

## User Experience

When a user attempts to start a second instance of the Label Maker application:

1. The single-instance mechanism detects that an instance is already running
2. A clear message dialog appears: "Label Maker is already running"
3. The second instance exits gracefully
4. The user can continue working with the existing instance

## Design Considerations

The implementation prioritizes:

1. **Reliability**: Using multiple detection methods ensures consistent behavior
2. **Simplicity**: The solution is straightforward and easy to maintain
3. **User Experience**: Clear messaging helps users understand what's happening
4. **Resource Management**: Proper cleanup prevents resource leaks

## Benefits

The single-instance mechanism provides several benefits:

1. **Prevents Confusion**: Users won't be confused by multiple application windows
2. **Reduces Resource Usage**: Prevents unnecessary duplication of resources
3. **Avoids Data Conflicts**: Prevents potential conflicts from multiple instances accessing the same files
4. **Improves Performance**: Ensures optimal performance by preventing resource contention

## Conclusion

The single-instance mechanism is a simple but effective solution that improves the overall user experience of the Label Maker application. By preventing multiple instances from running simultaneously, it ensures consistent behavior and optimal performance.

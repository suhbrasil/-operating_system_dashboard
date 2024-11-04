# Linux System Dashboard

This project is a dashboard for monitoring and visualizing system information on a Linux operating system. It provides insights into file systems, directory structures, and resources allocated by processes.

## Features

### 1. File System Monitoring
- Displays current information about the file system, including partitions, memory usage (total, used, free), and usage percentage.
- Information is retrieved through functions in `model.py`, specifically by accessing the `/proc` directory.

### 2. Directory Structure Navigation
- Shows a navigable directory tree starting from the root (`/`) with a depth limit of 3 (adjustable if needed).
- Displays file details such as size, permissions, and last modified date.
- Information is dynamically fetched and displayed in `view.py` using recursive functions from `model.py`.

### 3. Resource Usage by Processes
- Visualizes open files, semaphores/mutexes, and sockets for a selected process.
- Provides detailed socket information by accessing network files in `/proc/{pid}/net/`.
- Data is displayed in a popup for each selected process.

## Architecture

The project is divided into the following components:

- **`controller.py`**: Manages data flow between the model and view, coordinating updates to the dashboard.
- **`model.py`**: Handles data retrieval and processing from system files, such as `/proc/partitions` and process-specific directories.
- **`view.py`**: Renders the data in a graphical interface, creating tables and popups for different dashboard sections.

## Dependencies

The project relies on the following libraries (listed in `requirements.txt`):
- `customtkinter==5.2.2`
- `matplotlib==3.8.4`
- `pandas==2.2.2`
- `Pillow==8.4.0`

Install dependencies with:
```bash
pip install -r requirements.txt

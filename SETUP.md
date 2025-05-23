# GeoSight DPR Generator Setup

## Environment Variables

To use the Google Maps integration for project area definition and visualization, you need to provide a Google Maps API key.

1.  **Obtain a Google Maps API Key:**
    *   Go to the [Google Cloud Console](https://console.cloud.google.com/).
    *   Create a new project or select an existing one.
    *   Enable the "Maps JavaScript API" and potentially "Geocoding API" and "Places API" for full functionality.
    *   Create an API key under "Credentials".
    *   **Important:** Secure your API key by restricting its usage to your specific domains or IP addresses.

2.  **Set the Environment Variable:**
    *   You need to set the `GOOGLE_MAPS_API_KEY` environment variable to the key you obtained.
    *   How you set environment variables depends on your operating system and development environment:
        *   **Linux/macOS (Terminal):**
            ```bash
            export GOOGLE_MAPS_API_KEY="YOUR_API_KEY_HERE"
            ```
            To make it permanent, add this line to your shell's configuration file (e.g., `~/.bashrc`, `~/.zshrc`).
        *   **Windows (Command Prompt):**
            ```cmd
            set GOOGLE_MAPS_API_KEY=YOUR_API_KEY_HERE
            ```
        *   **Windows (PowerShell):**
            ```powershell
            $env:GOOGLE_MAPS_API_KEY="YOUR_API_KEY_HERE"
            ```
        *   **Replit (Secrets):**
            If you are using Replit, you can store the API key as a secret.
            1.  Go to the "Secrets" tab in the left sidebar.
            2.  Add a new secret with the key `GOOGLE_MAPS_API_KEY` and your API key as the value.
            The application will automatically pick it up from there.
        *   **Other Hosting/IDE:** Consult the documentation for your specific hosting provider or IDE on how to set environment variables.

**Note:** The application will still run if the API key is not provided, but the map functionalities will be disabled or may not work correctly.

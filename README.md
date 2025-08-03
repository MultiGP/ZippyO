# Software Setup Instructions


## Introduction

----------------------------------------------------------------------------


**To install the ZippyO server:**

1. If the computer does not already have Python installed, download and install Python from https://www.python.org/downloads . The minimum version of Python needed for ZippyO is 3.8. To check if Python is installed and the version, open up a command prompt and enter ```python --version```

2. From the ZippyO [Releases page on github](https://github.com/ZippyO/ZippyO/releases), download the "Source code (zip)" file.

3. Unzip the downloaded file into a directory (aka folder) on the computer.

4. Open up a command prompt and navigate to the topmost ZippyO directory.

5. Create a Python virtual environment ('venv') by entering: ```python -m venv --system-site-packages .venv```

6. Activate the Python virtual environment ('venv'):

  * On a Windows system the command to use will likely be: ```.venv\Scripts\activate.bat```

  * On a Linux system the command to use will likely be: ```source .venv/bin/activate```

7. Using the same command prompt, navigate to the ```src/server``` directory in the ZippyO files (using the 'cd' command).

8. Install the ZippyO server dependencies using the 'requirements.txt' file, using one of the commands below. (Note that this command may require administrator access to the computer, and the command may take a few minutes to finish).

  * On a Windows system the command to use will likely be:<br/>```python -m pip install -r requirements.txt```<br>

Note: If the above command fails with a message like "error: Microsoft Visual C++ 14.0 is required", the "Desktop development with C++" Tools may be downloaded (from [here](https://aka.ms/vs/17/release/vs_BuildTools.exe)) and installed to satisfy the requirement.<br>

  * On a Linux system the command to use will likely be:<br/>```pip install -r requirements.txt```


**To run the ZippyO server on these systems:**

1. Open up a command prompt and navigate to the topmost ZippyO directory.

2. Activate the Python virtual environment ('venv')
  * On a Windows system the command to use will likely be: ```.venv\Scripts\activate.bat```

  * On a Linux system the command to use will likely be: ```source .venv/bin/activate```

3. Using the same command prompt, navigate to the ```src/server``` directory.

4. Enter: ```python server.py```

5. If the server starts up properly, you should see various log messages, including one like this:
    ```
    Running http server at port 5000
    ```

1. The server may be stopped by hitting Ctrl-C

<a id="logging"></a>
## Logging

The ZippyO server generates "log" messages containing information about its operations. Below is a sample configuration for logging:

```
    "LOGGING": {
        "CONSOLE_LEVEL": "INFO",
        "SYSLOG_LEVEL": "NONE",
        "FILELOG_LEVEL": "INFO",
        "FILELOG_NUM_KEEP": 30,
        "CONSOLE_STREAM": "stdout"
    }
```
The following log levels may be specified:  DEBUG, INFO, WARNING, WARN, ERROR, FATAL, CRITICAL, NONE

If the FILELOG_LEVEL value is not NONE then the server will generate log files in the `src/server/logs` directory. A new log file is created each time the server starts, with each file having a unique name based on the current date and time (i.e., "rh_20200621_181239.log"). Setting FILELOG_LEVEL to DEBUG will result in more detailed log messages being stored in the log file, which can be useful when debugging problems.

The FILELOG_NUM_KEEP value is the number of log files to keep; the rest will be deleted (oldest first).

The CONSOLE_STREAM value may be "stdout" or "stderr".

If the SYSLOG_LEVEL value is not NONE then the server will send log messages to the logging utility built into the host operating system.

<br/>

----------------------------------------------------------------------------

### Update existing installation of ZippyO
If you have ZippyO already installed and just want to refresh its code
```
cd ~/ZippyO
git pull origin main
```
 

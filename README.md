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
4.  Update src/server/config.json FILE_PATH to point to json location that livetime will be sending to

4. Enter: ```python server.py```

5. If the server starts up properly, you should see various log messages, including one like this:
    ```
    Running http server at port 5001
    ```

1. The server may be stopped by hitting Ctrl-C

**Usage:**
URL: http://<hostname>:5001
/      : shows all of the livetime json attributes
/nextup    : Page modifies on purple flag to show the race before it starts. Shows the pilots in the race
/inprogress    :Page modifes on green flag, shows running order of pilots, and behind next
/results       :Page shows the race finish order
(more to come)

Example:
```
http://127.0.0.1:5001/
```

**Development**
Example: 
```
 <body>
<div class="container-fluid">
<div name="Race_FlagColor"></div>
<h2>Next Up</h2>
<span style="display: flex;">Driver 1:&nbsp; <div name="Drivers_0_FirstName"></div>&nbsp;<div name="Drivers_0_LastName"></div><img name="Drivers_0_DriverLID" width="50" height="50" templatesrc="./static/image/imageREPLACEME.png" ></img></span>
<span style="display: flex;">Driver 2:&nbsp; <div name="Drivers_1_FirstName"></div>&nbsp;<div name="Drivers_1_LastName"></div><img name="Drivers_1_DriverLID" width="50" height="50" templatesrc="./static/image/imageREPLACEME.png" ></img></span>
<span style="display: flex;">Driver 3:&nbsp; <div name="Drivers_2_FirstName"></div>&nbsp;<div name="Drivers_2_LastName"></div><img name="Drivers_2_DriverLID" width="50" height="50" templatesrc="./static/image/imageREPLACEME.png" ></img></span>
<span style="display: flex;">Driver 4:&nbsp; <div name="Drivers_3_FirstName"></div>&nbsp;<div name="Drivers_3_LastName"></div><img name="Drivers_3_DriverLID" width="50" height="50" templatesrc="./static/image/imageREPLACEME.png" ></img></span>

</div>
</body>
```

Some examples above: elements like Drivers_0_FirstName are keys found in the livetime.json file.  these <div> elements with that name will display the values of those keys.

In the case of <img> the value of the Key will be dynamically substitued into the "REPLACEME" portion of the url for the image locations.. 

It is also possible to access the json data when the HTML is being rendered, though typical python templating in your html file.
However, be aware this will only be evaluated as the html page is being generated/loaded, and not dynamically while the pae is open
```
{{ data.Race.FlagColor }}
```

To only do dynamic updates for certain Flags, (Purple, Green, Checkered). add this to the top of your html
```
<script>
const dynamicUpdate="Green Flag";
</script>
```

----------------------------------------------------------------------------

### Update existing installation of ZippyO
If you have ZippyO already installed and just want to refresh its code
```
cd ~/ZippyO
git pull origin main
```
 

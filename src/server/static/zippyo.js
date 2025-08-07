
        get_version = undefined;
        get_timestamp = undefined;
        get_settings = undefined;
        reset = undefined;
        object_count = undefined;

        $(document).ready(function() {
            var buzzer = $('#buzzer')[0];

            var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

            var start_timestamp = [];

            function append_to_log(text) {
                $('#log').prepend('<br>' + $('<div/>').text(text).html());
            }

function traverseJson(obj, parentKey = '') {
  for (const [key, value] of Object.entries(obj)) {
    const currentPath = parentKey ? `${parentKey}_${key}` : key;

    if (typeof value === 'object' && value !== null) {
      if (Array.isArray(value)) {
        //console.log(`Array found at: ${currentPath}`);
        value.forEach((item, index) => {
          if (typeof item === 'object' && item !== null) {
            traverseJson(item, `${currentPath}_${index}`);
          } 
        });
      } else {
        traverseJson(value, currentPath); // Recursive call for nested objects
      }
    } else {
        thisitem = document.getElementsByName(currentPath); 
        compvalue=(value !== null)?value:"null";
        if (thisitem != null){
            for (let i = 0; i < thisitem.length; i++) {
               const element = thisitem[i];
               if ( element.curval != compvalue){
                  element.curval = value;
                  if (element.tagName == "IMG"){
                    templatesrc = element.getAttribute("templatesrc");
                    finalsrc = templatesrc.replaceAll("REPLACEME",value);
                    element.removeAttribute("src");
                    element.src = finalsrc;
                    element.curval = value;
                  }else{ 
                     element.innerText = value;
                  }
               }
            }
        }
    }
  }
}

            function set_bigjson(text) {
                //$('#bigjson').text(text);
                const jsonObject = JSON.parse(text);
                if (typeof dynamicUpdate === 'undefined' || jsonObject.Race.FlagColor == dynamicUpdate){
                   if (object_count !== undefined && object_count != jsonObject.Drivers.length) {
                      document.location.reload();
                   }
                   object_count = jsonObject.Drivers.length;
                   traverseJson(jsonObject);
                }
            }

            socket.on('connect', function() {
                append_to_log('connected!');
            });

            socket.on('heartbeat', function(msg) {
                if (document.readyState === "complete"){
                   set_bigjson(JSON.stringify(msg));
                }
            });


            function ms_to_time(s) {
              // Pad to 2 or 3 digits, default is 2
              function pad(n, z) {
                z = z || 2;
                return ('00' + n).slice(-z);
              }

              var ms = s % 1000;
              s = (s - ms) / 1000;
              var secs = s % 60;
              s = (s - secs) / 60;
              var mins = s % 60;

              return pad(mins) + ':' + pad(secs) + '.' + pad(ms, 3);
            }

		});

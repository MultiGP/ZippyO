
        $(document).ready(function() {
            var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
            socket.on('bracket_change', function(msg) {
                console.log("hello");
                if (document.readyState === "complete"){
                      document.location.reload();
                }
            });

	});

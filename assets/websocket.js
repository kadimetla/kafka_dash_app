document.addEventListener("DOMContentLoaded", function() {
    function connectWebSocket() {
        var socket = io.connect('http://' + document.domain + ':' + location.port, {
            transports: ['websocket'],
            upgrade: false
        });

        socket.on("connect", () => {
            console.log("Connected with socket ID: " + socket.id);
        });

        socket.on("disconnect", (reason) => {
            console.log("Disconnected: " + reason);
            if (reason === "ping timeout" || reason === "transport close" || reason === "transport error") {
                console.log("Attempting to reconnect...");
                setTimeout(connectWebSocket, 1000);  // Try to reconnect after 1 second
            }
        });

        socket.on('update', function(msg) {
            console.log('Data received: ', msg);

            // Update the pie chart directly
            var chartElement = document.getElementById('pie-chart').querySelector('.js-plotly-plot');
            const data = [{
                values: msg.Values,
                labels: msg.Category,
                type: 'pie'
            }];
            Plotly.react(chartElement, data);
        });
    }

    connectWebSocket();
});

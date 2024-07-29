import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from kafka import KafkaConsumer
import json
import threading

# Initialize Flask server and Dash app
server = Flask(__name__)
app = dash.Dash(__name__, server=server)
socketio = SocketIO(server, ping_interval=25, ping_timeout=60)

# Initial data for the pie chart
initial_data = {'Category': ['A', 'B', 'C'], 'Values': [10, 20, 30]}
df = pd.DataFrame(initial_data)

# Create a pie chart figure
def create_pie_chart(df):
    fig = px.pie(df, names='Category', values='Values')
    return fig

# Kafka consumer function
def consume_kafka_data():
    consumer = KafkaConsumer('dash_topic', bootstrap_servers='localhost:9092', value_deserializer=lambda m: json.loads(m.decode('utf-8')))
    for message in consumer:
        print("consumer print ",message)
        data = message.value
        socketio.emit('update', data)

# Start Kafka consumer in a separate thread
thread = threading.Thread(target=consume_kafka_data)
thread.daemon = True
thread.start()

# Flask route to update data manually (for testing)
@server.route('/update-data', methods=['POST'])
def update_data():
    global df
    data = request.json
    if data:
        df = pd.DataFrame(data)
        socketio.emit('update', data)
        return jsonify({"status": "success", "data": data})
    else:
        return jsonify({"status": "failure", "message": "No data received"}), 400

@socketio.on('connect')
def handle_connect():
    print('Client connected: ' + request.sid)
    # Emit current data to newly connected client
    socketio.emit('update', df.to_dict(orient='list'), room=request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected: ' + request.sid)

# Define the custom index_string with all required placeholders
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        <title>Dash App</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <script src="https://cdn.socket.io/4.4.1/socket.io.min.js"></script>
    </head>
    <body>
        <div id="react-entry-point">
            <!-- This is where Dash will mount -->
            {%app_entry%}
        </div>
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
            <script src="/assets/websocket.js"></script>
        </footer>
    </body>
</html>
'''

# Dash layout
app.layout = html.Div([
    dcc.Graph(id='pie-chart', figure=create_pie_chart(df)),
    html.Div(id='data-output', style={'display': 'none'})
])

# No Dash callback needed for updating the pie chart since it will be handled by WebSocket

if __name__ == "__main__":
    socketio.run(server, debug=True)


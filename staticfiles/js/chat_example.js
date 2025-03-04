const socket = new WebSocket('ws://localhost:8000/ws/chat/myroom/');
socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log(data.message);
};
socket.send(JSON.stringify({ 'message': 'Hello, world!' }));
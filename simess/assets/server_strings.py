prompt_str = "#> {0}"

client_status_str = ["Disconnected", "Connected"]

server_events_str = {
    "Server Event Print": "[ Event: {0}\n  Nickname: {1}\n  IP: {2} Port: {3}\n  Timestamp: {4} ]\n",
    "Server Event Share": "#> [ {0} ({1}:{2}) {3} ({4})]",
    "Server Shutting Down": "[ Shutting Down... ]"
}

server_error_str = {
    "Unknown Command": "[ Unknown Command ]\n"
}

client_message_broadcast_str = "{0} <{1} ({2})"

server_success_reply_str = {
    "Sent": "[ Sent ]"
}

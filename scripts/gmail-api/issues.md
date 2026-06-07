# Implemented
The Gmail API script now detects stored tokens that do not include every required scope and starts a fresh OAuth flow instead of refreshing an incompatible token.
The Gmail API auto reply script now has a systemd service and timer that runs every 5 minutes.

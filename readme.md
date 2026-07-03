# Real-Time Asynchronous Chat Architecture

A real-time messaging backend engineered with **Django** and **WebSockets**. This architecture utilizes **Django Channels** to handle asynchronous ASGI connections, a memory-based message broker for low-latency broadcasting, and a relational database for persistent chat log auditing.

## Architecture & Core Tech Stack
* **Framework:** Django / Python
* **Asynchronous Protocol:** WebSockets (Django Channels / Daphne ASGI)
* **Database:** SQLite / Relational DB Layer
* **Frontend:** Vanilla JavaScript, HTML5 WebSockets API

## Key Features Implemented

* **Full-Duplex Real-Time Communication:** Bypasses traditional HTTP request/response cycles by maintaining persistent WebSocket connections for zero-latency message broadcasting.
* **Asynchronous Database Persistence:** Utilizes Django Channels' `database_sync_to_async` decorators to perform non-blocking database writes during live broadcasting, preventing thread starvation.
* **State Hydration & History Retrieval:** Automatically fetches and serves the last 50 historical messages from the relational database the millisecond a new client connects, ensuring seamless state continuity.
* **Sessionless Identity Management:** Implemented lightweight JSON payload tagging to track user display names across the broadcast groups without requiring heavy session middleware.

## System Flow Lifecycle
1.  **Handshake:** Client initiates a WebSocket connection to the Daphne ASGI server via `ws://<host>/ws/chat/<room_name>/`.
2.  **Hydration:** `consumers.py` accepts the connection, queries the database asynchronously, and pushes historical chat state to the client.
3.  **Broadcast:** Incoming JSON payloads are parsed and instantly broadcasted to all active clients in the channel group.
4.  **Audit Logging:** Message metadata (username, content, timestamp) is serialized and persisted to the underlying relational database.

## Local Execution Instructions

### Prerequisites
* Python 3.10+

### Setup & Launch
Clone the repository:
```bash
git clone [https://github.com/yourusername/realtime-chat-server.git](https://github.com/yourusername/realtime-chat-server.git)
cd realtime-chat-server

1.Activate a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # (Or `venv\Scripts\activate` on Windows)
pip install -r requirements.txt
```
2.Run database migrations to construct the schema:
```bash
python manage.py makemigrations chat
python manage.py migrate
```
3.Start the ASGI Daphne server:
```bash
python manage.py runserver
```
4.Open the included index.html file in multiple web browser windows to test the real-time broadcasting and database persistence.
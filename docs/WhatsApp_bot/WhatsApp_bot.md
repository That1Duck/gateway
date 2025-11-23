# WhatsApp bot application for backend

This document provides the plan and stages of implementation.

---
# 1. Technology Stack

* **Meta WhatsApp Cloud API**

Layout for application:
```
gateway/app/
    whatsapp_bot/
        webhook.py # FastApi routers for bot
        engine.py  # text handler
        client.py  # Meta API client for sending messages
        config.py  # Configuration of variables
```

---
# 2. Stages 

1. * Additional environment variables have been created. 
   * The bot framework has been created. 
   * A router and two main endpoints have been created.
   * A router has been added to the main backend.
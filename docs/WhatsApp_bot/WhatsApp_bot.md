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
---
2. * New table for whatsapp user data `models\whatsapp_user`
   * Service searching for user in db by phone number or creating new one `services\whatsapp_user`
   * Rewrote `handle_incoming_text` in `engines` and added `router_user_message` as a menu manager.  
---
3. * Extended:
     * `models\whatsapp_user`
     * Service `services\whatsapp_user`
     * Menu in `engines`. Functionality implementation required.
---
4. * Extended `engine.py`
---
5. * Supplemented and corrected `engine.py`
---
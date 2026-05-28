## IdentitySvc Follow-up (Not Implemented Here)

These steps must be applied in `LanguageApp-IdentitySvc` during cutover to `LanguageApp-EnglishSvc`.

1. Register a new service key:
   - `service_name`: `english-service`
   - Roles:
     - `english-user`
     - `admin`
2. Assign `english-user` (and `admin` where needed) to users who currently have access to:
   - `phrasalverbs-service`
   - `prepositions-service`
   - `chat-practice-service`
3. Deploy IdentitySvc updates.
4. Force re-authentication so users receive JWTs including `roles["english-service"]`.
5. After EnglishSvc is fully live and verified, remove obsolete role mappings:
   - service keys: `phrasalverbs-service`, `prepositions-service`, `chat-practice-service`
   - roles: `phrasalverbs-user`, `prepositions-user`, `chat-practice-user`
   - legacy per-service admin role assignments

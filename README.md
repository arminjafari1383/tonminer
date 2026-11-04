# TON Miner — Django + React + TON Connect

Converted from the provided single-file `TON Miner (2).html`. The original CSS, palette and embedded mining rig artwork are retained in `frontend/src/original.css`. The original HTML used localStorage and a fake completed payment; this project creates a real order, requests TON transfer via TON Connect, and **only confirms deposits after an on-chain lookup**.

## Run locally

1. `cd backend && python -m venv .venv && source .venv/bin/activate` (Windows: `.venv\Scripts\activate`)
2. `pip install -r requirements.txt`
3. `cp .env.example .env` and set `TON_RECEIVER` to your own **mainnet** TON address (EQ... / UQ...), `DJANGO_SECRET_KEY` to a real random secret, and ideally `TONCENTER_API_KEY`.
4. `python manage.py migrate --run-syncdb` then `python manage.py runserver`.
5. In a second terminal: `cd frontend && npm install && cp .env.example .env && npm run dev`.
6. Set `frontend/.env` `VITE_PUBLIC_URL` to your public HTTPS frontend URL and edit `frontend/public/tonconnect-manifest.json` to the same HTTPS domain and icon URL. Host it on a publicly accessible HTTPS domain: mobile wallets require a reachable manifest. For local tests use an HTTPS tunnel and update CORS accordingly.
7. Open your Vite URL; choose a wallet, select a plan, pay, then click **بررسی پرداخت**. Confirmation can take time; a transaction-request response alone is **not** a verified payment.

## How payments work

POST `/api/payments/` with `{"wallet":"UQ...","amount":"20"}` => order ID, unique `TONMINER-...` memo, receiver, nanoTON-derived amount.
The frontend sends a TON Connect mainnet transfer with a standard text comment payload (32-bit zero opcode followed by UTF-8 memo).
GET `/api/payments/<uuid>/` checks Toncenter v2 inbound transactions, matching **exact memo, amount and source wallet**, records transaction hash exactly once, and returns pending/confirmed/expired. An expired order can still have a valid late transaction; manual reconciliation is necessary. The account and amount are never verified based solely on client claims.

## Production limitations / security

- **Do not deploy as a finished mining/investment product.** Mining graphics, power and return tiers are illustrative only. No real mining engines, accrued earnings, guaranteed ROI, referral payouts or withdrawals exist.
- Current order URLs act as unguessable bearer IDs (no user login). Implement TON proof (wallet ownership verification), authenticated accounts, permissions, abuse controls, server-side ledger, background indexing, reconciliation and fraud monitoring before production.
- V2 `getTransactions` scans only the latest 100 inbound transactions; busy wallets need a proper indexed payment processor or per-order address and reconciliation. Use a dedicated receiving wallet and a reliable TON indexer for production.
- The confirmation checker assumes Toncenter's `message` is the decoded incoming text comment. Validate against your chosen indexer's transaction schema and network before going live.
- Protect outgoing wallet keys offline / in a secure signer. **Never put your seed phrase in React or Django source.** This project performs no outbound transfers.
- SQLite and `run-syncdb` are development conveniences. Use proper Django migrations, PostgreSQL, HTTPS, reverse proxy, rate limiting and monitoring in production.
- Use small test payments on a configured testnet deployment first (this sample explicitly supports mainnet only; network selection and API host must be adapted for testnet).

## Run with Docker Compose

Requirements: Docker Engine and the Docker Compose plugin.

1. From the project root, create the backend environment file:

   ```bash
   cp backend/.env.example backend/.env
   ```

2. Edit `backend/.env` and set at least:
   - `DJANGO_SECRET_KEY` to a long random secret.
   - `TON_RECEIVER` to the receiving TON wallet address.
   - `ALLOWED_HOSTS` to the domain name (and `localhost` for local testing).
   - `TONCENTER_API_KEY` if you have one.

3. Update `frontend/public/tonconnect-manifest.json` so its `url` and `iconUrl` use your publicly reachable HTTPS domain. TON wallets need to access this manifest.
4. Start the stack from the project root:

   ```bash
   docker compose up --build -d
   ```

5. Open `http://localhost:9000` (or the port configured by `FRONTEND_PORT`). Django migrations run automatically when the backend container starts. API requests are reverse-proxied by Nginx to Django. Django is also directly exposed at `http://localhost:10000` (configurable using `BACKEND_PORT`). The frontend remains configured to call `/api` through Nginx.

Useful commands:

```bash
docker compose logs -f
docker compose ps
docker compose down
# Keep database volume when stopping. To delete it too (DESTROYS stored data):
# docker compose down -v
```

The SQLite database is persisted in the `django_data` Docker volume. For production, put the app behind HTTPS, configure a real domain in `ALLOWED_HOSTS`, use a production database such as PostgreSQL, and review the security limitations above. Do not expose the development server or use the example secret in production.


## Automatic payment verification and receipts (updated)

- No manual verification button: while the app is open it polls pending order IDs every 5 seconds and refreshes balance every 15 seconds. This does **not** replace a server-side scheduled reconciliation worker when users close the app.
- Payment creation returns only a pending request, **not an invoice**. A final receipt appears after an on-chain match.
- CreditLedger stores one credit per confirmed payment in SQLite; balance comes from the backend `/api/balance/?wallet=...`, not browser localStorage.
- Existing confirmed payments gain a ledger entry when their status endpoint is requested. Existing pending payments are checked when their owner reopens the app with the same browser data.
- For production use wallet authentication, background settlement/reconciliation, pagination/indexing, tested transaction decoding, database migrations, and rate limiting.

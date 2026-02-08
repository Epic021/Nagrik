# NAGRIK WhatsApp Bot

WhatsApp bot that integrates with the NAGRIK backend API using Baileys.

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env if needed (default points to localhost:8000)
   ```

3. **Start the bot:**
   ```bash
   npm start
   ```

4. **Scan QR code** with WhatsApp to connect

## Usage

- Send **START** to begin a complaint session
- Send **STOP** to end the session
- Send text or images to register complaints

## API Endpoints

The bot calls these NAGRIK API endpoints:
- `POST /api/v1/whatsapp/chat` - Process messages
- `POST /api/v1/whatsapp/clear` - Clear session
- `GET /api/v1/whatsapp/health` - Health check

## Requirements

- Node.js 18+
- NAGRIK backend running on port 8000

import {
    makeWASocket,
    DisconnectReason,
    useMultiFileAuthState,
    fetchLatestBaileysVersion,
    Browsers,
    downloadMediaMessage
} from '@whiskeysockets/baileys'
import qrcode from 'qrcode-terminal'
import axios from 'axios'
import 'dotenv/config'

// API URL - points to FastAPI backend
const API_URL = process.env.NAGRIK_API_URL || 'http://localhost:8000/api/v1/whatsapp'

// Track active sessions and processed messages
const activeSessions = new Set()
const processedMessages = new Set()

const getMessage = (key) => {
    return undefined
}

let sock = null

async function connectWhatsApp() {
    const { state, saveCreds } = await useMultiFileAuthState('auth')
    const { version, isLatest } = await fetchLatestBaileysVersion()
    console.log(`using WA v${version.join('.')}, isLatest: ${isLatest}`)

    sock = makeWASocket({
        version,
        auth: state,
        browser: Browsers.ubuntu('Chrome'),
        syncFullHistory: false,
        getMessage,
        logger: {
            level: 'silent',
            trace: () => { },
            debug: () => { },
            info: () => { },
            warn: () => { },
            error: () => { },
            fatal: () => { },
            child: () => ({ trace: () => { }, debug: () => { }, info: () => { }, warn: () => { }, error: () => { }, fatal: () => { } })
        }
    })

    sock.ev.on('creds.update', saveCreds)

    sock.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect, qr } = update

        if (qr) {
            console.log('\n[QR] QR code received, scan it with your phone:\n')
            qrcode.generate(qr, { small: true })
        }

        if (connection === 'close') {
            const statusCode = lastDisconnect?.error?.output?.statusCode
            const shouldReconnect = statusCode !== DisconnectReason.loggedOut

            if (statusCode === 440) {
                console.log('[WARN] Session conflict. Waiting 5s...')
                setTimeout(() => connectWhatsApp(), 5000)
            } else if (shouldReconnect) {
                connectWhatsApp()
            } else {
                console.log('[INFO] Logged out.')
            }
        } else if (connection === 'open') {
            console.log('[OK] Bot ready! Send "START" to begin, "STOP" to end.')
        }
    })

    sock.ev.on('messages.upsert', async (upsert) => {
        if (upsert.type !== 'notify') return

        for (const msg of upsert.messages) {
            // Skip self messages
            if (msg.key.fromMe) continue

            // Deduplication - skip if already processed
            const msgId = msg.key.id
            if (processedMessages.has(msgId)) continue
            processedMessages.add(msgId)

            // Clean up old message IDs (keep last 100)
            if (processedMessages.size > 100) {
                const arr = Array.from(processedMessages)
                processedMessages.clear()
                arr.slice(-50).forEach(id => processedMessages.add(id))
            }

            await handleMessage(msg)
        }
    })
}

async function handleMessage(msg) {
    const userId = msg.key.remoteJid
    const text = getMessageContent(msg.message)?.trim().toUpperCase()

    console.log(`[MSG] ${userId}: "${text || '[media]'}"`)

    // Handle START command
    if (text === 'START') {
        activeSessions.add(userId)
        console.log(`[SESSION] Session started for ${userId}`)
        await sendReply(userId, '*NAGRIK Complaint Registration Bot*\n\nHello! I am here to help you register your complaint.\n\nPlease describe your issue. You can also send images if needed.\n\nType *STOP* anytime to end the conversation.')
        return
    }

    // Handle STOP command
    if (text === 'STOP') {
        if (activeSessions.has(userId)) {
            activeSessions.delete(userId)
            // Clear API session
            try {
                await axios.post(`${API_URL}/clear`, { user_id: userId })
            } catch (e) { }
            console.log(`[SESSION] Session ended for ${userId}`)
            await sendReply(userId, 'Thank you for using NAGRIK. Your session has ended.\n\nType *START* to begin a new complaint.')
        }
        return
    }

    // Only process if session is active
    if (!activeSessions.has(userId)) {
        // Ignore messages when not in session
        return
    }

    // Process message with API
    try {
        const messageText = getMessageContent(msg.message) || ''
        let imageBase64 = null

        // Check for image
        if (msg.message?.imageMessage) {
            console.log('[MEDIA] Downloading image...')
            const buffer = await downloadMediaMessage(msg, 'buffer', {})
            imageBase64 = buffer.toString('base64')
        }

        // Send to NAGRIK API
        console.log('[API] Sending to NAGRIK API...')
        const response = await axios.post(`${API_URL}/chat`, {
            user_id: userId,
            message: messageText,
            image: imageBase64
        }, { timeout: 30000 })

        if (response.data.success) {
            await sendReply(userId, response.data.response)
            console.log('[OK] Reply sent')
        } else {
            await sendReply(userId, '[ERROR] Sorry, I encountered an error. Please try again.')
        }

    } catch (error) {
        console.error('[ERROR] API error:', error.message)
        await sendReply(userId, '[ERROR] Service temporarily unavailable. Please try again later.')
    }
}

async function sendReply(jid, text) {
    try {
        await sock.sendMessage(jid, { text })
    } catch (e) {
        console.error('[FAIL] Failed to send:', e.message)
    }
}

function getMessageContent(message) {
    if (!message) return ''
    return (
        message.conversation ||
        message.extendedTextMessage?.text ||
        message.imageMessage?.caption ||
        ''
    )
}

console.log('[START] Starting NAGRIK WhatsApp Bot...')
console.log(`[CONFIG] API URL: ${API_URL}`)
connectWhatsApp()

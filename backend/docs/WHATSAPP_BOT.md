# WhatsApp Bot (Baileys) Integration Guide

## Overview

The NAGRIK backend is fully compatible with Baileys WhatsApp bots. This guide shows how your Baileys bot should interact with the API.

---

## Architecture

```
WhatsApp User
     ↓
[Baileys Bot] ←→ [NAGRIK API]
     ↓              ↓
  Media →     MongoDB Atlas
```

The Baileys bot acts as a **client** to the NAGRIK API, same as the mobile/web frontend.

---

## Required Endpoints for WhatsApp Bot

### 1. User Registration/Login

WhatsApp users are identified by phone number. Auto-register on first message.

```javascript
// Check if user exists, create if not
async function getOrCreateUser(phoneNumber, name) {
  try {
    // Try to login first
    const login = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        phone: phoneNumber.replace(/\D/g, '').slice(-10),  // Extract 10 digits
        password: generatePasswordFromPhone(phoneNumber)    // Derive password from phone
      })
    });
    
    if (login.ok) {
      return await login.json();  // { access_token: "..." }
    }
    
    // User doesn't exist, register
    const register = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: name || 'WhatsApp User',
        phone: phoneNumber.replace(/\D/g, '').slice(-10),
        password: generatePasswordFromPhone(phoneNumber)
      })
    });
    
    // Then login
    return await getOrCreateUser(phoneNumber, name);
  } catch (e) {
    console.error('Auth error:', e);
    return null;
  }
}
```

---

### 2. Submit Complaint from WhatsApp

```javascript
async function submitComplaint(token, { text, mediaUrl, location }) {
  // Step 1: If has image, upload and classify
  let category_id = null;
  let uploadedUrl = null;
  
  if (mediaUrl) {
    // Upload image to GCS
    const formData = new FormData();
    formData.append('file', await downloadMedia(mediaUrl));
    
    const upload = await fetch(`${API_URL}/files/upload`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: formData
    });
    uploadedUrl = (await upload.json()).url;
    
    // Classify from image
    const classify = await fetch(`${API_URL}/classify/from-image`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image_url: uploadedUrl, description: text })
    });
    const classification = await classify.json();
    category_id = classification.category_id;
  } else {
    // Classify from text
    const classify = await fetch(`${API_URL}/classify/from-text`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: text.slice(0, 100), description: text })
    });
    const classification = await classify.json();
    category_id = classification.category_id;
  }
  
  // Step 2: Submit complaint
  const complaint = await fetch(`${API_URL}/complaints`, {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      title: text.slice(0, 100),
      description: text,
      category_id: category_id || 'other',  // Fallback if classification failed
      location: location || { lat: 28.6139, lng: 77.2090 },  // Default: Delhi center
      media_urls: uploadedUrl ? [uploadedUrl] : [],
      urgency: 'medium'
    })
  });
  
  return await complaint.json();
}
```

---

### 3. Handle WhatsApp Location Share

```javascript
// When user shares location
async function handleLocation(msg) {
  if (msg.message.locationMessage) {
    const { degreesLatitude, degreesLongitude } = msg.message.locationMessage;
    
    // Validate it's in Delhi
    const validate = await fetch(
      `${API_URL}/geo/validate?lat=${degreesLatitude}&lng=${degreesLongitude}`
    );
    const result = await validate.json();
    
    if (!result.is_valid_delhi_location) {
      return "Sorry, we currently only support complaints in Delhi NCR.";
    }
    
    // Get address
    const reverse = await fetch(
      `${API_URL}/geo/reverse?lat=${degreesLatitude}&lng=${degreesLongitude}`
    );
    const address = await reverse.json();
    
    return {
      lat: degreesLatitude,
      lng: degreesLongitude,
      address: address.address
    };
  }
}
```

---

### 4. Conversational Flow

```javascript
const userStates = new Map();  // Track conversation state

async function handleMessage(msg) {
  const phone = msg.key.remoteJid.split('@')[0];
  const text = msg.message?.conversation || msg.message?.extendedTextMessage?.text || '';
  const state = userStates.get(phone) || { step: 'idle' };
  
  switch (state.step) {
    case 'idle':
      if (text.toLowerCase().includes('complaint') || text.toLowerCase().includes('problem')) {
        userStates.set(phone, { step: 'awaiting_description' });
        return "Please describe your complaint. You can also send a photo.";
      }
      if (text.toLowerCase().includes('status')) {
        return await getMyComplaints(phone);
      }
      return "Welcome to NAGRIK! Reply with 'complaint' to report an issue or 'status' to check your complaints.";
    
    case 'awaiting_description':
      state.description = text;
      state.step = 'awaiting_location';
      userStates.set(phone, state);
      return "Please share your location (tap 📎 → Location) or type the address.";
    
    case 'awaiting_location':
      // Handle location or address text
      const location = await handleLocation(msg) || await geocodeAddress(text);
      state.location = location;
      
      // Submit complaint
      const token = await getOrCreateUser(phone);
      const complaint = await submitComplaint(token.access_token, {
        text: state.description,
        location: state.location
      });
      
      userStates.set(phone, { step: 'idle' });
      return `✅ Complaint registered!\n\nID: ${complaint.id}\nCategory: ${complaint.category.name}\nDepartment: ${complaint.department.name}\n\nTrack status by replying 'status'`;
  }
}
```

---

### 5. Check Complaint Status

```javascript
async function getMyComplaints(phone) {
  const token = await getOrCreateUser(phone);
  const response = await fetch(`${API_URL}/complaints/my`, {
    headers: { 'Authorization': `Bearer ${token.access_token}` }
  });
  const data = await response.json();
  
  if (data.complaints.length === 0) {
    return "You haven't submitted any complaints yet.";
  }
  
  let message = "📋 *Your Complaints:*\n\n";
  for (const c of data.complaints.slice(0, 5)) {
    const status = {
      'pending': '🟡',
      'assigned': '🔵',
      'in_progress': '🟠',
      'resolved': '🟢',
      'citizen_rejected': '🔴'
    }[c.status] || '⚪';
    
    message += `${status} *${c.title}*\n`;
    message += `   Status: ${c.status}\n`;
    message += `   Upvotes: ${c.upvote_count}\n\n`;
  }
  
  return message;
}
```

---

## Environment Setup for Bot

The Baileys bot needs these environment variables:

```bash
NAGRIK_API_URL=http://localhost:8000/api/v1  # or production URL
```

---

## Notes for Bot Developer

1. **Phone number handling**: Strip country code, keep last 10 digits for Indian numbers
2. **Media handling**: Download WhatsApp media, upload to `/files/upload`, get URL
3. **Location**: WhatsApp location messages contain `degreesLatitude` and `degreesLongitude`
4. **State management**: Use in-memory map or Redis for conversation state
5. **Error handling**: Always have fallback responses if API fails
6. **Rate limiting**: Implement per-user rate limiting to prevent spam

---

## Testing with Bot

```bash
# Start the API
cd backend && uvicorn app.main:app --reload --port 8000

# Start Baileys bot (in another terminal)
cd whatsapp-bot && node index.js

# Send message to WhatsApp number to test
```

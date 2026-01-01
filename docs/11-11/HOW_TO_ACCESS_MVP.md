# 🌐 How to Access Your MVP

**VM External IP:** `35.215.64.103`

---

## ✅ EASIEST OPTION: Direct VM Access

**Just open these URLs in your browser:**

### Frontend (Your MVP UI)
```
http://35.215.64.103:3000
```

### Backend API (Health Check)
```
http://35.215.64.103:8000/health
```

### API Documentation (Swagger UI)
```
http://35.215.64.103:8000/docs
```

---

## 🎯 YOUR 4 MVP PILLARS

Once you open the frontend (http://35.215.64.103:3000), you'll see:

1. **Data (Content Pillar)** - Upload & analyze files
2. **Insights** - Discover patterns & trends
3. **Operations** - Optimize your processes
4. **Business Outcomes** - Build your AI future

Click on any pillar to test its features!

---

## 🔐 ALTERNATIVE: SSH Port Forwarding (More Secure)

If you prefer to use `localhost` in your browser (more secure for production):

### Step 1: Disconnect from current SSH session
```bash
exit  # or just close the terminal
```

### Step 2: Reconnect with port forwarding
```bash
ssh -L 3000:localhost:3000 -L 8000:localhost:8000 [your-vm-ssh-command]
```

### Step 3: Access in browser
```
http://localhost:3000  (Frontend)
http://localhost:8000  (Backend)
```

**Benefits:**
- Traffic goes through encrypted SSH tunnel
- Firewall doesn't need to allow external access
- More secure for production deployments

---

## 🧪 QUICK TESTS YOU CAN DO

### 1. Visual Smoke Test
1. Open http://35.215.64.103:3000
2. Verify all 4 pillars are visible
3. Click each pillar to see if pages load

### 2. File Upload Test (Content Pillar)
1. Click "Data" pillar
2. Try uploading a test file
3. See if it gets parsed and analyzed

### 3. Backend Health Check
1. Open http://35.215.64.103:8000/health
2. Verify all managers show as "healthy"

### 4. API Documentation
1. Open http://35.215.64.103:8000/docs
2. Browse available endpoints
3. Try the "Try it out" feature on any endpoint

---

## ⚠️ WHY "localhost" DOESN'T WORK

When you SSH into the VM and then try to open `localhost:3000` in your **local browser**:

```
Your Browser (localhost:3000)
       ↓
  [Looks on YOUR computer] ❌ Nothing there!
```

The correct flow is:

```
Your Browser (VM_IP:3000)
       ↓
  [Connects to VM] ✅ Frontend is here!
```

Or with SSH port forwarding:

```
Your Browser (localhost:3000)
       ↓
  [SSH tunnel forwards to VM] ✅ Works!
```

---

## 🚀 START TESTING NOW!

**Click here to open your MVP:**
http://35.215.64.103:3000

All 4 pillars are operational and ready for testing! 🎉

---

## 📝 NOTES

- VM services are running on ports 3000 (frontend) and 8000 (backend)
- GCP firewall is allowing external access (ports are open)
- Both services are healthy and operational
- This is your development environment - for production, you'll deploy to Cloud Run

**Enjoy testing your MVP!** 🎊



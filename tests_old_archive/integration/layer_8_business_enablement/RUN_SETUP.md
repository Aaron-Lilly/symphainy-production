# How to Run the Setup Script

## Option 1: Run from Project Root (Recommended)

```bash
# From project root directory
cd /home/founders/demoversion/symphainy_source

# Run with full path
bash tests/integration/layer_8_business_enablement/setup_test_infrastructure.sh
```

## Option 2: Run from Test Directory

```bash
# Navigate to test directory first
cd /home/founders/demoversion/symphainy_source/tests/integration/layer_8_business_enablement

# Then run the script
./setup_test_infrastructure.sh
# OR
bash setup_test_infrastructure.sh
```

## Option 3: Use Absolute Path

```bash
bash /home/founders/demoversion/symphainy_source/tests/integration/layer_8_business_enablement/setup_test_infrastructure.sh
```

## Troubleshooting

### Error: "No such file or directory"

**If you see this error, try:**

1. **Check your current directory:**
   ```bash
   pwd
   # Should be: /home/founders/demoversion/symphainy_source
   ```

2. **Verify the script exists:**
   ```bash
   ls -la tests/integration/layer_8_business_enablement/setup_test_infrastructure.sh
   ```

3. **Use bash explicitly:**
   ```bash
   bash tests/integration/layer_8_business_enablement/setup_test_infrastructure.sh
   ```

4. **Check script permissions:**
   ```bash
   chmod +x tests/integration/layer_8_business_enablement/setup_test_infrastructure.sh
   ```

### Error: "Permission denied"

**Fix permissions:**
```bash
chmod +x tests/integration/layer_8_business_enablement/setup_test_infrastructure.sh
```

### Error: "gcloud: command not found"

**Install Google Cloud SDK:**
```bash
# Follow instructions at: https://cloud.google.com/sdk/docs/install
```

---

## Quick Copy-Paste Commands

**From project root:**
```bash
cd /home/founders/demoversion/symphainy_source
bash tests/integration/layer_8_business_enablement/setup_test_infrastructure.sh
```

**Or navigate first:**
```bash
cd /home/founders/demoversion/symphainy_source/tests/integration/layer_8_business_enablement
bash setup_test_infrastructure.sh
```


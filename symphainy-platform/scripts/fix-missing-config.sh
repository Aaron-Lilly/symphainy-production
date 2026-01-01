#!/bin/bash
# Fix missing configuration keys in .env.secrets

echo "🔧 Fixing missing configuration keys..."

# Add missing configuration keys to .env.secrets
cat >> .env.secrets << 'EOF'

# =============================================================================
# MISSING CONFIGURATION KEYS (REQUIRED BY UTILITIES)
# =============================================================================
# Database URLs (Required by utilities)
DATABASE_URL=http://localhost:8529
REDIS_URL=redis://localhost:6379

# Secret Key (Required by utilities)
SECRET_KEY=sk-1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef
EOF

echo "✅ Missing configuration keys added to .env.secrets"





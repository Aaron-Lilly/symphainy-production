#!/bin/bash
# Check which GitHub Secrets are configured
# Note: This can't read secret VALUES (they're encrypted), but can check if they EXIST

echo "========================================"
echo "GitHub Secrets Verification"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "This script will help you verify your GitHub Secrets setup."
echo ""
echo "${YELLOW}Note:${NC} GitHub Secrets are encrypted and can't be read."
echo "We'll guide you to check them manually in GitHub."
echo ""

# Check if gh CLI is installed
if command -v gh &> /dev/null; then
    echo "${GREEN}✓${NC} GitHub CLI (gh) is installed"
    echo ""
    
    # Check if authenticated
    if gh auth status &> /dev/null; then
        echo "${GREEN}✓${NC} GitHub CLI is authenticated"
        echo ""
        
        echo "Attempting to list repository secrets..."
        echo ""
        
        # Try to list secrets (requires admin access)
        gh secret list 2>&1 | head -20
        
    else
        echo "${RED}✗${NC} GitHub CLI is not authenticated"
        echo ""
        echo "To authenticate, run:"
        echo "  gh auth login"
    fi
else
    echo "${RED}✗${NC} GitHub CLI (gh) is not installed"
    echo ""
    echo "To install:"
    echo "  Debian/Ubuntu: sudo apt install gh"
    echo "  Mac: brew install gh"
    echo ""
    echo "Or check secrets manually (see below)"
fi

echo ""
echo "========================================"
echo "Required Secrets for Three-Tier Deployment"
echo "========================================"
echo ""

echo "📋 Required Secrets:"
echo ""
echo "For VM Staging (Tier 2):"
echo "  1. GCP_VM_IP           - Your VM's external IP"
echo "  2. GCP_VM_USERNAME     - SSH username (probably 'founders')"
echo "  3. GCP_VM_SSH_KEY      - Private SSH key for CI/CD"
echo ""
echo "For Cloud Run Production (Tier 3):"
echo "  4. GCP_PROJECT_ID      - Your GCP project ID"
echo "  5. GCP_SA_KEY          - Service account JSON key"
echo ""
echo "For Notifications (Optional):"
echo "  6. SLACK_WEBHOOK       - Slack webhook URL"
echo ""

echo "========================================"
echo "How to Check Secrets in GitHub (Manual)"
echo "========================================"
echo ""
echo "1. Go to: https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions"
echo "2. You should see a list of secret names (not values)"
echo "3. Compare with the required list above"
echo ""

echo "========================================"
echo "Quick Verification Commands"
echo "========================================"
echo ""

# Get VM IP
echo "${YELLOW}Your VM IP:${NC}"
gcloud compute instances list 2>/dev/null | grep -v NAME || echo "  Run: gcloud compute instances list"
echo ""

# Get GCP Project ID
echo "${YELLOW}Your GCP Project ID:${NC}"
gcloud config get-value project 2>/dev/null || echo "  Run: gcloud config get-value project"
echo ""

# Check if SSH key exists
echo "${YELLOW}SSH Key for CI/CD:${NC}"
if [ -f ~/.ssh/github_actions_key ]; then
    echo "  ${GREEN}✓${NC} Found: ~/.ssh/github_actions_key"
    echo "  Add this to GitHub Secret: GCP_VM_SSH_KEY"
else
    echo "  ${RED}✗${NC} Not found: ~/.ssh/github_actions_key"
    echo "  Generate with:"
    echo "    ssh-keygen -t rsa -b 4096 -C 'github-actions' -f ~/.ssh/github_actions_key -N ''"
    echo "    cat ~/.ssh/github_actions_key.pub >> ~/.ssh/authorized_keys"
fi
echo ""

# Check if service account key exists
echo "${YELLOW}GCP Service Account Key:${NC}"
if [ -f ~/github-actions-key.json ]; then
    echo "  ${GREEN}✓${NC} Found: ~/github-actions-key.json"
    echo "  Add this to GitHub Secret: GCP_SA_KEY"
else
    echo "  ${RED}✗${NC} Not found: ~/github-actions-key.json"
    echo "  Generate with:"
    echo "    gcloud iam service-accounts create github-actions-deploy"
    echo "    gcloud iam service-accounts keys create ~/github-actions-key.json \\"
    echo "      --iam-account=github-actions-deploy@YOUR_PROJECT.iam.gserviceaccount.com"
fi
echo ""

echo "========================================"
echo "Next Steps"
echo "========================================"
echo ""
echo "1. Review the required secrets list above"
echo "2. Check GitHub Settings → Secrets → Actions"
echo "3. Add any missing secrets"
echo "4. See full setup guide: .github/THREE_TIER_SETUP.md"
echo ""

# Test if we can reach the VM
echo "${YELLOW}Testing VM connectivity:${NC}"
VM_IP=$(gcloud compute instances list --format="get(networkInterfaces[0].accessConfigs[0].natIP)" 2>/dev/null | head -1)
if [ ! -z "$VM_IP" ]; then
    echo "  Testing: $VM_IP"
    if timeout 3 bash -c "echo > /dev/tcp/$VM_IP/22" 2>/dev/null; then
        echo "  ${GREEN}✓${NC} VM is reachable on port 22 (SSH)"
    else
        echo "  ${RED}✗${NC} Cannot reach VM on port 22"
        echo "  Check firewall rules"
    fi
else
    echo "  ${YELLOW}⚠${NC}  Could not detect VM IP automatically"
fi
echo ""





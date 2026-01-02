#!/bin/bash
# Environment Variable Validation Script
#
# Usage:
#   source validate-env.sh [environment]
#
# Validates that all required environment variables are set

ENVIRONMENT=${1:-development}

# Required variables (minimum set)
REQUIRED_VARS=(
    "FRONTEND_URL"
    "API_URL"
    "NEXT_PUBLIC_API_URL"
    "NEXT_PUBLIC_BACKEND_URL"
)

# Optional but recommended
RECOMMENDED_VARS=(
    "NEXT_PUBLIC_FRONTEND_URL"
    "CORS_ORIGINS"
    "API_CORS_ORIGINS"
)

# Production-specific requirements
if [ "${ENVIRONMENT}" = "production" ]; then
    REQUIRED_VARS+=(
        "ENVIRONMENT"
        "LOG_LEVEL"
    )
fi

# Check required variables
MISSING_VARS=()
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING_VARS+=("$var")
    fi
done

# Report missing variables
if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo "❌ Missing required environment variables:"
    for var in "${MISSING_VARS[@]}"; do
        echo "   - $var"
    done
    echo "💡 Set these in your .env.${ENVIRONMENT} file"
    return 1
fi

# Warn about missing recommended variables
MISSING_RECOMMENDED=()
for var in "${RECOMMENDED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING_RECOMMENDED+=("$var")
    fi
done

if [ ${#MISSING_RECOMMENDED[@]} -gt 0 ]; then
    echo "⚠️  Missing recommended environment variables:"
    for var in "${MISSING_RECOMMENDED[@]}"; do
        echo "   - $var"
    done
    echo "💡 These have defaults but may cause issues in production"
fi

echo "✅ Environment validation passed"
return 0





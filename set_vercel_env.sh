#!/bin/bash
# Set Environment Variables using Vercel CLI
# This script sets up the required environment variables for the Tenacious Stats dashboard

echo "Setting up Vercel environment variables..."

# Read the base64 encoded credentials
CREDENTIALS_B64=$(cat credentials_base64.txt | tr -d '\n')

# Set PROPERTY_ID
echo ""
echo "Setting PROPERTY_ID..."
echo "368035934" | vercel env add PROPERTY_ID production preview development

# Set GOOGLE_APPLICATION_CREDENTIALS_B64
echo ""
echo "Setting GOOGLE_APPLICATION_CREDENTIALS_B64..."
echo "$CREDENTIALS_B64" | vercel env add GOOGLE_APPLICATION_CREDENTIALS_B64 production preview development

echo ""
echo "✅ Environment variables set!"
echo ""
echo "Next steps:"
echo "1. Verify variables: vercel env ls"
echo "2. Deploy: vercel --prod"











#!/bin/bash

echo "Building and deploying frontend to Azure..."

cd frontend

echo "Installing dependencies..."
npm install

echo "Building Next.js app..."
npm run build

echo "Creating deployment package..."
mkdir -p deploy
cp -r .next/standalone/* deploy/
mkdir -p deploy/.next
cp -r .next/static deploy/.next/
[ -d "public" ] && cp -r public deploy/
cp package.json deploy/
echo 'node server.js' > deploy/startup.sh
chmod +x deploy/startup.sh

echo "Creating deployment zip..."
cd deploy
zip -r ../deploy.zip .
cd ..

echo "Deploying to Azure..."
az webapp deployment source config-zip \
  --resource-group livekitsdr-rg \
  --name livekitsdr-frontend \
  --src deploy.zip

echo "Cleaning up..."
rm -rf deploy deploy.zip

echo "Deployment complete!"
echo "Frontend URL: https://livekitsdr-frontend.azurewebsites.net"
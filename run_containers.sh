#!/bin/bash
# Build and run the SuperKart backend (Flask) and frontend (Streamlit) as separate containers
set -e

# 1. Create a user-defined Docker network so the containers can reach each other by name
docker network create superkart-net 2>/dev/null || true

# 2. Build the images
docker build -t superkart-backend ./backend_files
docker build -t superkart-frontend ./frontend_files

# 3. Remove old containers, if any
docker rm -f superkart-backend superkart-frontend 2>/dev/null || true

# 4. Run the backend (port 7860) and the frontend (port 8501) on the same network
docker run -d --name superkart-backend --network superkart-net -p 7860:7860 superkart-backend
docker run -d --name superkart-frontend --network superkart-net -p 8501:8501 \
    -e BACKEND_URL=http://superkart-backend:7860 superkart-frontend

docker ps
echo "Backend  -> port 7860 | Frontend -> port 8501 (make both ports Public in the Ports tab)"

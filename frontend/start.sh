#!/bin/bash
# Smart startup: use lightweight 'serve' for production, 'craco start' for preview/dev
# This prevents the CRA webpack dev server from consuming 500MB+ of memory in production

# Check if we're in a production/deployed environment
if [ "$ENABLE_HEALTH_CHECK" = "true" ] || [ "$NODE_ENV" = "production" ]; then
    echo "[FRONTEND] Production mode: serving static build with 'serve'"
    # Ensure build exists
    if [ -d "build" ]; then
        exec npx serve -s build -l 3000
    else
        echo "[FRONTEND] No build directory found, running yarn build first..."
        yarn build
        exec npx serve -s build -l 3000
    fi
else
    echo "[FRONTEND] Development mode: starting CRA dev server"
    exec yarn craco start
fi

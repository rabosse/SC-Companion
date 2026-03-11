const { execSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const http = require('http');

const buildDir = path.join(__dirname, 'build');
const buildExists = fs.existsSync(path.join(buildDir, 'index.html'));

// In production (ENABLE_HEALTH_CHECK=true from K8s secret), serve static build
// In development, use CRA dev server
const isProduction = process.env.ENABLE_HEALTH_CHECK === 'true';

if (isProduction && buildExists) {
  console.log('[FRONTEND] Production mode: serving static build');
  
  // Try serve package first
  try {
    const servePath = path.join(__dirname, 'node_modules', '.bin', 'serve');
    if (fs.existsSync(servePath)) {
      execSync('npx serve -s build -l 3000', { stdio: 'inherit', cwd: __dirname });
    } else {
      throw new Error('serve not found in node_modules');
    }
  } catch (e) {
    console.log('[FRONTEND] serve package not available, using built-in HTTP server');
    // Fallback: built-in Node.js static file server
    const server = http.createServer((req, res) => {
      let filePath = path.join(buildDir, req.url === '/' ? 'index.html' : req.url);
      
      // SPA fallback - serve index.html for non-file routes
      if (!fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
        filePath = path.join(buildDir, 'index.html');
      }
      
      const ext = path.extname(filePath).toLowerCase();
      const mimeTypes = {
        '.html': 'text/html', '.js': 'application/javascript', '.css': 'text/css',
        '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg',
        '.svg': 'image/svg+xml', '.ico': 'image/x-icon', '.woff': 'font/woff',
        '.woff2': 'font/woff2', '.ttf': 'font/ttf', '.map': 'application/json',
      };
      
      try {
        const content = fs.readFileSync(filePath);
        res.writeHead(200, { 'Content-Type': mimeTypes[ext] || 'application/octet-stream' });
        res.end(content);
      } catch {
        // SPA fallback
        const index = fs.readFileSync(path.join(buildDir, 'index.html'));
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.end(index);
      }
    });
    
    server.listen(3000, '0.0.0.0', () => {
      console.log('[FRONTEND] Built-in server listening on port 3000');
    });
  }
} else if (buildExists) {
  // Build exists but not explicitly production - try serve first, fallback to craco
  console.log('[FRONTEND] Build exists, trying lightweight serve...');
  try {
    execSync('npx serve -s build -l 3000', { stdio: 'inherit', cwd: __dirname });
  } catch {
    console.log('[FRONTEND] Falling back to CRA dev server');
    execSync('craco start', { stdio: 'inherit', cwd: __dirname });
  }
} else {
  console.log('[FRONTEND] Development mode: starting CRA dev server');
  execSync('craco start', { stdio: 'inherit', cwd: __dirname });
}

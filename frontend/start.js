const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const isProduction = process.env.ENABLE_HEALTH_CHECK === 'true';
const buildExists = fs.existsSync(path.join(__dirname, 'build', 'index.html'));

if (isProduction && buildExists) {
  console.log('[FRONTEND] Production mode: serving static build');
  execSync('npx serve -s build -l 3000', { stdio: 'inherit', cwd: __dirname });
} else {
  console.log('[FRONTEND] Development mode: starting CRA dev server');
  execSync('craco start', { stdio: 'inherit', cwd: __dirname });
}

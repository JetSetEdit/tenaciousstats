const fs = require('fs');
const path = require('path');

const versionFile = path.join(__dirname, 'public', 'version.txt');

// Read current version
let version = '1.0.0';
if (fs.existsSync(versionFile)) {
    version = fs.readFileSync(versionFile, 'utf8').trim();
}

// Parse version (semantic versioning: major.minor.patch)
const parts = version.split('.');
let major = parseInt(parts[0]) || 1;
let minor = parseInt(parts[1]) || 0;
let patch = parseInt(parts[2]) || 0;

// Increment patch version
patch++;

// Write new version
const newVersion = `${major}.${minor}.${patch}`;
fs.writeFileSync(versionFile, newVersion, 'utf8');

console.log(`Version incremented: ${version} → ${newVersion}`);









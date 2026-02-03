/**
 * Download deployment source from Vercel by deployment URL.
 * Usage: node download_vercel_deployment.js
 * Requires: VERCEL_ACCESS_TOKEN env var, and optionally pass deployment URL as first arg.
 */
const DEPLOYMENT_URL = process.argv[2] || 'tenacious-stats-dashboard-33ezfj9nh-admin-jetseteditas-projects.vercel.app';
const OUT_DIR = process.argv[3] || './vercel-deployment-download';
const TOKEN = process.env.VERCEL_ACCESS_TOKEN;

if (!TOKEN) {
  console.error('Set VERCEL_ACCESS_TOKEN environment variable.');
  process.exit(1);
}

const fs = require('fs');
const path = require('path');

async function get(url, opts = {}) {
  const res = await fetch(url, {
    ...opts,
    headers: {
      Authorization: `Bearer ${TOKEN}`,
      ...(opts.headers || {}),
    },
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}: ${await res.text()}`);
  return res.json();
}

async function getDeployment(idOrUrl) {
  const url = `https://api.vercel.com/v13/deployments/${encodeURIComponent(idOrUrl)}?slug=admin-jetseteditas-projects`;
  return get(url);
}

async function listFiles(deploymentId) {
  const url = `https://api.vercel.com/v6/deployments/${deploymentId}/files?slug=admin-jetseteditas-projects`;
  return get(url);
}

async function getFileContent(deploymentId, fileId) {
  const url = `https://api.vercel.com/v8/deployments/${deploymentId}/files/${fileId}?slug=admin-jetseteditas-projects`;
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${TOKEN}` },
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.text();
}

function flattenFiles(entries, prefix = '') {
  let files = [];
  for (const e of entries || []) {
    const name = path.join(prefix, e.name);
    if (e.type === 'file' && e.uid) {
      files.push({ path: name.replace(/\\/g, '/'), uid: e.uid });
    } else if (e.type === 'directory' && e.children) {
      files = files.concat(flattenFiles(e.children, name));
    }
  }
  return files;
}

async function main() {
  console.log('Fetching deployment:', DEPLOYMENT_URL);
  const deployment = await getDeployment(DEPLOYMENT_URL);
  const id = deployment.id;
  console.log('Deployment id:', id);

  let fileTree;
  try {
    fileTree = await listFiles(id);
  } catch (e) {
    console.warn('List files failed (Git deployments may not expose file tree):', e.message);
    console.log('Deployment metadata saved to', path.join(OUT_DIR, 'deployment.json'));
    fs.mkdirSync(OUT_DIR, { recursive: true });
    fs.writeFileSync(path.join(OUT_DIR, 'deployment.json'), JSON.stringify(deployment, null, 2));
    return;
  }

  const files = flattenFiles(fileTree);
  console.log('Files to download:', files.length);
  fs.mkdirSync(OUT_DIR, { recursive: true });
  fs.writeFileSync(path.join(OUT_DIR, 'deployment.json'), JSON.stringify(deployment, null, 2));

  for (const { path: filePath, uid } of files) {
    try {
      const content = await getFileContent(id, uid);
      const fullPath = path.join(OUT_DIR, filePath);
      fs.mkdirSync(path.dirname(fullPath), { recursive: true });
      fs.writeFileSync(fullPath, content, 'utf8');
      console.log('  ', filePath);
    } catch (e) {
      console.warn('  Skip', filePath, e.message);
    }
  }
  console.log('Done. Output:', OUT_DIR);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});

module.exports = {
  apps: [
    {
      name: 'poke-mcp-ssh-bridge',
      script: './scripts/start.sh',
      interpreter: 'bash',
      cwd: '/root/poke-mcp-ssh-bridge',
      autorestart: true,
      watch: false,
      max_restarts: 10,
      env: {
        PYTHONUNBUFFERED: '1'
      }
    },
    {
      name: 'poke-mcp-ssh-bridge-tunnel',
      script: './scripts/start-cloudflared.sh',
      interpreter: 'bash',
      cwd: '/root/poke-mcp-ssh-bridge',
      autorestart: true,
      watch: false,
      max_restarts: 10,
      env: {
        PYTHONUNBUFFERED: '1'
      }
    }
  ]
};
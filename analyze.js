{
  "version": 2,
  "builds": [
    { "src": "analyze.js", "use": "@vercel/node" },
    { "src": "index.html", "use": "@vercel/static" }
  ],
  "routes": [
    { "src": "/api/(.*)", "dest": "/analyze.js" },
    { "src": "/(.*)", "dest": "/index.html" }
  ]
}

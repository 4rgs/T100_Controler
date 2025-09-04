const CACHE_NAME = 't100-controller-v1.2';
const STATIC_CACHE_URLS = [
  './',
  './index.html',
  './manifest.json'
];

// Instalación del Service Worker
self.addEventListener('install', event => {
  console.log('Service Worker: Installing...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Service Worker: Caching App Shell');
        return cache.addAll(STATIC_CACHE_URLS);
      })
      .then(() => {
        console.log('Service Worker: Installed');
        return self.skipWaiting();
      })
  );
});

// Activación del Service Worker
self.addEventListener('activate', event => {
  console.log('Service Worker: Activating...');
  
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Service Worker: Clearing Old Cache');
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('Service Worker: Activated');
      return self.clients.claim();
    })
  );
});

// Estrategia de caché: Network First (para contenido dinámico)
self.addEventListener('fetch', event => {
  // Solo interceptar requests GET
  if (event.request.method !== 'GET') return;
  
  // No cachear WebSocket connections
  if (event.request.url.includes('ws://') || event.request.url.includes('wss://')) {
    return;
  }

  event.respondWith(
    fetch(event.request)
      .then(response => {
        // Si la respuesta es válida, guardar en cache
        if (response.status === 200) {
          const responseClone = response.clone();
          caches.open(CACHE_NAME)
            .then(cache => {
              cache.put(event.request, responseClone);
            });
        }
        return response;
      })
      .catch(() => {
        // Si falla la red, intentar servir desde cache
        return caches.match(event.request)
          .then(response => {
            if (response) {
              console.log('Service Worker: Serving from cache:', event.request.url);
              return response;
            }
            
            // Si no hay cache disponible, mostrar página offline básica
            if (event.request.destination === 'document') {
              return new Response(`
                <!DOCTYPE html>
                <html>
                <head>
                  <title>T100 Controller - Offline</title>
                  <meta name="viewport" content="width=device-width, initial-scale=1">
                  <style>
                    body { 
                      font-family: Arial, sans-serif; 
                      background: linear-gradient(135deg, #2c3e50, #34495e); 
                      color: white; 
                      text-align: center; 
                      padding: 50px; 
                      margin: 0;
                    }
                    .offline-msg {
                      max-width: 500px;
                      margin: 0 auto;
                      padding: 30px;
                      border-radius: 15px;
                      background: rgba(255,255,255,0.1);
                    }
                    .retry-btn {
                      padding: 15px 30px;
                      background: #3498db;
                      color: white;
                      border: none;
                      border-radius: 8px;
                      font-size: 16px;
                      cursor: pointer;
                      margin-top: 20px;
                    }
                    .retry-btn:hover { background: #2980b9; }
                  </style>
                </head>
                <body>
                  <div class="offline-msg">
                    <h1>🤖 T100 Controller</h1>
                    <h2>📡 Sin Conexión</h2>
                    <p>No se puede conectar al servidor. Verifica tu conexión a internet e intenta de nuevo.</p>
                    <button class="retry-btn" onclick="window.location.reload()">🔄 Reintentar</button>
                  </div>
                </body>
                </html>
              `, {
                headers: { 'Content-Type': 'text/html' }
              });
            }
          });
      })
  );
});

// Manejar mensajes del cliente
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

// Sincronización en segundo plano (opcional)
self.addEventListener('sync', event => {
  if (event.tag === 'background-sync') {
    event.waitUntil(
      console.log('Service Worker: Background sync triggered')
    );
  }
});

/**
 * Service Worker for DU Admission Analyzer
 * Provides offline support and caching strategies
 */

const CACHE_NAME = 'du-analyzer-v1.0.0';
const STATIC_CACHE = 'du-analyzer-static-v1';
const DYNAMIC_CACHE = 'du-analyzer-dynamic-v1';

// Files to cache for offline use
const STATIC_FILES = [
    '/',
    '/static/app.js',
    '/static/styles.css',
    '/static/manifest.json',
    'https://cdn.tailwindcss.com',
    'https://cdn.jsdelivr.net/npm/chart.js',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'
];

// API endpoints to cache
const API_ENDPOINTS = [
    '/api/files',
    '/api/status',
    '/api/analytics'
];

// Install event - cache static files
self.addEventListener('install', event => {
    console.log('Service Worker: Installing...');
    
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then(cache => {
                console.log('Service Worker: Caching static files');
                return cache.addAll(STATIC_FILES);
            })
            .then(() => {
                console.log('Service Worker: Skip waiting');
                return self.skipWaiting();
            })
            .catch(err => {
                console.error('Service Worker: Error caching static files', err);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    console.log('Service Worker: Activating...');
    
    event.waitUntil(
        caches.keys()
            .then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => {
                        if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
                            console.log('Service Worker: Deleting old cache', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('Service Worker: Claiming clients');
                return self.clients.claim();
            })
    );
});

// Fetch event - serve cached files and implement caching strategies
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }
    
    // Skip chrome-extension requests
    if (url.protocol === 'chrome-extension:') {
        return;
    }
    
    // Handle different types of requests
    if (request.url.includes('/api/')) {
        // API requests - network first, then cache
        event.respondWith(networkFirstStrategy(request));
    } else if (STATIC_FILES.some(file => request.url.includes(file))) {
        // Static files - cache first
        event.respondWith(cacheFirstStrategy(request));
    } else {
        // Other requests - network first with cache fallback
        event.respondWith(networkFirstStrategy(request));
    }
});

// Cache-first strategy for static files
async function cacheFirstStrategy(request) {
    try {
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            const cache = await caches.open(STATIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.error('Cache-first strategy failed:', error);
        return new Response('Offline', { status: 503 });
    }
}

// Network-first strategy for dynamic content
async function networkFirstStrategy(request) {
    try {
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.log('Network failed, trying cache:', error);
        
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Return offline page for navigation requests
        if (request.mode === 'navigate') {
            return caches.match('/');
        }
        
        return new Response('Offline', { 
            status: 503,
            statusText: 'Service Unavailable',
            headers: { 'Content-Type': 'text/plain' }
        });
    }
}

// Background sync for file uploads
self.addEventListener('sync', event => {
    console.log('Service Worker: Background sync triggered');
    
    if (event.tag === 'background-upload') {
        event.waitUntil(handleBackgroundUpload());
    }
});

async function handleBackgroundUpload() {
    try {
        // Get pending uploads from IndexedDB
        const pendingUploads = await getPendingUploads();
        
        for (const upload of pendingUploads) {
            try {
                await fetch('/api/upload', {
                    method: 'POST',
                    body: upload.formData
                });
                
                // Remove from pending uploads
                await removePendingUpload(upload.id);
                
                // Notify clients of successful upload
                self.clients.matchAll().then(clients => {
                    clients.forEach(client => {
                        client.postMessage({
                            type: 'UPLOAD_SUCCESS',
                            uploadId: upload.id
                        });
                    });
                });
            } catch (error) {
                console.error('Background upload failed:', error);
            }
        }
    } catch (error) {
        console.error('Background sync failed:', error);
    }
}

// IndexedDB operations for offline storage
function openDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('du-analyzer-db', 1);
        
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
        
        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            
            if (!db.objectStoreNames.contains('uploads')) {
                const uploadStore = db.createObjectStore('uploads', { keyPath: 'id' });
                uploadStore.createIndex('timestamp', 'timestamp', { unique: false });
            }
            
            if (!db.objectStoreNames.contains('analytics')) {
                const analyticsStore = db.createObjectStore('analytics', { keyPath: 'id' });
                analyticsStore.createIndex('processId', 'processId', { unique: false });
            }
        };
    });
}

async function getPendingUploads() {
    const db = await openDB();
    const transaction = db.transaction(['uploads'], 'readonly');
    const store = transaction.objectStore('uploads');
    
    return new Promise((resolve, reject) => {
        const request = store.getAll();
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
    });
}

async function removePendingUpload(id) {
    const db = await openDB();
    const transaction = db.transaction(['uploads'], 'readwrite');
    const store = transaction.objectStore('uploads');
    
    return new Promise((resolve, reject) => {
        const request = store.delete(id);
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve();
    });
}

// Push notifications for processing updates
self.addEventListener('push', event => {
    console.log('Service Worker: Push received');
    
    if (event.data) {
        const data = event.data.json();
        
        const options = {
            body: data.message || 'Processing update available',
            icon: '/static/icon-192x192.png',
            badge: '/static/badge-72x72.png',
            vibrate: [100, 50, 100],
            data: {
                processId: data.processId,
                url: data.url || '/'
            },
            actions: [
                {
                    action: 'view',
                    title: 'View Results',
                    icon: '/static/view-icon.png'
                },
                {
                    action: 'dismiss',
                    title: 'Dismiss',
                    icon: '/static/dismiss-icon.png'
                }
            ]
        };
        
        event.waitUntil(
            self.registration.showNotification(
                data.title || 'DU Admission Analyzer',
                options
            )
        );
    }
});

// Notification click handling
self.addEventListener('notificationclick', event => {
    console.log('Service Worker: Notification clicked');
    
    event.notification.close();
    
    if (event.action === 'view') {
        event.waitUntil(
            clients.openWindow(event.notification.data.url)
        );
    } else if (event.action === 'dismiss') {
        // Just close the notification
        return;
    } else {
        // Default action - open the app
        event.waitUntil(
            clients.matchAll({ type: 'window' }).then(clientList => {
                for (const client of clientList) {
                    if (client.url === '/' && 'focus' in client) {
                        return client.focus();
                    }
                }
                if (clients.openWindow) {
                    return clients.openWindow('/');
                }
            })
        );
    }
});

// Message handling for communication with main app
self.addEventListener('message', event => {
    console.log('Service Worker: Message received', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'CACHE_ANALYTICS') {
        cacheAnalyticsData(event.data.data);
    }
    
    if (event.data && event.data.type === 'GET_CACHE_STATUS') {
        getCacheStatus().then(status => {
            event.ports[0].postMessage(status);
        });
    }
});

async function cacheAnalyticsData(data) {
    try {
        const db = await openDB();
        const transaction = db.transaction(['analytics'], 'readwrite');
        const store = transaction.objectStore('analytics');
        
        await new Promise((resolve, reject) => {
            const request = store.put({
                id: data.processId,
                processId: data.processId,
                data: data,
                timestamp: Date.now()
            });
            request.onerror = () => reject(request.error);
            request.onsuccess = () => resolve();
        });
        
        console.log('Analytics data cached successfully');
    } catch (error) {
        console.error('Failed to cache analytics data:', error);
    }
}

async function getCacheStatus() {
    try {
        const cacheNames = await caches.keys();
        const status = {
            caches: cacheNames.length,
            staticCached: await caches.has(STATIC_CACHE),
            dynamicCached: await caches.has(DYNAMIC_CACHE),
            lastUpdated: Date.now()
        };
        
        return status;
    } catch (error) {
        console.error('Failed to get cache status:', error);
        return { error: error.message };
    }
}

// Periodic cleanup of old cache entries
self.addEventListener('periodicsync', event => {
    if (event.tag === 'cache-cleanup') {
        event.waitUntil(cleanupOldCaches());
    }
});

async function cleanupOldCaches() {
    const maxAge = 7 * 24 * 60 * 60 * 1000; // 7 days
    const now = Date.now();
    
    try {
        const cache = await caches.open(DYNAMIC_CACHE);
        const keys = await cache.keys();
        
        for (const request of keys) {
            const response = await cache.match(request);
            const dateHeader = response.headers.get('date');
            
            if (dateHeader) {
                const responseDate = new Date(dateHeader).getTime();
                if (now - responseDate > maxAge) {
                    await cache.delete(request);
                    console.log('Cleaned up old cache entry:', request.url);
                }
            }
        }
    } catch (error) {
        console.error('Cache cleanup failed:', error);
    }
}

// Error handling
self.addEventListener('error', event => {
    console.error('Service Worker error:', event.error);
});

self.addEventListener('unhandledrejection', event => {
    console.error('Service Worker unhandled rejection:', event.reason);
});

console.log('Service Worker: Script loaded');

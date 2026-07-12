/// <reference no-default-lib="true"/>
/// <reference lib="esnext" />
/// <reference lib="webworker" />
/// <reference types="@sveltejs/kit" />

import { build, files, version } from '$service-worker';

const CACHE = `salus-${version}`;
const ASSETS = [...build, ...files, '/_app/version.json', '/index.html'];
const API_RE = /^\/(?:api|auth)\//;
const IMMUTABLE = '/_app/immutable/';

// ---- install: cache all files in parallel, tolerate individual failures ----

self.addEventListener('install', (event) => {
	let failed = 0;
	const t0 = Date.now();
	event.waitUntil(
		caches.open(CACHE).then(async (cache) => {
			await Promise.all(
				ASSETS.map((asset) =>
					cache.add(asset).catch((err) => {
						failed++;
						console.warn(`[SW] precache failed: ${asset}`, err);
					})
				)
			);
			await self.skipWaiting();
			console.log(`[SW] precached ${ASSETS.length - failed}/${ASSETS.length} assets in ${Date.now() - t0}ms`);
		})
	);
});

// ---- activate: claim clients, purge old caches ----

self.addEventListener('activate', (event) => {
	event.waitUntil(
		(async () => {
			await self.clients.claim();
			const keys = await caches.keys();
			await Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)));
		})()
	);
});

// ---- fetch: assets from cache, API passthrough, navigate fallback ----

function isBuildArtifact(pathname) {
	return pathname.startsWith(IMMUTABLE) || pathname === '/_app/version.json';
}

self.addEventListener('fetch', (event) => {
	const { request } = event;
	if (request.method !== 'GET') return;

	const url = new URL(request.url);

	if (API_RE.test(url.pathname)) return;

	if (isBuildArtifact(url.pathname)) {
		event.respondWith(
			(async () => {
				const cache = await caches.open(CACHE);
				const cached = await cache.match(request, { ignoreVary: true, ignoreSearch: true });
				if (cached) return cached;
				try {
					const response = await fetch(request);
					if (response.ok) {
						cache.put(request, response.clone());
					}
					return response;
				} catch {
					if (url.pathname === '/_app/version.json') {
						return Response.json({});
					}
					return new Response('Offline', { status: 503 });
				}
			})()
		);
		return;
	}

	if (request.mode === 'navigate') {
		event.respondWith(
			(async () => {
				const cache = await caches.open(CACHE);
				const cachedIndex = await cache.match('/index.html');
				if (cachedIndex) return cachedIndex;
				try {
					const response = await fetch(request);
					if (response.ok) {
						cache.put('/index.html', response.clone());
					}
					return response;
				} catch {
					const fallback = await cache.match('/offline.html');
					return fallback || new Response('Offline', { status: 503 });
				}
			})()
		);
		return;
	}

	event.respondWith(
		(async () => {
			const cache = await caches.open(CACHE);
			const cached = await cache.match(request);
			if (cached) return cached;
			try {
				const response = await fetch(request);
				if (response.ok) {
					cache.put(request, response.clone());
				}
				return response;
			} catch {
				return new Response('', { status: 408 });
			}
		})()
	);
});

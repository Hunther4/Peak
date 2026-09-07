# Plan PWA — Peak Practice

> Convertir Peak de web app a Progressive Web App instalable en móvil.
> **Prioridad:** Después de corregir los errores de la auditoría y estabilizar el backend.

---

## ¿Qué es una PWA?

Tu misma app web, pero el navegador la trata como app nativa:
- Icono en la pantalla de inicio (al lado de WhatsApp, Spotify, etc.)
- Se abre sin barra de URL (pantalla completa)
- Carga instantánea gracias al cache del Service Worker
- Funciona offline (lectura de datos cacheados)

**No se reescribe nada.** Se agregan 3 archivos y se ajusta el CSS para mobile.

---

## Prerequisitos

| Requisito | Estado | Notas |
|-----------|--------|-------|
| HTTPS en producción | ❌ Pendiente | PWA requiere HTTPS. En `localhost` funciona sin SSL para desarrollo |
| App responsive | ⚠️ Parcial | La UI actual usa `lg:grid-cols-12`. Falta revisar breakpoints mobile |
| Vite como bundler | ✅ Listo | Vite tiene plugin oficial para PWA (`vite-plugin-pwa`) |

---

## Fases de Implementación

### Fase 1 — Manifest + Iconos (30 min)

**Archivo:** `frontend/public/manifest.json`

```json
{
  "name": "Peak Practice",
  "short_name": "Peak",
  "description": "Tu ciudadela privada de práctica deliberada",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#0a0a0a",
  "theme_color": "#22c55e",
  "orientation": "portrait",
  "icons": [
    { "src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png" },
    { "src": "/icons/icon-512-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ]
}
```

**Iconos necesarios:**
- `icon-192.png` — Icono estándar (192×192)
- `icon-512.png` — Icono grande (512×512)
- `icon-512-maskable.png` — Icono con safe zone para Android (512×512 con padding)

**Acción:** Generar los iconos con el logo "P" gradiente verde que ya tenemos en el header.

---

### Fase 2 — Service Worker con vite-plugin-pwa (45 min)

**Instalar:**
```bash
cd frontend
pnpm install -D vite-plugin-pwa
```

**Configurar en `vite.config.js`:**
```js
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'icons/*.png'],
      manifest: false, // Usamos el manifest.json manual
      workbox: {
        // Cache de assets estáticos (JS, CSS, imágenes)
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
        // Cache de llamadas a la API (estrategia network-first)
        runtimeCaching: [
          {
            urlPattern: /^http:\/\/localhost:8000\/api\//,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'peak-api-cache',
              expiration: { maxEntries: 50, maxAgeSeconds: 60 * 60 }, // 1 hora
            },
          },
        ],
      },
    }),
  ],
})
```

**Qué hace esto:**
- Cachea todos los archivos estáticos → la app carga instantáneamente
- Las llamadas a `/api/` intentan red primero, si no hay red usa el cache
- Se auto-actualiza cuando deployeás cambios

---

### Fase 3 — Meta tags en index.html (10 min)

**Archivo:** `frontend/index.html`

```html
<head>
  <!-- PWA -->
  <link rel="manifest" href="/manifest.json" />
  <meta name="theme-color" content="#22c55e" />
  <meta name="apple-mobile-web-app-capable" content="yes" />
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
  <link rel="apple-touch-icon" href="/icons/icon-192.png" />

  <!-- Viewport mobile -->
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
</head>
```

---

### Fase 4 — CSS Responsive para Mobile (1–2 horas)

Este es el trabajo más pesado. La UI actual está diseñada para desktop.

**Cambios principales:**

| Componente | Problema actual | Fix mobile |
|------------|----------------|------------|
| Layout principal | `grid-cols-12` con columna de 5 y 7 | En mobile: stack vertical (`grid-cols-1`) |
| `SessionForm` | Grid 2 columnas para skill/duración | En mobile: stack vertical |
| `AiModeToggle` | En el header, puede quedar apretado | Mover a un menú hamburguesa o hacerlo más compacto |
| `Timeline` | Ocupa la columna derecha completa | En mobile: va abajo del formulario |
| `SkillCard` | Grid de 3 stats en fila | Revisar que no se aprieten |
| `BooksPanel` | Ancho fijo | Hacer fluid |

**Breakpoints sugeridos (ya definidos por Tailwind):**
- `sm:` → 640px (teléfonos grandes)
- `md:` → 768px (tablets)
- `lg:` → 1024px (desktop — lo que tenemos ahora)

**Regla:** Todo lo que dice `lg:grid-cols-X` ya es responsive por defecto (mobile = 1 columna). Solo hay que revisar que no haya nada hardcodeado que rompa en pantallas chicas.

---

### Fase 5 — Testing en Mobile (30 min)

1. **Chrome DevTools** → Toggle Device Toolbar (Ctrl+Shift+M) → iPhone 14 / Pixel 7
2. **Conectar el celu real** → Abrir `http://<IP-local>:5173` en el browser del celu
3. **Lighthouse audit** → Chrome DevTools → Lighthouse → Categoría "PWA"
   - Debe dar ≥ 90 en "Installable" y "PWA Optimized"
4. **Instalar en el celu** → Menú del browser → "Agregar a pantalla de inicio"
5. **Probar offline** → Activar modo avión → La app debe cargar (datos cacheados)

---

## Consideraciones Especiales para Peak

### Offline: ¿Qué funciona y qué no?

| Feature | Offline | Por qué |
|---------|---------|---------|
| Ver dashboard y sesiones previas | ✅ | Cacheadas por el Service Worker |
| Ver skill cards y stats | ✅ | Datos del último fetch |
| Crear nueva sesión | ⚠️ Parcial | Se podría encolar y sincronizar después (Background Sync) |
| Auditoría IA | ❌ | Requiere LM Studio / Groq / OpenRouter activos |
| Indexar libros | ❌ | Requiere backend + ChromaDB |

### HTTPS para producción

Si querés usar Peak en el celu **fuera de tu red local**, necesitás HTTPS. Opciones:

1. **Tailscale / WireGuard** — Tunel VPN privado. Tu celu se conecta a tu PC como si estuviera en la misma red. **Recomendado para Peak** (privacidad total, gratis).
2. **Cloudflare Tunnel** — Expone tu backend al mundo con HTTPS automático. Gratis. Pero tu tráfico pasa por Cloudflare.
3. **Let's Encrypt + dominio** — HTTPS real con certificado gratuito. Requiere un dominio (~$10/año).

**Mi recomendación:** Tailscale. Filosofía Peak: privado, sin terceros, sin costo.

---

## Estimación Total

| Fase | Tiempo | Dificultad |
|------|--------|------------|
| 1. Manifest + Iconos | 30 min | Trivial |
| 2. Service Worker | 45 min | Bajo |
| 3. Meta tags | 10 min | Trivial |
| 4. CSS Responsive | 1–2 horas | Medio |
| 5. Testing mobile | 30 min | Bajo |
| **Total** | **~3–4 horas** | **Bajo–Medio** |

---

## Checklist Final (para cuando lo implementemos)

- [ ] Generar iconos PNG (192, 512, 512-maskable)
- [ ] Crear `manifest.json` en `frontend/public/`
- [ ] Instalar y configurar `vite-plugin-pwa`
- [ ] Agregar meta tags PWA en `index.html`
- [ ] Revisar todos los componentes en viewport mobile (375px)
- [ ] Ajustar grid layout principal para stack vertical en mobile
- [ ] Hacer SessionForm responsive
- [ ] Hacer AiModeToggle compacto en mobile
- [ ] Correr Lighthouse PWA audit → score ≥ 90
- [ ] Instalar en celu real y probar flujo completo
- [ ] Configurar Tailscale (opcional, para acceso fuera de la red local)

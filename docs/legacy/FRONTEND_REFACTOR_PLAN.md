# Peak Frontend Refactor Plan

## Estado Actual

**Stack**: React 19 + Tailwind 4 + Zustand + Vite 8  
**Componentes**: 25  
**Estética**: Dark premium, glassmorphism, partículas, gradientes mesh  
**Problema central**: Todo en una página sin navegación, App.jsx es un monolito de 325 líneas

---

## Fase 1: Estructura y Navegación (Prioridad ALTA)

### 1.1 Router con React Router
- Instalar `react-router-dom`
- Crear rutas: `/` (dashboard), `/practice/:skillType/:skillId`, `/settings`
- El juego se abre como modal OVERLAY, no como ruta separada
- **Por qué**: Sin navegación, el usuario no puede volver atrás ni compartir links

### 1.2 Layout con Sidebar o Bottom Nav
- **Sidebar colapsable** en desktop (iconos + labels)
- **Bottom nav** en mobile (4 tabs: Dashboard, Practicar, Progreso, Ajustes)
- Mostrar avatar + nombre del usuario
- **Por qué**: El usuario necesita orientación de "dónde estoy"

### 1.3 App.jsx → Shell
- App.jsx solo maneja layout + router
- Mover lógica de juegos a `pages/Practice.jsx`
- Mover lógica de clear data a `pages/Settings.jsx`
- **Por qué**: 325 líneas en un archivo = mantenimiento imposible

---

## Fase 2: Dashboard Rediseñado (Prioridad ALTA)

### 2.1 Hero Section con Stats Clave
- 3-4 métricas grandes: Sesiones totales, Racha actual, Nivel promedio, Tiempo practicado
- Estilo: cards con gradientes sutiles, números grandes
- **Por qué**: El usuario quiere ver su progreso de un vistazo

### 2.2 Skills jerárquicas (YA HECHO)
- Root skills como cards principales
- Sub-skills collapsables
- Indicador de plateau visible

### 2.3 Quick Actions
- Botón "Practicar ahora" prominente
- Última sesión con link rápido
- **Por qué**: Reducir clicks para practicar

---

## Fase 3: Componentes Reutilizables (Prioridad MEDIA)

### 3.1 Design System Components
Crear `components/ui/` con:
- `Button.jsx` (variantes: primary, ghost, danger)
- `Card.jsx` (glass panel reutilizable)
- `Badge.jsx` (deliberate, pending, etc.)
- `ProgressBar.jsx` (niveles, staircase)
- `Modal.jsx` (ya existe en ui.jsx, mover)
- `Toast.jsx` (ya existe, mover)
- `Spinner.jsx` (ya existe, mover)
- `EmptyState.jsx` (para estados vacíos)

### 3.2 SkillCard refactorizado
- Usar nuevos componentes UI
- Reducir de 159 → ~80 líneas
- Separar level ring en componente propio

### 3.3 SubSkillCard mejorado
- Agregar mini-gráfico de tendencia (sube/baja/estable)
- Tiempo desde última práctica
- **Por qué**: Dar contexto sin navegar

---

## Fase 4: Experiencia de Juego (Prioridad MEDIA)

### 4.1 GameShell mejorado
- Usar `layout/GameShell.jsx` (ya existe)
- Agregar: timer, nivel actual, score en tiempo real
- Transiciones suaves entre rondas
- **Por qué**: El juego es la experiencia core

### 4.2 Consolidación post-juego
- Modal de consolidación con campos de práctica deliberada
- Auto-sugerir micro-error basado en el juego
- Score + feedback inmediato
- **Por qué**: Ericsson dice que el feedback inmediato es clave

### 4.3 Historial de juego
- Mini-timeline de las últimas 5 sesiones
- Tendencia de nivel (sube/baja)
- **Por qué**: Motivación por progreso visible

---

## Fase 5: UX y Micro-interacciones (Prioridad BAJA)

### 5.1 Loading States
- Skeleton loaders para cada sección
- Spinner consistente
- **Por qué**: Percepción de velocidad

### 5.2 Empty States ilustrados
- Ilustraciones SVG simples para cada estado vacío
- CTAs claros
- **Por qué**: Guía al usuario nuevo

### 5.3 Animaciones
- Page transitions (slide/fade)
- Card hover effects (ya hay algunos)
- Number counters animados
- **Por qué**: Sensación de premium

### 5.4 Responsive Design
- Mobile-first para todo
- Touch targets mínimos 44px
- Bottom nav en mobile
- **Por qué**: Muchos usuarios en celular

---

## Fase 6: Calidad (Prioridad BAJA)

### 6.1 Error Boundaries
- Por sección: Dashboard, Games, Settings
- Fallback UI amigable
- **Por qué**: No pantalla blanca

### 6.2 Accessibility
- Keyboard navigation completa
- Screen reader labels
- Focus management
- **Por qué**: Inclusión

### 6.3 Performance
- React.lazy para juegos
- Virtual scrolling para timeline
- useMemo donde aplica
- **Por qué**: Mantener 60fps

---

## Orden de Ejecución Recomendado

| # | Fase | Esfuerzo | Impacto | Archivos |
|---|------|----------|---------|----------|
| 1 | 1.1 Router | M | ALTO | App.jsx, package.json |
| 2 | 1.2 Layout/Nav | M | ALTO | Nuevo: Layout.jsx, Nav.jsx |
| 3 | 1.3 App.jsx split | B | ALTO | App.jsx, pages/* |
| 4 | 2.1 Hero Stats | B | ALTO | Nuevo: HeroStats.jsx |
| 5 | 2.3 Quick Actions | B | MEDIO | Dashboard sections |
| 6 | 3.1 Design System | M | MEDIO | components/ui/* |
| 7 | 3.2 SkillCard refactor | B | MEDIO | SkillCard.jsx |
| 8 | 4.1 GameShell | M | MEDIO | GameShell.jsx, games |
| 9 | 5.1 Loading States | B | BAJO | Skeletons |
| 10 | 5.2 Empty States | B | BAJO | SVGs |

**M** = Medio (2-4h), **B** = Bajo (1-2h)

---

## Estimación Total

- **Fase 1**: ~6-8 horas (router + layout + split)
- **Fase 2**: ~3-4 horas (dashboard + hero)
- **Fase 3**: ~4-5 horas (design system + refactor)
- **Fase 4**: ~4-5 horas (juegos + consolidación)
- **Fase 5**: ~3-4 horas (UX + animaciones)
- **Fase 6**: ~2-3 horas (calidad)

**Total: ~22-29 horas de trabajo**

---

## Dependencias

- `react-router-dom` (nueva)
- No se necesitan librerías adicionales de UI (Tailwind cubre todo)
- Zustand se mantiene (funciona bien)

---

## Riesgos

1. **Router rompe existente**: Hacer migración incremental, no big bang
2. **Juegos se rompen**: Testear cada juego después del refactor
3. **Mobile responsive**: Revisar cada componente en viewport móvil
4. **Performance**: Medir antes/después con React DevTools

---

## Criterios de Éxito

- [ ] Navegación funcional con back/forward
- [ ] Dashboard carga en < 2s
- [ ] Todos los juegos funcionan
- [ ] Mobile responsive en iPhone SE → Desktop
- [ ] 0 errores en consola
- [ ] Tests pasan

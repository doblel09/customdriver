# 🤖 Custom Driver - Framework para Automatización y Scraping

Proyecto flexible de automatización web y scraping que soporta múltiples drivers configurables con capacidades anti-detección. Diseñado para pruebas E2E, automatización de tareas web y scraping avanzado.

## ✨ Características Principales

- **Múltiples Drivers Configurables**: SeleniumBase (CDP), Brave Browser, Undetectable Chrome y Incogniton
- **Anti-Detección**: Drivers optimizados para evitar detección de bots
- **Comportamiento Humano**: Delays aleatorios, escritura gradual y movimientos de mouse naturales
- **Emulación Móvil**: Soporte para eventos táctiles y comportamiento móvil
- **Gestión de Proxies**: Soporte SOCKS5 integrado
- **API Consistente**: Misma interfaz independientemente del driver subyacente

## 📦 Requisitos

```bash
pip install seleniumbase selenium incogniton
```

### Requisitos Adicionales

- **Brave Browser**: Instalación local requerida para SeleniumBase con CDP
- **ChromeDriver**: Necesario para Undetectable Chrome
- **Incogniton**: Cliente de Incogniton activo con perfiles configurados
- **Undetectable**: Cliente de Undetectable activo con perfiles configurados

## 🚀 Uso Rápido

### Inicialización Básica

```python
from driver import CustomDriver

# SeleniumBase con Brave (CDP)
driver = CustomDriver(
    browser_options={"type": "seleniumbase"}
)

# Undetectable
driver = CustomDriver(
    browser_options={"type": "undetectable", "mobile_emulation": False}
)

# Incogniton (con selección de perfil)
driver = CustomDriver(
    browser_options={"type": "incogniton", "mobile_emulation": False}
)
```

### Con Proxy

```python
driver = CustomDriver(
    proxy="192.168.1.1:1080",  # Formato IP:Puerto
    browser_options={"type": "seleniumbase"}
)
```

### Configuración de Velocidad

```python
driver = CustomDriver(
    type_speed=1.0,      # Velocidad de escritura (multiplicador)
    wait_speed=0.5,      # Tiempo adicional entre acciones
    typeSlowly=True,     # Escribir carácter por carácter
    browser_options={"type": "seleniumbase", "mobile_emulation": False}
)
```

## 📖 Métodos Principales

### Navegación

```python
# Navegar a URL
driver.get("https://example.com")

# Obtener URL actual
current_url = driver.get_current_url()

# Cambiar a nueva pestaña
driver.change_to_new_tab()
```

### Interacción con Elementos

```python
# Click en elemento
driver.click("#submit-button")
driver.click("//button[text()='Submit']", scroll=True)

# Escribir texto
driver.type("#email", "user@example.com")
driver.type("#password", "secret123", clickOutside=False)

# Seleccionar opción en dropdown
driver.select_option_by_value("#country", "US")
```

### Esperas y Verificaciones

```python
# Esperar elemento clickeable
element = driver.wait_for_clickable_element("#button", timeout=20)

# Esperar elemento visible
element = driver.wait_for_visible_element(".popup")

# Obtener elemento
element = driver.getElement("#content")

# Esperar que elemento desaparezca
driver.wait_for_element_to_disappear(".loading-spinner")
```

### Scroll

```python
# Scroll a elemento
element = driver.scroll_to_element("#footer")

# Scroll antes de interactuar
driver.click("#button", scroll=True)
driver.type("#input", "text", scroll=True)
```

## 🎯 Drivers Disponibles

### 1. SeleniumBase (CDP) con Brave

**Ventajas:**
- Integración directa con Chrome DevTools Protocol (CDP)
- Alta velocidad de ejecución
- Excelente para pruebas E2E

**Configuración:**
```python
driver = CustomDriver(
    proxy="socks5h://proxy.example.com:1080",
    browser_options={
        "type": "seleniumbase"
    }
)
```

### 2. Undetectable

**Ventajas:**
- Anti-detección avanzada
- Gestión de perfiles persistentes
- Ideal para scraping de sitios protegidos

**Configuración:**
```python
driver = CustomDriver(
    browser_options={"type": "undetectable"}
)
```

**Funcionalidades:**
- Selección interactiva de perfiles
- Conexión a perfiles activos
- Gestión automática de puerto de depuración

### 3. Incogniton

**Ventajas:**
- Gestión profesional de fingerprints
- Múltiples perfiles con identidades únicas
- Perfecto para tareas que requieren múltiples sesiones

**Configuración:**
```python
driver = CustomDriver(
    browser_options={"type": "incogniton"}
)
```

**Funcionalidades:**
- Lista interactiva de perfiles disponibles
- Lanzamiento automático de Selenium
- Integración con API de Incogniton

## 🎨 Ejemplos Avanzados

### Scraping con Comportamiento Humano

```python
driver = CustomDriver(
    type_speed=0.8,
    wait_speed=1.0,
    typeSlowly=True,
    browser_options={"type": "undetectable"}
)

driver.get("https://example.com/login")

# Escritura natural con delays
driver.type("#username", "myuser@email.com")
driver.type("#password", "mypassword")

driver.click("#login-button")
driver.wait_for_visible_element(".dashboard")
```

### Emulación Móvil

```python
driver = CustomDriver(
    browser_options={
        "type": "undetectable",
        "mobile_emulation": True
    }
)

driver.get("https://mobile.example.com")

# Usa eventos táctiles en lugar de clicks
driver.click("#menu-icon")  # Touch event
driver.type("#search", "query")
```

### Automatización con Múltiples Pestañas

```python
driver.get("https://example.com")
driver.click("a[target='_blank']")  # Abre nueva pestaña

# Cambiar a nueva pestaña
driver.change_to_new_tab()

# Trabajar en nueva pestaña
driver.wait_for_visible_element("#content")
current_url = driver.get_current_url()
```

### Formularios Complejos

```python
# Formulario con múltiples campos
driver.type("#first-name", "John", scroll=True)
driver.type("#last-name", "Doe")
driver.type("#email", "john@example.com")

# Dropdown
driver.select_option_by_value("#country", "US")

# Radio button
driver.click("input[value='male']", radio=True)

# Scroll y submit
driver.scroll_to_element("#submit-button")
driver.click("#submit-button")

# Verificar envío
driver.wait_for_visible_element(".success-message")
```

## 🔧 Estructura del Proyecto

```
auth/
├── driver.py                    # Clase principal CustomDriver
├── drivers/
│   ├── incogniton_driver.py    # Driver de Incogniton
│   └── undetectable.py         # Driver Undetectable Chrome
└── readme.md                    # Este archivo
```

## ⚙️ Configuración Detallada

### Parámetros de CustomDriver

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `proxy` | str | None | Proxy en formato IP:Puerto |
| `browser_options` | dict | {"type": "seleniumbase"} | Configuración del browser |
| `type_speed` | float | 0.0 | Multiplicador de velocidad de escritura |
| `wait_speed` | float | 0.0 | Tiempo adicional entre acciones |
| `typeSlowly` | bool | False | Escribir carácter por carácter |

### Opciones de Browser

```python
browser_options = {
    "type": "seleniumbase" | "undetectable" | "incogniton",
    "mobile_emulation": True | False
}
```

## 🛠️ Utilidades

### Pausar Ejecución

```python
driver.pause()  # Pausa hasta presionar Enter
```

### Cerrar Driver

```python
driver.quit()
```

## 🔍 Selectores Soportados

El framework detecta automáticamente el tipo de selector:

```python
# CSS Selector
driver.click("#myId")
driver.click(".myClass")
driver.click("button[type='submit']")

# XPath (detectado por //)
driver.click("//button[text()='Click Me']")
driver.click("//div[@class='container']//a")
```

## 🎭 Anti-Detección

El framework implementa múltiples técnicas anti-detección:

- ✅ Delays aleatorios entre acciones
- ✅ Escritura gradual con velocidad variable
- ✅ Movimientos de mouse naturales
- ✅ Emulación de eventos táctiles
- ✅ Drivers con fingerprints únicos (Incogniton)
- ✅ Chrome sin detección (Undetectable)

## 📝 Notas Importantes

1. **CDP Mode**: Algunos métodos tienen optimizaciones especiales cuando se usa SeleniumBase con CDP
2. **Mobile Emulation**: Cambia el comportamiento de `click()` para usar eventos táctiles
3. **Reintentos Automáticos**: El método `click()` incluye lógica de reintentos automáticos
4. **Selectores**: XPath se detecta automáticamente si comienza con `//`

## 🤝 Contribuciones

Este es un proyecto de uso interno. Para mejoras o sugerencias, contactame.

## 📄 Licencia

Uso interno - Todos los derechos reservados.

---

**Última actualización**: Diciembre 2025

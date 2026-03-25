# Elvira - Voz para Claude Code

Sistema de texto-a-voz (TTS) para Claude Code en VSCode. Usa la voz neural **Elvira** de Microsoft Edge TTS para leer en voz alta las respuestas de Claude. Combinado con el dictado de Windows, permite mantener conversaciones por voz con Claude Code.

---

## Resumen

- **Entrada de voz**: Dictado nativo de Windows (`Win + H`)
- **Salida de voz**: Microsoft Edge TTS (voz `es-ES-ElviraNeural`, neural, gratuita)
- **Toggle**: `Ctrl+Shift+H` activa/desactiva la voz
- **Filtrado inteligente**: Solo lee texto conversacional, ignora código, comandos, paths, tablas, markdown

---

## Archivos

| Archivo | Ubicación real | Descripción |
|---------|---------------|-------------|
| `tts-response.py` | `~/.claude/hooks/tts-response.py` | Script principal: filtra markdown, genera audio con edge-tts, reproduce con PowerShell MediaPlayer |
| `tts-response.sh` | `~/.claude/hooks/tts-response.sh` | Wrapper bash que pasa stdin al script Python |
| `tts-enabled` | `~/.claude/hooks/tts-enabled` | Archivo toggle: si existe = voz ON, si no existe = voz OFF |

---

## Instalación desde cero

### 1. Instalar edge-tts (Python)

```bash
pip install edge-tts
```

No necesita API key ni cuenta. Usa las voces neurales de Microsoft Edge, las mismas de Azure TTS, gratis.

### 2. Copiar los scripts a ~/.claude/hooks/

```bash
mkdir -p ~/.claude/hooks
cp tts-response.py ~/.claude/hooks/
cp tts-response.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/tts-response.sh
```

### 3. Configurar el hook en Claude Code

Editar `~/.claude/settings.json` y añadir la sección `hooks`:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash C:/Users/manue/.claude/hooks/tts-response.sh",
            "timeout": 60
          }
        ]
      }
    ]
  }
}
```

El hook se dispara cada vez que Claude termina de responder (`Stop` event). Pasa el JSON de la respuesta por stdin al script.

### 4. Configurar el atajo de teclado para toggle

Crear/editar `.vscode/tasks.json` en tu proyecto:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Toggle Claude TTS",
      "type": "process",
      "command": "powershell",
      "args": [
        "-ExecutionPolicy", "Bypass", "-Command",
        "$f = \"$env:USERPROFILE\\.claude\\hooks\\tts-enabled\"; if (Test-Path $f) { Remove-Item $f; [System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms') | Out-Null; [System.Windows.Forms.MessageBox]::Show('Voz DESACTIVADA','Elvira',[System.Windows.Forms.MessageBoxButtons]::OK,[System.Windows.Forms.MessageBoxIcon]::Information) | Out-Null } else { 'on' | Set-Content $f; [System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms') | Out-Null; [System.Windows.Forms.MessageBox]::Show('Voz ACTIVADA','Elvira',[System.Windows.Forms.MessageBoxButtons]::OK,[System.Windows.Forms.MessageBoxIcon]::Information) | Out-Null }"
      ],
      "problemMatcher": [],
      "presentation": {
        "reveal": "silent",
        "panel": "shared",
        "showReuseMessage": false,
        "close": true
      }
    }
  ]
}
```

Editar `~/.config/Code/User/keybindings.json` (o en Windows: `%APPDATA%/Code/User/keybindings.json`):

```json
[
  {
    "key": "ctrl+shift+h",
    "command": "workbench.action.tasks.runTask",
    "args": "Toggle Claude TTS"
  }
]
```

### 5. Activar dictado de voz de Windows (entrada)

No requiere instalación. Es nativo de Windows 10/11:

- **Win + H** abre la barra de dictado
- Funciona en cualquier campo de texto, incluido el chat de Claude Code
- Haz click en el campo de texto de Claude Code, pulsa Win+H, habla
- Reconocimiento en español automático (usa el idioma del sistema)
- Puntuación automática y bastante preciso

---

## Cómo funciona

### Flujo completo de una interacción por voz

1. Pulsas **Win+H** y hablas tu pregunta al campo de texto de Claude Code
2. Windows transcribe tu voz a texto
3. Pulsas Enter para enviar
4. Claude Code procesa y responde (texto en pantalla)
5. Al terminar, se dispara el hook `Stop`
6. `tts-response.sh` recibe el JSON con la respuesta por stdin
7. `tts-response.py` filtra el markdown y extrae solo texto conversacional
8. `edge-tts` genera un MP3 con la voz de Elvira (neural)
9. PowerShell `MediaPlayer` reproduce el MP3
10. Escuchas la respuesta de Claude en voz alta

### Filtrado de texto

El script filtra automáticamente:
- Bloques de codigo (``` ... ```)
- Inline code (`backticks`)
- Lineas que empiezan con $, #, > (comandos)
- Imports
- Tablas markdown (|...|...|)
- Paths de Windows y Unix
- JSON/objetos ({...})
- Links markdown [texto](url)
- Listas de items con backticks
- Co-Authored-By
- Separadores (---, ===)
- Simbolos unicode que se narran mal (R registrada, TM, flechas, bullets, comillas tipograficas)
- Tags HTML

Y conserva solo el texto conversacional limpio.

### Voces disponibles en espanol

```bash
python -m edge_tts --list-voices | grep "es-ES"
```

| Voz | Genero | Estilo |
|-----|--------|--------|
| es-ES-ElviraNeural | Mujer | Friendly, Positive (la que usamos) |
| es-ES-AlvaroNeural | Hombre | Friendly, Positive |
| es-ES-XimenaNeural | Mujer | Friendly, Positive |

Para cambiar la voz, edita `tts-response.py` linea del `--voice`.

### Ajustar velocidad

En `tts-response.py`, parametro `--rate`:
- `+15%` = un poco mas rapido (configuracion actual)
- `+30%` = bastante mas rapido
- `0%` o sin parametro = velocidad normal
- `-15%` = mas lento

---

## Activar y desactivar

- **Ctrl+Shift+H** = toggle con popup de confirmacion ("Voz ACTIVADA" / "Voz DESACTIVADA")
- Manual ON: `echo on > ~/.claude/hooks/tts-enabled`
- Manual OFF: `rm ~/.claude/hooks/tts-enabled`

---

## Problemas conocidos y soluciones

### Encoding: dice "sambolos" en vez de "simbolos"
- Causa: Python en Windows usa cp1252 por defecto en stdin
- Solucion: el script usa `sys.stdin.buffer.read().decode('utf-8')` para forzar UTF-8
- El texto se escribe a archivo temporal con encoding UTF-8 explicito
- edge-tts lee del archivo temporal, no de argumentos de linea de comandos

### Helena suena robotica
- Helena es la voz SAPI5 clasica de Windows (no neural)
- Solucion: usar edge-tts con voces neurales (ElviraNeural)
- edge-tts es gratuito, no requiere API key

### WSL intercepta los comandos bash
- En VSCode si tienes WSL instalado, `type: "shell"` en tasks puede usar WSL
- Solucion: usar `type: "process"` con `powershell` en vez de `bash`

### El hook no se dispara
- Verificar que `settings.json` tiene la seccion `hooks.Stop`
- Reiniciar VSCode despues de modificar settings.json
- El timeout del hook es 60 segundos (suficiente para respuestas largas)

---

## Requisitos

- Windows 10/11
- Python 3.8+
- pip install edge-tts
- VSCode con Claude Code
- Conexion a internet (edge-tts genera el audio online via API de Edge)

---

## Alternativas descartadas

- **Helena Desktop (SAPI5)**: voz robotica, mala calidad
- **Laura/Pablo (OneCore)**: mejores que Helena pero no accesibles via SAPI5, necesitan API UWP
- **Dalia (Windows Neural)**: necesita descargar voces especificas, no se encontro en este sistema
- **Azure TTS API**: de pago, innecesario teniendo edge-tts gratis
- **VS Code Speech extension**: solo transcribe (entrada), no lee respuestas (salida)

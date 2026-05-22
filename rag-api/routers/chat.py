from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

HTML_CHAT_INTERFACE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Café Aurora - Agente API</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --color-bg: #0f0d0c;
            --color-surface: #1a1614;
            --color-border: #2c2420;
            --color-primary: #d97706;
            --color-primary-hover: #b45309;
            --color-text: #fafaf9;
            --color-text-muted: #a8a29e;
            --color-chat-agent: #221c19;
            --color-chat-user: #3c3029;
            --color-tool-bg: #1e1815;
            --color-accent-green: #10b981;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Outfit', sans-serif;
            background-color: var(--color-bg);
            color: var(--color-text);
            display: flex;
            flex-direction: column;
            height: 100vh;
            overflow: hidden;
        }

        /* Cabecera */
        header {
            background-color: var(--color-surface);
            border-bottom: 1px solid var(--color-border);
            padding: 16px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 10;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .brand-logo {
            font-size: 24px;
            font-weight: 700;
            background: linear-gradient(135deg, #fbbf24 0%, #d97706 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 0.5px;
        }

        .badge-status {
            background-color: rgba(16, 185, 129, 0.1);
            color: var(--color-accent-green);
            border: 1px solid rgba(16, 185, 129, 0.2);
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background-color: var(--color-accent-green);
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 8px var(--color-accent-green);
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { opacity: 0.4; }
            50% { opacity: 1; }
            100% { opacity: 0.4; }
        }

        /* Contenedor Principal */
        main {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            width: 100%;
            max-width: 900px;
            margin: 0 auto;
            position: relative;
            height: calc(100vh - 65px);
        }

        /* Área de Mensajes */
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 24px;
            display: flex;
            flex-direction: column;
            gap: 20px;
            scroll-behavior: smooth;
        }

        /* Personalización de scrollbar */
        .chat-container::-webkit-scrollbar {
            width: 6px;
        }
        .chat-container::-webkit-scrollbar-track {
            background: transparent;
        }
        .chat-container::-webkit-scrollbar-thumb {
            background-color: var(--color-border);
            border-radius: 3px;
        }

        .welcome-view {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            height: 100%;
            max-width: 500px;
            margin: auto;
            gap: 16px;
        }

        .welcome-title {
            font-size: 32px;
            font-weight: 600;
            color: var(--color-text);
        }

        .welcome-subtitle {
            font-size: 15px;
            color: var(--color-text-muted);
            line-height: 1.5;
        }

        .suggestions {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            width: 100%;
            margin-top: 12px;
        }

        .suggestion-btn {
            background-color: var(--color-surface);
            border: 1px solid var(--color-border);
            padding: 14px;
            border-radius: 12px;
            text-align: left;
            cursor: pointer;
            transition: all 0.2s ease;
            font-family: inherit;
            color: var(--color-text);
            font-size: 14px;
        }

        .suggestion-btn:hover {
            border-color: var(--color-primary);
            background-color: #221c19;
            transform: translateY(-2px);
        }

        /* Mensajes */
        .message {
            display: flex;
            flex-direction: column;
            max-width: 85%;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .message.user {
            align-self: flex-end;
        }

        .message.agent {
            align-self: flex-start;
        }

        .message-bubble {
            padding: 14px 18px;
            border-radius: 16px;
            font-size: 15px;
            line-height: 1.5;
            word-wrap: break-word;
        }

        .user .message-bubble {
            background-color: var(--color-chat-user);
            color: var(--color-text);
            border-bottom-right-radius: 4px;
            border: 1px solid var(--color-border);
        }

        .agent .message-bubble {
            background-color: var(--color-chat-agent);
            color: var(--color-text);
            border-bottom-left-radius: 4px;
            border: 1px solid var(--color-border);
        }

        .message-meta {
            font-size: 11px;
            color: var(--color-text-muted);
            margin-top: 4px;
            display: flex;
            gap: 8px;
            padding: 0 4px;
        }

        .user .message-meta {
            align-self: flex-end;
        }

        /* Desglose de herramientas / Ruta de Razonamiento */
        .reasoning-container {
            margin-top: 8px;
            border: 1px solid var(--color-border);
            border-radius: 10px;
            background-color: var(--color-tool-bg);
            overflow: hidden;
        }

        .reasoning-header {
            padding: 8px 12px;
            font-size: 12px;
            font-weight: 500;
            color: var(--color-primary);
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: rgba(217, 119, 6, 0.05);
            user-select: none;
        }

        .reasoning-header::after {
            content: '▼';
            font-size: 8px;
            transition: transform 0.2s ease;
        }

        .reasoning-container.expanded .reasoning-header::after {
            transform: rotate(180deg);
        }

        .reasoning-steps {
            display: none;
            padding: 12px;
            border-top: 1px solid var(--color-border);
            font-size: 13px;
            flex-direction: column;
            gap: 12px;
        }

        .reasoning-container.expanded .reasoning-steps {
            display: flex;
        }

        .step-item {
            border-left: 2px solid var(--color-primary);
            padding-left: 10px;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        .step-title {
            font-weight: 600;
            color: var(--color-text);
            font-size: 12px;
            display: flex;
            justify-content: space-between;
        }

        .step-args {
            font-family: monospace;
            font-size: 11px;
            color: var(--color-text-muted);
            background-color: rgba(0,0,0,0.2);
            padding: 4px 6px;
            border-radius: 4px;
        }

        .step-result {
            font-size: 12px;
            color: #d1c7bd;
        }

        /* Indicador de Carga (Agente Pensando) */
        .loading-bubble {
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 12px 18px;
            background-color: var(--color-chat-agent);
            border: 1px solid var(--color-border);
            border-radius: 16px;
            border-bottom-left-radius: 4px;
            align-self: flex-start;
            animation: fadeIn 0.2s ease;
        }

        .dot {
            width: 8px;
            height: 8px;
            background-color: var(--color-primary);
            border-radius: 50%;
            animation: bounce 1.4s infinite ease-in-out both;
        }

        .dot:nth-child(1) { animation-delay: -0.32s; }
        .dot:nth-child(2) { animation-delay: -0.16s; }

        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1.0); }
        }

        /* Barra de Entrada de Texto */
        .input-area {
            padding: 20px 24px;
            background-color: var(--color-bg);
            border-top: 1px solid var(--color-border);
            display: flex;
            gap: 12px;
            align-items: center;
            z-index: 10;
        }

        .input-wrapper {
            position: relative;
            flex: 1;
            display: flex;
            align-items: center;
        }

        .chat-input {
            width: 100%;
            background-color: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: 24px;
            padding: 14px 20px;
            padding-right: 50px;
            font-family: inherit;
            font-size: 15px;
            color: var(--color-text);
            outline: none;
            transition: border-color 0.2s ease;
        }

        .chat-input::placeholder {
            color: var(--color-text-muted);
        }

        .chat-input:focus {
            border-color: var(--color-primary);
        }

        .send-btn {
            position: absolute;
            right: 8px;
            background-color: var(--color-primary);
            color: #000;
            border: none;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background-color 0.2s ease, transform 0.1s ease;
        }

        .send-btn:hover {
            background-color: var(--color-primary-hover);
        }

        .send-btn:active {
            transform: scale(0.95);
        }

        .send-btn svg {
            width: 16px;
            height: 16px;
            fill: #000;
            transform: translateX(1px);
        }
        
        .footer-note {
            text-align: center;
            font-size: 11px;
            color: var(--color-text-muted);
            margin-top: 6px;
            padding-bottom: 8px;
        }
    </style>
</head>
<body>
    <header>
        <div class="brand">
            <span class="brand-logo">Café Aurora</span>
            <span class="badge-status">
                <span class="status-dot"></span>
                Agente Activo
            </span>
        </div>
        <div style="font-size: 13px; color: var(--color-text-muted); font-weight: 500;">
            Semana 10 AI Bootcamp
        </div>
    </header>

    <main>
        <div class="chat-container" id="chatContainer">
            <!-- Vista de Bienvenida Inicial -->
            <div class="welcome-view" id="welcomeView">
                <div style="font-size: 40px;">☕</div>
                <h1 class="welcome-title">Café Aurora Agent</h1>
                <p class="welcome-subtitle">
                    Interactúe con el Agente Conversacional Inteligente para consultar el menú, calcular precios, verificar el estado de pedidos o conocer los horarios de nuestras sucursales.
                </p>
                <div class="suggestions">
                    <button class="suggestion-btn" onclick="sendSuggestion('¿Cuánto cuesta el latte de mazapán?')">
                        💰 Precio de Latte de Mazapán
                    </button>
                    <button class="suggestion-btn" onclick="sendSuggestion('¿Qué pedidos están en preparación?')">
                        📋 Pedidos en preparación
                    </button>
                    <button class="suggestion-btn" onclick="sendSuggestion('¿Cuánto cuestan 3 lattes de mazapán con el descuento de empleado?')">
                        🎁 3 Lattes con descuento
                    </button>
                    <button class="suggestion-btn" onclick="sendSuggestion('¿Cuáles son los horarios de la sucursal Roma Norte?')">
                        🕒 Horarios Roma Norte
                    </button>
                </div>
            </div>
        </div>

        <div>
            <div class="input-area">
                <div class="input-wrapper">
                    <input type="text" class="chat-input" id="chatInput" placeholder="Escriba su consulta aquí..." autofocus autocomplete="off">
                    <button class="send-btn" id="sendBtn" onclick="sendMessage()">
                        <svg viewBox="0 0 24 24">
                            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"></path>
                        </svg>
                    </button>
                </div>
            </div>
            <div class="footer-note">
                FastAPI + OpenAI gpt-4o-mini | Bucle de razonamiento local seguro
            </div>
        </div>
    </main>

    <script>
        const chatContainer = document.getElementById('chatContainer');
        const chatInput = document.getElementById('chatInput');
        const welcomeView = document.getElementById('welcomeView');

        // Escuchar tecla Enter
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });

        function sendSuggestion(text) {
            chatInput.value = text;
            sendMessage();
        }

        function toggleReasoning(element) {
            const container = element.parentElement;
            container.classList.toggle('expanded');
        }

        async function sendMessage() {
            const text = chatInput.value.trim();
            if (!text) return;

            // Ocultar vista de bienvenida si es el primer mensaje
            if (welcomeView) {
                welcomeView.style.display = 'none';
            }

            // Añadir mensaje del usuario
            appendMessage(text, 'user');
            chatInput.value = '';

            // Mostrar burbuja de carga del agente
            const loadingId = appendLoading();
            chatContainer.scrollTop = chatContainer.scrollHeight;

            try {
                const response = await fetch('/agent', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ question: text })
                });

                // Remover burbuja de carga
                removeLoading(loadingId);

                if (response.status === 200) {
                    const data = await response.json();
                    appendMessage(data.answer, 'agent', data);
                } else if (response.status === 422) {
                    appendMessage('⚠️ Error: La consulta debe tener al menos 3 caracteres.', 'agent');
                } else {
                    const errText = await response.text();
                    appendMessage(`⚠️ Error en la llamada al servidor: ${errText}`, 'agent');
                }
            } catch (err) {
                removeLoading(loadingId);
                appendMessage('⚠️ Error de conexión: No se pudo comunicar con el servidor.', 'agent');
            }

            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function appendMessage(text, sender, data = null) {
            const msgDiv = document.createElement('div');
            msgDiv.className = `message ${sender}`;

            const bubble = document.createElement('div');
            bubble.className = 'message-bubble';
            bubble.innerText = text;
            msgDiv.appendChild(bubble);

            const meta = document.createElement('div');
            meta.className = 'message-meta';
            const now = new Date();
            const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            
            if (sender === 'agent' && data) {
                meta.innerText = `${timeStr} | ${data.iterations} iteraciones | ${data.elapsed_seconds.toFixed(2)}s`;
            } else {
                meta.innerText = timeStr;
            }
            msgDiv.appendChild(meta);

            // Si hay datos del agente con herramientas utilizadas, añadir el desglose
            if (sender === 'agent' && data && data.steps && data.steps.length > 0) {
                const reasoning = document.createElement('div');
                reasoning.className = 'reasoning-container';
                
                const header = document.createElement('div');
                header.className = 'reasoning-header';
                header.innerText = `Ruta de Razonamiento (${data.steps.length} pasos)`;
                header.onclick = () => toggleReasoning(header);
                reasoning.appendChild(header);

                const stepsDiv = document.createElement('div');
                stepsDiv.className = 'reasoning-steps';

                data.steps.forEach(step => {
                    const stepItem = document.createElement('div');
                    stepItem.className = 'step-item';

                    const title = document.createElement('div');
                    title.className = 'step-title';
                    
                    const stepName = document.createElement('span');
                    stepName.innerHTML = `Llamada a <strong>${step.tool}</strong> (Iteración ${step.iteration})`;
                    title.appendChild(stepName);

                    const timeInfo = document.createElement('span');
                    timeInfo.style.color = 'var(--color-text-muted)';
                    timeInfo.style.fontSize = '10px';
                    timeInfo.innerText = `${step.elapsed_seconds.toFixed(4)}s`;
                    title.appendChild(timeInfo);
                    
                    stepItem.appendChild(title);

                    const args = document.createElement('div');
                    args.className = 'step-args';
                    args.innerText = JSON.stringify(step.arguments);
                    stepItem.appendChild(args);

                    const res = document.createElement('div');
                    res.className = 'step-result';
                    res.innerHTML = `<strong>Resultado:</strong> ${step.result_preview}`;
                    stepItem.appendChild(res);

                    stepsDiv.appendChild(stepItem);
                });

                reasoning.appendChild(stepsDiv);
                msgDiv.appendChild(reasoning);
            }

            chatContainer.appendChild(msgDiv);
        }

        function appendLoading() {
            const id = 'loading_' + Math.random().toString(36).substr(2, 9);
            const loadDiv = document.createElement('div');
            loadDiv.className = 'loading-bubble';
            loadDiv.id = id;

            for (let i = 0; i < 3; i++) {
                const dot = document.createElement('div');
                dot.className = 'dot';
                loadDiv.appendChild(dot);
            }

            chatContainer.appendChild(loadDiv);
            return id;
        }

        function removeLoading(id) {
            const el = document.getElementById(id);
            if (el) el.remove();
        }
    </script>
</body>
</html>
"""


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def render_chat_page():
    """Sirve la interfaz web de chat interactiva en la raíz de la API."""
    return HTML_CHAT_INTERFACE

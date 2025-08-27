from langchain_core.messages import AIMessage, ToolMessage

def executar_analise(pergunta: str, graph):
    """Executa o agente e imprime o stream de respostas de forma legível."""
    inputs = {"messages": [("user", pergunta)]}
    print(f"\n--- Pergunta: {pergunta} ---")
    
    # Itera sobre cada passo do grafo para uma impressão mais detalhada
    for step_output in graph.stream(inputs):
        for node_name, state_update in step_output.items():
            print(f"--- Nó: {node_name} ---")
            
            # Itera sobre as mensagens no estado atual
            for message in state_update.get("messages", []):
                if isinstance(message, AIMessage):
                    print(f"  🤖 Resposta do Agente:")
                    if message.content:
                        print(f"    - Conteúdo: {message.content}")
                    if message.tool_calls:
                        print("    - Chamada de Ferramenta:")
                        for tool_call in message.tool_calls:
                            print(f"      -> Nome da Ferramenta: {tool_call['name']}")
                            print(f"      -> Argumentos: {tool_call['args']}")
                
                elif isinstance(message, ToolMessage):
                    print(f"  🛠️ Execução de Ferramenta:")
                    print(f"    - Ferramenta: {message.name}")
                    print(f"    - Status: {message.status.upper()}")
                    print(f"    - Resultado:")
                    # Impressão do resultado formatado
                    resultado = message.content
                    if resultado.startswith("Erro"):
                        print(f"      ❌ {resultado}")
                    else:
                        for linha in resultado.split('\n'):
                            print(f"      ✅ {linha}")
                    
            print("-" * 40)
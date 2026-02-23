import os
import sys
from pydantic import SecretStr

def get_llm():
    provider = os.getenv("LLM_PROVIDER", "azure").lower()
    temperature = float(os.getenv("LLM_TEMPERATURE", "0.0"))

    if provider == "azure":
        from langchain_openai import AzureChatOpenAI
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        
        if not all([api_key, endpoint, deployment_name]):
            print("エラー: Azure OpenAIの環境変数が設定されていません。.envファイルを確認してください。")
            sys.exit(1)

        return AzureChatOpenAI(
            azure_endpoint=endpoint,
            api_key=SecretStr(api_key),
            api_version=api_version,
            azure_deployment=deployment_name,
            temperature=temperature
        )
    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-4o")
        
        if not api_key:
            print("エラー: OpenAI APIの環境変数が設定されていません。.envファイルを確認してください。")
            sys.exit(1)
            
        return ChatOpenAI(
            api_key=SecretStr(api_key),
            model=model_name,
            temperature=temperature
        )
    else:
        print(f"エラー: サポートされていないLLMプロバイダーです: {provider}")
        sys.exit(1)

import os
import sys
import asyncio
import argparse
from dotenv import load_dotenv
from llm_factory import get_llm
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

async def run_agent(args, source_content, api_content):

    # MCPクライアントの生成
    client = MultiServerMCPClient(
        {
            "playwright": {
                "transport": "http",
                "url": "http://host.docker.internal:9223/mcp"
            }
        }
    )
    
    # エージェントのメイン処理ではMCPクライアントのsessionを維持する
    # そうしないと、Playwrightで「ブラウザでの一連の操作」を扱えない
    async with client.session("playwright") as session:

        # MCPクライアントのsessionからMCPで定義されているtoolを取得します
        # langchainではMCPサーバをToolと同様に利用することができます
        tools = await load_mcp_tools(session)

        llm = get_llm()
        
        resource_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resource")
        with open(os.path.join(resource_dir, "step1_system_prompt.md"), "r", encoding="utf-8") as f:
            system_prompt_text = f.read()
        with open(os.path.join(resource_dir, "step1_human_prompt.md"), "r", encoding="utf-8") as f:
            human_prompt_text = f.read()

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt_text),
            ("placeholder", "{chat_history}"),
            ("human", human_prompt_text),
            ("placeholder", "{agent_scratchpad}"),
        ])


        # 実行
        agent = create_agent(model=llm, tools=tools, system_prompt=system_prompt_text)
        chain = prompt | agent
        
        query = "既存システムの画面を解釈し、新システムのソースとAPI仕様を考慮したE2Eテスト仕様書を作成してください。"
        
        result = await chain.ainvoke({
            "existing_url": args.existing_url,
            "source_code": source_content,
            "api_spec": api_content,
            "input": query
        })

        # 最後の"Message"を取得
        return result["messages"][-1].text

def main():
    parser = argparse.ArgumentParser(description="Auto E2E Test Tool - Step 1: Generate Test Specification")
    parser.add_argument("source_file", help="Path to the screen source code (e.g., HTML, TSX, Vue)")
    parser.add_argument("api_spec_file", help="Path to the API specification file (JSON)")
    parser.add_argument("--existing-url", required=True, help="URL of the existing system's screen to analyze")
    parser.add_argument("--output", default="テスト仕様書.md", help="Output Markdown file name")
    
    args = parser.parse_args()
    
    load_dotenv()
    

        
    try:
        with open(args.source_file, "r", encoding="utf-8") as f:
            source_content = f.read()
    except Exception as e:
        print(f"画面ソースコードの読み込みに失敗しました: {e}")
        sys.exit(1)
        
    try:
        with open(args.api_spec_file, "r", encoding="utf-8") as f:
            api_content = f.read()
    except Exception as e:
        print(f"API定義書の読み込みに失敗しました: {e}")
        sys.exit(1)
        
    print(f"[{args.source_file}] と [{args.api_spec_file}] を読み込み、 URL: [{args.existing_url}] を解析してテスト仕様書を生成中...")

    try:
        output_content = asyncio.run(run_agent(
            args, source_content, api_content
        ))
        
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_content)
        print(f"テスト仕様書を [{args.output}] に書き出しました。")
    except Exception as e:
        print(f"処理中にエラーが発生しました: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

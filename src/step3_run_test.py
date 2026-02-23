import os
import sys
import argparse
import subprocess
from dotenv import load_dotenv
from llm_factory import get_llm
from langchain_core.prompts import ChatPromptTemplate

def main():
    parser = argparse.ArgumentParser(description="Auto E2E Test Tool - Step 3: Run Test Code")
    parser.add_argument("test_file", help="Path to the Test Code (TypeScript)")
    parser.add_argument("--output", default="テスト結果.md", help="Output Test Result Markdown file")
    
    args = parser.parse_args()
    
    load_dotenv()
    print(f"[{args.test_file}] を実行しています(npx playwright test)...")
    
    # Run playwright test using subprocess
    # Note: Requires playwright and typescript configuration in the project
    result = subprocess.run(["npx", "playwright", "test", args.test_file], capture_output=True, text=True)
    
    exit_code = result.returncode
    stdout = result.stdout
    stderr = result.stderr
    
    test_log = f"Exit Code: {exit_code}\n\nSTDOUT:\n{stdout}\n\nSTDERR:\n{stderr}"
    
    print(f"テストが完了しました。終了コード: {exit_code}。結果を分析してMarkdownを生成中...")

    llm = get_llm()
    
    resource_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resource")
    with open(os.path.join(resource_dir, "step3_system_prompt.md"), "r", encoding="utf-8") as f:
        system_prompt_text = f.read()
    with open(os.path.join(resource_dir, "step3_human_prompt.md"), "r", encoding="utf-8") as f:
        human_prompt_text = f.read()

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt_text),
        ("human", human_prompt_text)
    ])
    
    chain = prompt | llm
    
    response = chain.invoke({
        "test_log": test_log
    })
    
    try:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(response.content)
        print(f"テスト結果を [{args.output}] に書き出しました。")
    except Exception as e:
        print(f"出力ファイルの書き出しに失敗しました: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

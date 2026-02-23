import os
import sys
import argparse
from dotenv import load_dotenv
from llm_factory import get_llm
from langchain_core.prompts import ChatPromptTemplate

def main():
    parser = argparse.ArgumentParser(description="Auto E2E Test Tool - Step 4: Analyze Failure")
    parser.add_argument("source_file", help="Path to the screen source code (e.g., HTML, TSX, Vue)")
    parser.add_argument("test_result_file", help="Path to the Test Result (Markdown)")
    parser.add_argument("--output", default="修正方針.md", help="Output Failure Analysis Markdown file")
    
    args = parser.parse_args()
    
    load_dotenv()
    try:
        with open(args.source_file, "r", encoding="utf-8") as f:
            source_content = f.read()
    except Exception as e:
        print(f"画面ソースコードの読み込みに失敗しました: {e}")
        sys.exit(1)
        
    try:
        with open(args.test_result_file, "r", encoding="utf-8") as f:
            result_content = f.read()
    except Exception as e:
        print(f"テスト結果の読み込みに失敗しました: {e}")
        sys.exit(1)
        
    print(f"[{args.source_file}] と [{args.test_result_file}] を読み込みました。修正方針を生成中...")

    llm = get_llm()
    
    resource_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resource")
    with open(os.path.join(resource_dir, "step4_system_prompt.md"), "r", encoding="utf-8") as f:
        system_prompt_text = f.read()
    with open(os.path.join(resource_dir, "step4_human_prompt.md"), "r", encoding="utf-8") as f:
        human_prompt_text = f.read()

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt_text),
        ("human", human_prompt_text)
    ])
    
    chain = prompt | llm
    
    response = chain.invoke({
        "source_code": source_content,
        "test_result": result_content
    })
    
    try:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(response.content)
        print(f"修正方針を [{args.output}] に書き出しました。")
    except Exception as e:
        print(f"出力ファイルの書き出しに失敗しました: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

import os
import sys
import argparse
from dotenv import load_dotenv
from llm_factory import get_llm
from langchain_core.prompts import ChatPromptTemplate

def main():
    parser = argparse.ArgumentParser(description="Auto E2E Test Tool - Step 2: Generate Test Code")
    parser.add_argument("spec_file", help="Path to the Test Specification (Markdown)")
    parser.add_argument("--output", default="e2e.spec.ts", help="Output TypeScript file name")
    
    args = parser.parse_args()
    
    load_dotenv()
        
    try:
        with open(args.spec_file, "r", encoding="utf-8") as f:
            spec_content = f.read()
    except Exception as e:
        print(f"テスト仕様書の読み込みに失敗しました: {e}")
        sys.exit(1)
        
    print(f"[{args.spec_file}] を読み込みました。テストコードを生成中...")

    llm = get_llm()
    
    resource_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resource")
    with open(os.path.join(resource_dir, "step2_system_prompt.md"), "r", encoding="utf-8") as f:
        system_prompt_text = f.read()
    with open(os.path.join(resource_dir, "step2_human_prompt.md"), "r", encoding="utf-8") as f:
        human_prompt_text = f.read()

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt_text),
        ("human", human_prompt_text)
    ])
    
    chain = prompt | llm
    
    response = chain.invoke({
        "spec_content": spec_content
    })
    
    content = response.content
    if "```typescript" in content:
        content = content.split("```typescript")[1].split("```")[0].strip()
    elif "```ts" in content:
        content = content.split("```ts")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].strip()
        if content.startswith("ts") or content.startswith("typescript"):
            content = "\n".join(content.split("\n")[1:])
            
    try:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"テストコードを [{args.output}] に書き出しました。")
    except Exception as e:
        print(f"出力ファイルの書き出しに失敗しました: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

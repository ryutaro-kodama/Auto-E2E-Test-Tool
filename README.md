# Auto-E2E-Test-Tool

LLM + Playwright MCP の構成で、自動でE2Eテストを作成するツールです。

## 前提
- LLM APIは各自契約したものを使用してください。現在は"OpenAI API", "Azure OpenAI"に対応しています
    - .env内で使用するLLMプロバイダーを指定してください。また、必要な変数も定義してください
- ホスト側環境で Playwright MCP を使用できるようにしておいてください
    - devcontainer内で Playwright MCP を操作することも可能ですが、どのようなブラウザ操作をしているか確認できないため、ホスト側の Playwright MCP を操作する構成にしました
    - 参考として、以下コマンドを実行した場合の動作確認は実施済みです
      ```sh
      $ npx playwright install-deps
      $ npx playwright install chrome
      ```
- 入力としてファイルを渡す場合は、.devcontainer.jsonを編集して、当該ファイル or ディレクトリをマウントさせて、コンテナ内から見えるようにしてください

## 使い方
### 0. Playwright MCP サーバーの起動

```sh
$ npx @playwright/mcp@latest --host 0.0.0.0 --port 9222 --allowed-hosts "*"
```

`--port`で指定するポートは、"step1_generate_spec.py"で指定するMCPサーバーのポートと同じポートにする必要があります  
devcontainer内からアクセスする場合、ホスト名がlocalhostでない場合がある（host.docker.internal等）ため、`--host 0.0.0.0`, `--allowed-hosts "*"`の指定が必要です

### 1. テスト仕様書の作成
以下3要素から、テスト仕様書を作成します
- 旧システム画面URL
- 新システムソースコード
- 新システムAPI仕様書

Usage: 
```sh
$ step1_generate_spec.py [-h] --existing-url EXISTING_URL [--output OUTPUT] source_file api_spec_file
```

`EXISTING_URL`は、ホスト側の Playwright MCP から見たURLを記載してください

### 2. E2Eテストコードの作成
以下要素から、テストコードを作成します
- 1.の仕様書

Usage:
```sh
$ step2_generate_code.py [-h] [--output OUTPUT] spec_file
```

### 3. E2Eテストコードの実行

2.で作成したテストコードを実行する
テスト対象プロジェクトでplaywrightが動くように設定しておく必要がある

```sh
$ npm init playwright@latest
```

`tests/`ディレクトリに2.で作成したテストを配置し、以下のコマンドで実行する
```sh
$ npx playwright test
```

`playwright-report/`ディレクトリ配下に`index.html`としてテストの実行結果レポートファイルが生成されるので、これを3.2で使用する

#### 4. ソースコード修正案の作成
テストコードとテストレポートをもとに、画面ソースコードの修正案を作成します

Usage:
```sh
$ step4_analyze_failure.py [-h] [--output OUTPUT] source_file test_result_file
```

## その他
`sample/`ディレクトリに、springとreactのサンプルプロジェクトを配置しています
`output/`ディレクトリに、そのサンプルプロジェクトへ本ツールを適用した際のアウトプットを保存しています

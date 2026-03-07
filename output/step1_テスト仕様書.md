# E2E テスト仕様書 — Employee Directory（新画面）  
※既存画面（http://localhost:8081/）の解析結果と、新画面ソースコード + API 定義書を比較して作成しています。  
出力は日本語・Markdown形式です。

---

## 1. 画面の目的と概要（既存システムとの差分含む）

目的: 従業員データの一覧表示およびフィルタ検索を行う管理画面。  
主な機能: 名前（部分一致・大文字小文字無視）、性別（完全一致）、生年月日（完全一致）による絞り込み。フィルタに合致する従業員をテーブル表示し、合致件数をバッジで表示する。絞り込み結果が0件の場合は空状態メッセージと「Clear Filters」ボタンを表示する。

既存システム（実際に http://localhost:8081/ を確認）との主な差分：
- 言語：既存は日本語ラベル（名前/性別/生年月日/備考）、新画面は英語ラベル（Name/Gender/Date of Birth 等）。
- 入力項目：既存にあった「備考」フィールドは新画面には存在しない（新画面のテーブル列は ID/Name/Gender/Date of Birth）。
- 検索トリガー：既存は「検索」ボタン押下でサーバ検索を行う設計、対して新画面（ソース）は入力 onChange で即時フィルタ（クライアント側スタブデータ）する設計。将来的には API（/api/employees）へ GET リクエストを貼る想定（API定義書あり）。
- 性別オプション：既存は「指定なし」「男性」「女性」だけだが、新画面は "Male"/"Female"/"Other"（"Other" が追加）。
- 空状態の扱い：新画面は空状態で SVG アイコンと「Clear Filters」ボタンを表示する。
- 新画面では検索件数をバッジ（例: "3 found"）で表示する。

注）現在のローカル稼働中の既存アプリ（スナップショット）ではサーバサイド検索と備考列があり、APIエンドポイント(/api/employees)は API 定義書に記載されているが、現時点の新画面ソースはスタブデータを使用しており、ネットワーク呼び出しを行いません。E2E テスト自動化では「UI の仕様」と「API 仕様（契約）」の両方を検証するため、Playwright 等でネットワークのスタブ（モック）・検査を行うシナリオを含めます。

---

## 2. 検証すべきテストシナリオ一覧

※自動化対象から除外したい場合は、チェックボックスを `- [ ]` に変更してください。各見出しは必ずタスクリスト形式で始めます。

- [x] 画面初期表示（Header / subtitle / フィルタ入力 / 結果テーブルの存在）
- [x] 名前フィルタの部分一致（大文字小文字差の無視）
- [x] 性別フィルタの完全一致（Male / Female / Other）
- [x] 生年月日フィルタの完全一致（YYYY-MM-DD）
- [x] 複数フィルタ同時適用（name + gender, name + dob, gender + dob）
- [x] 絞り込み結果件数バッジ表示（件数が UI と一致すること）
- [x] テーブル行のデータ整合性（ID, Name, Gender, DateOfBirth が一致、gender-badge の CSS クラス）
- [x] 空結果の空状態表示（アイコン、メッセージ、Clear Filters ボタン表示）と Clear Filters の動作
- [x] 検索トリガーの有無（Search ボタンは存在しないこと／onChange で絞り込み）※既存との差分検証
- [x] API 呼び出しパターン（期待クエリパラメータ） — 正常系（200 + 配列）
- [x] API 異常系：404/500 等のハンドリング（UI に適切なエラーメッセージまたはフォールバックが行われること）
- [x] API 空リスト応答（200 + []）時の UI 表示（空状態）
- [x] API レスポンス遅延時の UI 応答（ローディング表示またはタイムアウトの振る舞い）※ローディング未実装なら「応答なしの状態」を期待して異常系として扱う
- [x] 入力エッジケース：空文字、長い文字列、特殊文字（日本語/英数字/記号）、日付未選択
- [x] 性別に "Other" を選択した場合の表示（テーブル上の表記とクラス）
- [x] 大量データ想定の表示（多数行のレンダリング確認）※パフォーマンス観点の簡易確認

---

## 3. 各シナリオの詳細（操作手順、期待結果、API 要件）

以下は Playwright 等で自動化する前提の具体手順・アサーション指示です。セレクタは新画面ソース（id / class）に基づきます。API 検証は実環境が未実装の場合はネットワークを intercept / mock して確認します。

共通（セレクタ / 期待要素）
- ヘッダ: h1 = "Employee Directory"
- サブタイトル: p.subtitle
- Name input: #name-filter (type="text")
- Gender select: #gender-filter (select option values: "", "Male", "Female", "Other")
- DOB input: #dob-filter (type="date")
- Results count: .badge（テキスト例: "3 found"）
- Table: table.styled-table > tbody > tr（行）、各列: .cell-id, .cell-name, gender は <span class="gender-badge male/female/other">, DateOfBirth は 4列目
- Empty state: td.empty-state .empty-content p（"No employees match your search criteria."）、.reset-btn（Clear Filters ボタン）
- Search button: (存在しないことを確認) 例: text=`検索` / button with label "Search"などはないこと

テストデータ（ソースのスタブに基づく）
- EMP-001: 山田 太郎, Male, 1990-01-15
- EMP-002: 佐藤 花子, Female, 1995-05-20
- EMP-003: 鈴木 一郎, Male, 1985-11-03
- EMP-004: 田中 裕子, Female, 1992-08-12
- EMP-005: 伊藤 健太, Male, 1998-03-25

---

### - [x] 画面初期表示（Header / subtitle / フィルタ入力 / 結果テーブルの存在）
- 前提：ページを開く（http://localhost:8081/ 新画面がデプロイされている前提）。  
- 操作手順（Playwright 想定）:
  1. page.goto('/path-to-new-dashboard') または /（環境に応じて）
  2. 要素が表示されるまで待つ（例: await page.waitForSelector('#name-filter')）
- 期待結果:
  - h1 に "Employee Directory" が表示される
  - p.subtitle が存在する（"Manage and filter staff records seamlessly." 等）
  - #name-filter、#gender-filter、#dob-filter が表示されている
  - 結果テーブル table.styled-table が表示され、初期は全件（5件）が表示される
  - .badge が "5 found" を示す
- API 要件:
  - （新画面がサーバへ問い合わせする設計の場合）起動時に GET /api/employees が呼ばれる（クエリなし）。レスポンス 200 + 配列（5個の Employee）を期待。

---

### - [x] 名前フィルタの部分一致（大文字小文字差の無視）
- 前提：画面ロード済み
- 操作手順:
  1. #name-filter に "山田" を入力
  2. 入力完了後、リストの変化を待つ（onChange で即時反映）
- 期待結果:
  - テーブルに 1 行のみ表示され、.cell-name が "山田 太郎" を含む
  - .badge が "1 found"
- API 要件:
  - フロントがサーバに問い合わせる場合：GET /api/employees?name=山田 を期待（パラメータは URL エンコードすること）
  - サーバ応答例（200）: [ { id:"EMP-001", name:"山田 太郎", gender:"Male", dateOfBirth:"1990-01-15" } ]

検証ポイント:
- 部分一致の検証（例："山" や "太郎" でもヒットするか）
- 大文字小文字の無視：英字でのテストを追加（例: name "YAMADA" が "Yamada" にマッチすること）

---

### - [x] 性別フィルタの完全一致（Male / Female / Other）
- 前提：画面ロード済み
- 操作手順:
  1. #gender-filter を "Male" に選択
- 期待結果:
  - テーブルに male の従業員（EMP-001, EMP-003, EMP-005）3件が表示される
  - .badge が "3 found"
  - 各行の Gender 列に表示されるテキストは "Male"
  - gender-badge にクラス "male" が付与されている（class 名は emp.gender.toLowerCase() に依存）
- API 要件:
  - GET /api/employees?gender=Male（完全一致。サーバは enum 値を受け取る）

追加:
- "Other" を選択した場合は、該当が無ければ 0 件（空状態）となることを確認する。API 仕様上は "Other" を受け付ける。

---

### - [x] 生年月日フィルタの完全一致（YYYY-MM-DD）
- 前提：画面ロード済み
- 操作手順:
  1. #dob-filter に "1995-05-20" を入力/選択
- 期待結果:
  - 佐藤 花子 (EMP-002) のみ表示される
  - .badge が "1 found"
- API 要件:
  - GET /api/employees?dateOfBirth=1995-05-20（format: YYYY-MM-DD）

注：date input により不正な日付入力は UI 上防がれる。手動で不正な文字列を送ることはできない。

---

### - [x] 複数フィルタ同時適用（組合せ検証）
- シナリオ例 1（name + gender）:
  - 入力: name="鈴木", gender="Male" → 期待: EMP-003 のみ
- シナリオ例 2（name + dob）:
  - 入力: name="田中", dateOfBirth="1992-08-12" → 期待: EMP-004 のみ
- シナリオ例 3（gender + dob）:
  - 入力: gender="Female", dateOfBirth="1995-05-20" → 期待: EMP-002 のみ
- 操作手順:
  1. 対応する各入力をセット
  2. 結果反映を待つ
- 期待結果:
  - 期待該当行のみ表示されている
  - .badge が 1 を示す
- API 要件:
  - GET /api/employees?name=...&gender=...&dateOfBirth=...（指定されたパラメータのみを付与）

---

### - [x] 絞り込み結果件数バッジ表示
- 前提：画面ロード済み
- 操作手順:
  1. 各フィルタ操作を行い、該当件数を確認
- 期待結果:
  - .badge の数字がテーブル表示行数と一致する（数値と "found" の文言を確認）
- API 要件:
  - サーバからの配列の length を UI が正しく反映していること

---

### - [x] テーブル行のデータ整合性（ID, Name, Gender, DateOfBirth / gender-badge の CSS）
- 前提：画面ロード済み
- 操作手順:
  1. 初期表示（全件）で各行の列を順に検査
- 期待結果:
  - 1列目: ID（class="cell-id"）が EMP-... 形式であること
  - 2列目: 名前が Employee.name と一致
  - 3列目: gender のテキストが Employee.gender（"Male"/"Female"/"Other"）
  - 3列目の <span> に class `gender-badge male` 等、gender の小文字が含まれること
  - 4列目: dateOfBirth が YYYY-MM-DD 形式で表示される
- API 要件:
  - UI の各列が API レスポンスのフィールドに対応していること

---

### - [x] 空結果の空状態表示と Clear Filters の動作
- 前提：画面ロード済み
- 操作手順:
  1. name に "存在しない名前" を入力（例: "ZZZ"）
  2. 空状態の UI を確認
  3. .reset-btn（Clear Filters）をクリック
- 期待結果:
  - 空状態では以下が表示される:
    - SVG アイコン（empty-icon）
    - メッセージ "No employees match your search criteria."
    - Clear Filters ボタン（.reset-btn）
  - Clear Filters クリックで全フィルタがリセット（#name-filter が空、#gender-filter が ""、#dob-filter が空）
  - フィルタクリア後、テーブルに全件（5件）が表示され、.badge が "5 found"
- API 要件:
  - Clear Filters 後に GET /api/employees が呼ばれる場合はクエリ無しで全件取得（200 + 全配列）

---

### - [x] 検索トリガーの有無（Search ボタンは存在しないこと）
- 前提：画面ロード済み
- 操作手順:
  1. page.locator('button', { hasText: 'Search' }) / page.getByRole('button', { name: /Search|検索/ }) で存在確認
- 期待結果:
  - "検索" / "Search" といった実行ボタンは DOM に存在しないこと（新画面仕様では onChange で即時フィルタリングされる）
- 補足（既存との差分確認）:
  - 既存画面では「検索」ボタンが存在するため、差分レビュー用テストとしても検証する。

---

### - [x] API 呼び出しパターン（期待クエリパラメータ） — 正常系（200 + 配列）
- 前提：フロントが実際に API を呼び出す実装になっている、またはテストで network intercept を使う
- 操作手順（Playwright の route/expect を用いる例）:
  1. page.route('**/api/employees**', route => { route.continue() 或いは route.fulfill({ status:200, body: JSON.stringify(mockEmployees) }) })
  2. 操作でフィルタを適用し、該当リクエストが発行されることを待つ
  3. リクエストの URL クエリ文字列を検証（name/gender/dateOfBirth の有無と値）
- 期待結果（リクエスト）:
  - クエリ名は API 定義書に準拠（name, gender, dateOfBirth）
  - 使われていないパラメータは付与しない（または空なら省略）
- 期待結果（レスポンス）:
  - 200 の場合、body は配列（0件〜複数）で Employee オブジェクトを含む
  - UI は受け取った配列長に応じて表示を更新する

レスポンス例（モック）
```json
[
  { "id": "EMP-001", "name": "山田 太郎", "gender": "Male", "dateOfBirth": "1990-01-15" },
  ...
]
```

---

### - [x] API 異常系：500 / 404 のハンドリング
- 前提：network を intercept してエラー応答を返す
- 操作手順:
  1. route.fulfill({ status: 500, body: JSON.stringify({ message: "Internal Server Error" }) })
  2. 操作（フィルタ変更）を行い、API 呼び出しをトリガー
- 期待結果:
  - UI がエラーメッセージを表示すること（設計未定の場合は最低でも console エラーを確認し、テストでは「エラー状態のハンドリング」が行われることを要件として残す）
  - 試験設計メモ: 現行ソースでは API エラー時の明示的なエラーメッセージ表示が未実装である可能性があるため、PO に「エラー時の表示要求」を確認すること
- API 要件:
  - 500 や 4xx を明確に返せること（テストは mock を用いる）

---

### - [x] API 空リスト応答（200 + []）時の UI 表示（空状態）
- 前提：route.fulfill({ status:200, body: '[]' })
- 操作手順:
  1. 任意のフィルタを入力（または mock によって [] を返す）
- 期待結果:
  - 空状態（上記の空メッセージ・Clear Filters 表示）に遷移する
  - .badge は "0 found" と表示される（実装に合わせて確認。もし "0 found" でない場合は要仕様確認）

---

### - [x] API レスポンス遅延時の UI 応答（ローディング/タイムアウト）
- 前提：route.fulfill を遅延させる（setTimeout で数秒遅延）
- 操作手順:
  1. route で 3〜5 秒遅延して 200 を返す
  2. フィルタを変更して API 呼び出しを発生させる
- 期待結果:
  - ローディングインジケータが UI にある設計ならそれが表示される（新画面に未実装の場合は「応答中」に対する設計が必要）
  - タイムアウトの取り扱い（指定時間で失敗とする等）が設計されていればそれに従う
- メモ:
  - 現行ソースにローディング表示がなければ、遅延時に UI が凍る / 何も変化しないことを「既知の挙動」として記録し、改善要求を提出する。

---

### - [x] 入力エッジケース（空文字、長文字列、特殊文字、日本語）
- テストケース:
  1. name に空文字 → 全件表示（既定の挙動）
  2. name に長文字列（例 500 文字）→ サニティチェック（UI が固まらない / エラーにならない）
  3. name に記号や絵文字 → サニティチェック（部分一致に影響しない）
  4. dob に未選択 → フィルタとして無視される
- 期待結果:
  - UI が例外を投げないこと
  - API を呼ぶ場合は、不要な空パラメータを送らないこと（またはサーバ側で適切に無視すること）

---

### - [x] 性別に "Other" を選択した場合の表示
- 前提：従業員データに Other がいる前提（モックで作成）
- 操作手順:
  1. #gender-filter を "Other" に選択（またはモックレスポンスに Other を含める）
- 期待結果:
  - テーブルに Other の従業員が表示される
  - gender-badge のクラスは "other" であること
- API 要件:
  - GET /api/employees?gender=Other を受け付けること

---

### - [x] 大量データ想定の表示（簡易パフォーマンス）
- 前提：mock で 1000 件程度の Employee を返す
- 操作手順:
  1. route.fulfill({ status:200, body: JSON.stringify(大量配列) })
- 期待結果:
  - テーブルがレンダリングされる（全件表示が極端に遅くないことを確認）
  - 必要であればページネーションや仮想化の導入が必要である旨をレポート
- メモ:
  - 新画面の現状はスタブ配列を全件描画する実装のため、大量データはパフォーマンス問題の指摘対象

---

## 補足：Playwright での実装ヒント（自動化スクリプト向け）

- ネットワークモック（API 仕様検証）:
  - page.route('**/api/employees**', async (route, request) => { 
      // リクエスト URL の query を検査して期待クエリと一致するか assert
      // route.fulfill({ status:200, body: JSON.stringify(mockResponse) })
    })
- 入力操作:
  - await page.fill('#name-filter', '山田')
  - await page.selectOption('#gender-filter', 'Male')
  - await page.fill('#dob-filter', '1990-01-15') // date input は format に注意
- テーブル検証:
  - const rows = await page.$$eval('table.styled-table tbody tr', rows => rows.map(r => r.innerText));
  - badge のテキスト: await page.textContent('.badge')
- 存在しない Search ボタン確認:
  - const btn = await page.$('button:has-text("検索"), button:has-text("Search")'); expect(btn).toBeNull();
- エラー時 UI 検証:
  - モックで 500 を返し、画面上に `.error-message` 等が表示されるかを確認（実装がなければ要件としてドキュメント化）

---

## 期待される API リクエスト仕様（要約）
- エンドポイント: GET /api/employees
- クエリパラメータ:
  - name (optional): 部分一致検索用文字列（サーバ側は部分一致で実装）
  - gender (optional): "Male" | "Female" | "Other"（完全一致）
  - dateOfBirth (optional): YYYY-MM-DD（完全一致）
- レスポンス:
  - 200: application/json で Employee[]（各 Employee: id, name, gender, dateOfBirth）
  - 4xx/5xx: エラーレスポンス（body に { message: "..." } 等） — フロントは適切にハンドリングすること
- 備考:
  - 未指定のパラメータは省略してリクエストすることが望ましい
  - パラメータ値は URL エンコードして送信すること

---

## テスト実装上の注意・既知差分リスト（開発/PO への確認項目）
1. 新画面では現在スタブデータ（STUB_EMPLOYEES）を使用している。実装時に API 呼び出しを導入する想定でテストを作成すること。E2E 実行環境では API のモックを利用することを推奨。
2. エラー表示やローディング表示の UI が設計書にない場合、期待動作を PO と合意してから自動化する（現在は未実装の可能性あり）。
3. 既存画面の「備考」列は新画面で削除されているため、部署等の情報が必要な場合は API 側仕様の更新が必要。
4. 言語差分（日本語/英語ラベル）は画面遷移テストや翻訳対応の要否を確認すること。
5. 性別に "Other" が追加されているため、既存データに Other を含めるかどうかを DB 設計で確認すること。

---

以上が、既存画面と新画面（ソース）・API 定義を踏まえた E2E テスト仕様書です。  
自動化スクリプト（Playwright）作成時に必要であれば、各シナリオの Playwright コードテンプレート（route モックを含む）を出力します。どのシナリオから実装しますか？
# 概要
提供されたテスト結果（Playwright レポート）と画面ソース（AdminDashboard コンポーネント）を比較したところ、テストが失敗している主な原因は「テストが期待するセレクタ／属性（例：data-testid、恒常的に存在するリセットボタン、gender 値の形式 等）が画面ソースに存在しない／想定と異なる」ことと推定されます。  
以下に失敗しうるテストケース例、原因の特定箇所、及び具体的な修正案（コード差分例）を提示します。

---

1) 失敗しうるテストケースと推定原因
- 失敗ケース A: "検索フィールド（name / gender / date）を Playwright で取得できない"  
  推定原因: テスト側で `data-testid="name-filter"` 等の data-testid 属性で要素を取得しているが、実装では input/select に該当の `data-testid` が付いていない（実装は `id="name-filter"` 等のみ）。
- 失敗ケース B: "結果件数（badge）を特定できない / 検索結果カウントのセレクタがヒットしない"  
  推定原因: テストが `data-testid="results-count"` のような明示的な属性を期待しているが、実装は <span className="badge"> を使っているだけで data-testid が無い。
- 失敗ケース C: "Clear / Reset Filters ボタンが見つからない／操作できない"  
  推定原因: 実装では「Clear Filters」ボタンが検索結果がゼロ（empty state）のときにのみ <tbody> の empty-state にレンダリングされる。テストは（結果のある状態や検索パネル直下で）常にアクセスできるボタンを期待している可能性がある。
- 失敗ケース D: "Gender の値比較が失敗する"  
  推定原因: テストが `<option value="male">` のような小文字値を期待している（case-sensitive な比較）にも関わらず、実装では `value="Male"` のように TitleCase を使っている。
- 失敗ケース E: "アクセシビリティや自動化用の明確な role/aria が不足しているため取得失敗"  
  推定原因: 特に Playwright のテストで role や accessible name を利用している場合、ボタンや重要要素に aria-label / data-testid があると安定するが、現在それらが不足している。

（上記は Playwright レポートからの典型的な不一致パターンに基づく推定です。実際の失敗ログに特定のセレクタやエラーメッセージがあればさらに精密に対応できます。）

---

2) 画面ソースのどこに問題があるか（具体的箇所）
- search-panel（JSX 内）
  - name input, gender select, date input に data-testid 属性がない（セレクタ不一致）。
  - Gender の option value は "Male"/"Female"/"Other"（TitleCase）で、テストが小文字値を期待する場合は不一致。
  - Clear Filters ボタンは empty-state（結果が0のとき）にしか存在しないため、テストが結果ありのときにリセットを使えない。
- results-panel（JSX 内）
  - 結果件数（badge）に data-testid が付与されていない。
- 汎用
  - 自動化／アクセシビリティ向けの data-testid / aria-* が不足している（例：検索ボックスやリセットボタン、結果テーブル等）。

---

3) 具体的なコード修正提案（差分・例）
以下は最小の変更でテスト／自動化に安定させるための修正案です。

- 変更点要約
  1. 検索入力要素に data-testid を追加（name/gender/dob）。
  2. gender の option value を小文字（"male"/"female"/"other"）に変更（表示ラベルはそのまま TitleCase）。
  3. 検索パネルに常時利用できる「Clear Filters」ボタン（Reset）を追加（empty-state 内のボタンは残しても良い）。
  4. 結果件数バッジに data-testid="results-count" を追加。
  5. 可能であれば重要な要素に aria-label を追加（アクセシビリティ＆セレクタ耐性向上）。

- 修正コード（AdminDashboard の該当箇所の抜粋／置換例）

```tsx
/* 検索パネル内の input/select を下記のように修正します */

/* Name */
<input
  id="name-filter"
  data-testid="name-filter"
  aria-label="Filter by name"
  type="text"
  placeholder="Search by name..."
  value={searchParams.name || ''}
  onChange={(e) => handleSearchChange('name', e.target.value)}
  className="styled-input"
/>

/* Gender */
<select
  id="gender-filter"
  data-testid="gender-filter"
  aria-label="Filter by gender"
  value={searchParams.gender || ''}
  onChange={(e) => handleSearchChange('gender', e.target.value)}
  className="styled-input"
>
  <option value="">All Genders</option>
  <option value="male">Male</option>
  <option value="female">Female</option>
  <option value="other">Other</option>
</select>

/* Date of birth */
<input
  id="dob-filter"
  data-testid="dob-filter"
  aria-label="Filter by date of birth"
  type="date"
  value={searchParams.dateOfBirth || ''}
  onChange={(e) => handleSearchChange('dateOfBirth', e.target.value)}
  className="styled-input"
/>

/* 検索パネルに常時表示されるリセットボタン（empty-state 内のボタンは残す） */
<button
  className="reset-btn"
  data-testid="reset-filters"
  aria-label="Clear filters"
  onClick={() => setSearchParams({ name: '', gender: '', dateOfBirth: '' })}
>
  Clear Filters
</button>
```

- 結果ヘッダの件数バッジへ data-testid を追加

```tsx
/* Results header 内 */
<div className="results-header">
  <h2>Results</h2>
  <span className="badge" data-testid="results-count">{filteredEmployees.length} found</span>
</div>
```

- 注意点（gender 値変更の影響）
  - 既存のロジックで gender を比較している箇所（filteredEmployees のフィルタ）は文字列比較なので、小文字にすると正しく動作しますが、既に `Employee.gender` の型が 'Male'|'Female'|'Other' 固定であれば、データ側と UI 側で値の正規化を行うべきです。例えば入力値を比較するときは .toLowerCase() を使って安全化します：

```ts
const matchGender = !searchParams.gender || emp.gender.toLowerCase() === searchParams.gender.toLowerCase();
```

（あるいは option の value を TitleCase のままにしてテスト側を合わせる、という選択肢もあります。どちらを採るかはチームの方針に合わせてください。）

---

追加の改善提案（テスト安定化）
- data-testid による要素取得を統一しておくと Playwright テストは安定します（例: "name-filter", "gender-filter", "dob-filter", "reset-filters", "results-count", テーブルの行には data-testid="employee-row-{id}" 等）。
- 重要な操作（reset、検索）に aria-label を加えることでアクセシビリティが向上し、Playwright の role/aria ベースのセレクタにも対応しやすくなります。
- Clear Filters ボタンを empty-state 専用ではなく検索パネルに常設することで、テストがどの状態でもリセット操作を行えるようになり、E2E テストの安定性が向上します。

---

4) まとめ（推奨する最小修正）
- 検索 input/select に data-testid を追加（必須）
- 結果カウントに data-testid="results-count" を追加（必須）
- Clear Filters ボタンを検索パネル内に常設する（推奨）
- gender option の value を小文字にするか、フィルタ比較時に .toLowerCase() を用いる（どちらかを採用）

これらを適用すれば、Playwright テストが期待しているセレクタや UI の存在に合致し、テストの多くは成功へ向かうはずです。必要であれば、実際のテストのエラーメッセージ（Playwright の失敗ログに出ている「期待したセレクタ」や「not found」など）を共有いただければ、さらにピンポイントで修正差分（patch / git diff）を作成します。
# Paper Daily · arXiv 论文日报

公开网站：https://paperdaily.wfz521.com/

**研究来源为 arXiv**：检索计算机科学（cs）与数学（math）官方新公告列表，包含其中的交叉公告并按稳定编号去重。网页按日期、arXiv 官方学科组、主分类、阅读深度和文本搜索筛选；点击论文标题或“展开总结”原地阅读，再次点击收起。原始论文链接独立。

## 来源与阅读范围

- 唯一主动研究来源是 arXiv 官方新公告列表、RSS、摘要页及可合法取得的 arXiv 全文。`data/sources.json` 仅列 arXiv，不调用外部论文数据库、出版商、机构网站或作者网站继续研究。
- 作者与机构只依据所读 arXiv 版本署名；未披露或未核实明确说明，不向外部网站补查，不猜当前职务、经历或个人相关性。
- 优先阅读全文；最低须实际取得并阅读完整标题和摘要。仅标题、检索片段、打不开摘要者只记检索缺口，不生成论文卡片。
- `reading_depth=abstract` 显著标“摘要级解读”；保存 `abstract_review={source_url,complete_abstract_accessed:true,read_confirmed:true,scope}`，必须有真实阅读依据。
- `partial` / `full_review` 保存 `substantive_review` 的 `content_urls`、`scope`、`method_evidence`、`result_evidence`、`conditions_evidence`。局部正文阅读不等于全文证明审核或实验复现。未读部分不补猜。
- 总结包含中英文标题、全部作者、署名机构、研究问题、主要结果、方法、条件与局限、日期版本和原文链接。重要结果按作者主张转述，不冒充独立验证。
- 不执行论文代码、不开展实验、不转载原始摘要或论文全文。代码链接如已在原稿核实可保留，但不运行。

## arXiv 官方分类

- 分类目录为 `data/arxiv-taxonomy.json`，以 arXiv 官方 taxonomy 为准。中英显示名称中的中文仅为译名，官方英文名称及代码保留。
- 每篇保存 `primary_category`、`canonical_primary_category`、`arxiv_group`、`arxiv_archive`、`cross_categories`、`arxiv_categories` 和 `category_evidence`。主分类必须取自官方明确标识的主分类字段，不按代码顺序或内容推断。
- 网页与报告按官方主分类唯一归组；交叉分类仅作官方类别标签，不重复计数。官方别名按目录的 canonical_code / canonical_group 对应，不能仅用代码前缀归组。
- cs.CR（Cryptography and Security）属于 Computer Science；math-ph（Mathematical Physics）属于 Physics。物理学保留官方 archive 层级；同名 archive 与 category 合并显示，避免重复标题。
- 当前数据不接受自定义 domains、subfields、keywords 分类字段；研究方法与概念保留在科学内容正文，不另造分类标签。

## AOE 日界与去重

- 每日 AOE 24:00（UTC−12）更新，即 UTC 次日 12:00、北京时间次日 20:00。固定 UTC−12，无夏令时；自动任务原有启用状态和日程不变。
- 截止 T 只统计 `[T−24h,T)` 内首次公开公告的论文，归档日期为刚结束的 AOE 自然日。检索窗口为连续 24 小时，仅发布已结束窗口的日报。
- arXiv 提交日期不是公告日期；RSS 批次时间是来源提供的批次证据，不伪称独立观测的精确首次可访问秒数。保存 `public_at`、`public_time_source`、`public_time_precision`、`date_note` 和 `eligibility`。
- 时间范围完全落在窗口内才能 `confirmed`。只有日期、时区不明或边界不能确定时，已读条目放 `pending_papers`，另列且不计确认新增。
- 按稳定 arXiv 编号合并跨分类、重复公告及版本；`replaced` / 修订不计作新论文。保留实际核实的版本变化，不靠更新时间杜撰内容变化。
- `editorial_note` 和检索日志区分目录发现、完整摘要实际阅读、核心正文审阅、确认新增与时间待核实。获取整个目录不等于读完全部论文，不把选读冒充全量覆盖。

## 当前文件结构

- `index.html`、`assets/`：无外部依赖的静态网页；无来源选择器或按来源分组。
- `data/issues.json`：当前 arXiv 日期索引，`source_scope=arxiv_only`；每项明确 `path` 与 `report`，前端按索引载入。
- `data/arxiv/YYYY-MM-DD.json`：当前每期结构化数据，所有确认及待核实条目的 `source` 必须是 `arxiv`。
- `reports/arxiv/YYYY-MM-DD.md`：当前每期中文 Markdown。下载按钮只链接当前 arXiv 报告。
- `data/retrieval/arxiv/YYYY-MM-DD.json`：该期官方入口、时间证据、实际检索/阅读数量及缺口。
- `data/arxiv/seen.json`：当前范围的已收录稳定身份与首次正式期次，供跨日去重。
- 历史文件原位保留，不进入当前网页索引或统计；校验器验证已有内容未被覆盖。

## 每日增量流程

1. 读取本规范、当前来源目录、日期索引与 `data/arxiv/seen.json`，先检查本期是否已经发布；保留远程用户更改。
2. 全面检索本期 24 小时窗口内 cs 与 math 列表的 arXiv 官方新公告，完成分页与跨分类去重；先建立全部候选清单，再逐篇阅读标题和完整摘要进行筛选，不能先随意抽取小样本。记录目录发现、摘要已筛、未筛和失败数量。
3. 在全体候选摘要筛选基础上，按问题重要性、方法/理论新意、证据强度、技术实用性及可解释价值选择值得详细总结的研究，记录入选理由；不以热度或编号代替判断。优先再读入选稿全文。未完成全体摘要筛选时明确标为进行中/阶段性选读，不宣称已全面筛选；没有合格新增时可发零篇，不用旧稿凑数。
4. 写入 `data/arxiv/YYYY-MM-DD.json`、相应检索日志，更新当前日期索引及当前去重表。重跑是更正或补录，不重复声称论文首次发表。
5. 执行：
   ```sh
   python3 tools/render_markdown.py
   python3 tools/validate.py
   python3 tools/test_time_validation.py
   python3 tools/test_screening_validation.py
   node --check assets/app.js
   node tools/test_ui.cjs
   ```
6. 交互更改还需检查桌面/手机、键盘、重复展开收起、组合筛选、清除、日期载入及 Markdown 下载路径。展开状态在同一期筛选中保留，成功切换期次后重置。
7. 保存至 Space「学术论文日报」，原规范/源码归档保持同一文件身份；公开 ZIP 仅含源码与原创总结，不含原始论文、抓取缓存、运行数据或私密信息。
8. 非强制提交到 `wang2000star/paper-daily` 的 main；保留 `CNAME`，不改 DNS、凭据或仓库权限。核验远端提交、Pages 部署及线上实际字节，不把提交成功当成已上线。

## 运行边界

日报由已设置的每日任务采集、整理、存档并提交；本站是 GitHub Pages 静态展示端，不虚构仓库内的联网摘要后台。默认不发邮件；无第三方追踪，不在前端放密钥，不依赖查看者电脑。

仅整理公开学术资料，不含私人研究进度或内部笔记。原文版权属于作者与出版方；未取得独立许可前，不推定本仓库赋予超出版权法的再许可。

## 全量摘要筛选的交付校验

- 每期按实际窗口目录建立候选总数和稳定ID清单，逐条记录完整摘要阅读、选择理由与证据边界；只有候选ID集合与已读集合完全一致，才能标全量摘要初筛完成。分片数、分片大小和候选总数随当期实际数量变化，不固定为某一日的样本数。
- 最终精选是完成初筛后的已核名单；每篇标“入选理由（据论文所述贡献）”，结果明确为作者报告，未独立审核的重要证明主张不在标题中冒充定论。
- 署名/机构标题页核对与正文阅读分开统计；核对署名不把摘要级升级为局部正文审阅。机构无证据时明确未核实，不推断当前职务。
- 全量筛选、最终内容复核及机构元数据冻结完成后统一保存和发布，不上传未完成的中间批次。原始摘要和全文不进入公开源码；逐篇原创筛选台账另存 Space。

- 零库存期必须在截止后复核 cs 与 math 官方列表或 RSS，并记录 `zero_inventory_verification` 的来源 URL、检查时间、完整状态与零新增计数。零库存不伪造阅读分片；非零库存仍须完整分片和逐 ID 审读证据。检索失败或初筛未完不等于零新增。

## 面向读者的文案

首页和日报仅保留日期窗口、研究范围、阅读深度、来源状态及证据边界等阅读必需信息。需求变更、维护过程、内部约束和执行记录不进入读者文案；技术维护细节另存文档或检索记录。

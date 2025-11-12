# Godot 4.5 + C# 闁瑰灈鍋撻柡鍫灡閻栥倖娼绘担鐩掆晝鎷嬮垾鍐茬亰缂佷究鍨圭槐?

> Windows-only 韫囶偊鈧喐瀵氬?/ Quickstart: 鐟?See [Phase-17-Windows-Only-Quickstart.md](Phase-17-Windows-Only-Quickstart.md)
> 鏉╂盯妯佺悰銉ュ帠 / Addendum: [Phase-17-Windows-Only-Quickstart-Addendum.md](Phase-17-Windows-Only-Quickstart-Addendum.md)
> Phase 6 DB Quickstart: 瑙?See [Phase-6-Quickstart-DB-Setup.md](Phase-6-Quickstart-DB-Setup.md)
> FeatureFlags Quickstart: See [Phase-18-Staged-Release-and-Canary-Strategy.md](Phase-18-Staged-Release-and-Canary-Strategy.md)
> Windows Manual Release: See [WINDOWS_MANUAL_RELEASE.md](../release/WINDOWS_MANUAL_RELEASE.md)


> 濡炪倕婀卞ú? vitegame 闁?godotgame
> 閺夆晙鑳朵簺缂侇偉顕ч悗? 閻庣懓鏈弳锝夊箮閳ь剟寮甸娑氬灲闁哄洦瀵у畷鏌ユ晬閸絿绠ラ悶娑樻湰濡?+ UI + 婵炴挸寮堕悡?+ 婵炴潙顑堥惁顖炴晬?
> 闁烩晩鍠楅悥锝夌嵁閸愭彃閰? Windows Desktop
> 闁哄牃鍋撻柛姘濞插潡寮? 2025-12-21

---

## 閺夆晙鑳朵簺婵帒鍊介～?

### 闁哄秶顭堢缓楣冨矗濡搫顕ч悗闈涙贡閸欏海鎮?

| 閻忕偛鍊归?| 闁告鍠愭俊褔寮甸娑氬灲 (vitegame) | 闁哄倻澧楁俊褔寮甸娑氬灲 (godotgame) | 閺夆晙鑳朵簺濠㈣泛绉靛鍛償?|
|------|-------------------|-------------------|----------|
| 婵℃鐭傚鎵偓鍦嚀濞?| Electron | Godot 4.5 | 闁宠棄鎳夊Σ鍕煡閸涱亝顫夐柍?|
| 婵炴挸鎲￠崹娆忣嚕閺囩喐鎯?| Phaser 3 | Godot 4.5 (Scene Tree) | 闁宠棄鎳夊Σ鍕煡閸涱亝顫夐柍?|
| UI婵℃妫欓悘?| React 19 | Godot Control | 闁宠棄鎳夊Σ鍕煡閸涱亝顫夐柍?|
| 闁哄秴鍢茬槐?| Tailwind CSS v4 | Godot Theme/Skin | 闁宠棄鎳夊Σ鍕煡閸涱亝顫婇柍?|
| 鐎殿喒鍋撻柛娆愬灱椤曘垻鎳涢埀?| TypeScript | C# (.NET 8) | 闁宠棄鎳夊Σ鍕煡閸涱亝顫夐柍?|
| 闁哄瀚紓鎾愁啅閵夈儱寰?| Vite | Godot Export Templates | 闁宠棄鎳夊Σ鍕煡閸涱亝顫婇柍?|
| 闁告娲栭崢鎾趁圭€ｎ厾妲?| Vitest | xUnit + FluentAssertions | 闁宠棄鎳夊Σ鍕煡閸涱亝顫婇柍?|
| 闁革妇鍎ゅ▍娆徝圭€ｎ厾妲?| - | GdUnit4 (Godot Unit Test) | 闁宠棄鎳夊Σ鍕煡閸″繑顫婇柍?|
| E2E婵炴潙顑堥惁?| Playwright (Electron) | Godot Headless + 闁煎浜滅紓鎻渦nner | 闁宠棄鎳夊Σ鍕煡閸涱亝顫夐柍?|
| 閻熸洖妫涘ú濠囨偝?| Vitest Coverage | coverlet | 闁宠棄鎳夊Σ鍕煡閸″繑顫婇柍?|
| 闁轰胶澧楀畵浣规償?| SQLite (better-sqlite3) | godot-sqlite | 闁宠棄鎳夊Σ鍕煡閸″繑顫婇柍?|
| 闂佹澘绉堕悿鍡欌偓娑櫭崑?| Local JSON | ConfigFile (user://) | 闁宠棄鎳夊Σ鍕煡閸″繑顫婇柍?|
| 濞存粌顑勫▎銏ゆ焻濮橆偂绻?| EventBus (CloudEvents) | Signals + Autoload | 闁宠棄鎳夊Σ鍕煡閸涱亝顫夐柍?|
| 濠㈣埖姘ㄩ崵搴ｇ矙?| Web Worker | WorkerThreadPool / Thread | 闁宠棄鎳夊Σ鍕煡閸涱亝顫婇柍?|
| 闂傚牊鐟﹂埀顑跨閸ㄥ酣寮?| ESLint + TypeScript | Roslyn + StyleCop + SonarQube | 闁宠棄鎳夊Σ鍕煡閸涱亝顫婇柍?|
| 闂佹寧鐟ㄩ銈嗘交閸婄喖鍤?| Sentry (Electron SDK) | Sentry (Godot SDK) | 闁宠棄鎳夊Σ鍕煡閸″繑顫婇柍?|

### 闁稿繑濞婇弫顓燁槹鎼淬劍鐝﹂悹鍥у閸?

**[濡ゅ倹锕㈤ˉ鎾绘⒔椤?闂傚洠鍋撻悷鏇氱閻ｎ剟宕楅妸鈺佹闁?*
- Electron 閻庣懓顦崣蹇涘春閾忕懓娈?闁?Godot 閻庣懓顦崣蹇涘春閾忕懓娈犻柨娑樼墕椤﹀鏌?缂傚啯鍨圭划?闁哄倸娲ｅ▎銏㈠寲閼姐倗鍩犻柣褑妫勯幃鏇㈠础閺囶亞绀?
- React 缂備礁瀚▎?闁?Godot Control 闁煎搫鍊婚崑锝夋晬閸︾澁 闁哄鍩栭悗顖溾偓鐟拌嫰閸欏繑绋夊鍛€遍柨?
- Playwright E2E 闁?Godot Headless 婵炴潙顑堥惁顖炴晬閸喓銈撮悹鍥ㄦ礃椤㈠寮哥捄铏规殮闁稿繈鍔嶅ù娑㈠箲椤喚绀?
- CloudEvents 濠靛倹鍨圭€?闁?Godot Signals 濠靛倹鍨圭€规娊鏁嶉崼婊呯殤濞寸姴澧庨柈瀵哥磼閻旂厧娅㈤悹浣瑰礃椤撴悂鏁?

**[濞戞搩鍙冮ˉ鎾绘⒔椤?闂傚洠鍋撻悷鏇氱窔閳ь剙鍊块崢銈夊绩瑜版巻鍋?*
- TypeScript 濞戞挻鑹炬慨鐔兼焻閺勫繒甯?闁?C# 濡澘妫楅悡娆戜沪閸岋妇绀勯柛娆樺灦閸庢挳宕氶崱妯荤皻缂?+ 濞存粌鎼导鎰板冀閿熺姷宕ｉ柨?
- Vitest 闁告娲栭崢鎾趁圭€ｎ厾妲?闁?xUnit 闁告娲栭崢鎾趁圭€ｎ厾妲搁柨娑樼墛缁佸鎷犻弴鐕佹敱闁哄鍎肩缓鑲╃矓娴兼瑧绀?
- Vite 闁哄瀚紓鎾趁规担琛℃煠 闁?Godot Export 婵炵繝鑳堕埢濂告晬閸喓鈧垰顕欓崫鍕矗闁稿繘鏀卞ù娑㈠箲椤喚绀?
- Sentry 闂傚棗妫欓崹?闁?Sentry Godot SDK闁挎稑鐗愰～鍥圭€ｎ偀鍋撹缁鸿偐绮旀导娆戠

**[濞达絽閰ｉˉ鎾绘⒔椤?闁告瑯鍨伴ˇ鏌ユ偨閵娧呯梾濡?*
- SQLite 闁轰胶澧楀畵浣肝熼垾宕団偓鐑芥晬閸︾帪hema 闁告瑯鍨伴ˇ鏌ユ偨椤帞绀堿PI 闂傚洠鍋撻梺顐㈠€块崢銈夋晬?
- 閻犳劑鍔戦崳娲⒒閵娧屾矗闁诡剚绻嗛惌楣冩晬閸綆娲柣鈺傜墱瀹?闂佹彃绉撮ˇ鏌ユ偝?濠㈣泛绉靛鍛償閿曞倹顫岄柛濠勫帶瑜版彃鈻界捄銊︽殢闁?
- ADR/Base/Overlay 闁哄倸娲﹂妴鍌滅磼閹惧鈧垶鏁嶉崼鐕佹敱闁哄娉涜ぐ鑼偓鐟版湰閺嗭絾绌卞┑鍫熸畬闁?
- 闁哄啨鍎辩换鏃€娼忛幘鍐叉瘔閻熸瑥瀚€垫牠鏁嶉崸妾昰s/ 闁烩晩鍠栫紞宥囩磼閹惧鈧垶宕ｉ娆戠闁归晲绶ょ槐?

---

## 閺夆晙鑳朵簺闁哄倸娲﹂妴鍌滅磼閹惧鈧?

### 缂佹鍏涚粩鎾⒓閼告鍞介柨娑欒壘閸ｎ垱寰勯崶锔剧憿闁糕晛鎼鍥╂媼閹规劦鍚€
- [Phase-1-Prerequisites.md](Phase-1-Prerequisites.md) 闁?闁绘粠鍨伴。銊╁礄閸℃妲靛☉鎾抽娴兼劙宕楀畡鎵殧閻?
- [Phase-2-ADR-Updates.md](Phase-2-ADR-Updates.md) 闁?ADR 闁哄洤鐡ㄩ弻濠冪▔鎼淬垺鐓€濠⒀呭剳缁辨DR-0018~0022闁?
- [Phase-3-Project-Structure.md](Phase-3-Project-Structure.md) 闁?Godot 濡炪倕婀卞ú鎵磼閹惧鈧垳鎷嬮幑鎰靛悁

### 缂佹鍏涚花鈺呮⒓閼告鍞介柨娑欑閻楀疇绠涢崘銊ф勾閺夆晙鑳朵簺
- [Phase-4-Domain-Layer.md](Phase-4-Domain-Layer.md) 闁?缂?C# 濡澘妫楅悡娆戜沪閸屾繄璁ｇ紒澶夌串缁辨─ame.Core闁?
- [Phase-5-Adapter-Layer.md](Phase-5-Adapter-Layer.md) 闁?Godot 闂侇偄鍊块崢銈囦沪閸屾繍鍟庨悹?
- [Phase-6-Data-Storage.md](Phase-6-Data-Storage.md) 闁?SQLite 闁轰胶澧楀畵浣轰沪閸屾繄璁ｇ紒?

### 缂佹鍏涚粭渚€姊奸懜娈垮斀闁挎稒鐡桰 濞戞挸楠稿┃鈧柡鍜佸灥缁鸿偐绮?
- [Phase-7-UI-Migration.md](Phase-7-UI-Migration.md) 闁?React 闁?Godot Control 閺夆晙鑳朵簺
- [Phase-8-Scene-Design.md](Phase-8-Scene-Design.md) 闁?闁革妇鍎ゅ▍娆撳冀閹存粎鐟㈤柤鍝勫€婚崑锝囨媼閹规劦鍚€
- [Phase-9-Signal-System.md](Phase-9-Signal-System.md) 闁?CloudEvents 闁?Signals 閺夆晙鑳朵簺

### 缂佹鍓欏ú鎾绘⒓閼告鍞介柨娑欑缁佸鎷犻弴姘辩Ъ缂侇垰顭烽崳绋款嚈?
- [GdUnit4 C# Runner 闁规亽鍎遍崣鍡涘箰閸パ冪](gdunit4-csharp-runner-integration.md) 闁?C# 闁革妇鍎ゅ▍娆徝圭€ｎ厾妲搁柛娑欏灊閹躲倗鎮扮仦鐑╁亾娴ｇ懓袚闁告稑锕ら幊锟犲触瀹ュ啠鍋撴稉鍜?鐎规悶鍎板▎銏ゅ绩閸洘鑲?

- [Phase-10-Unit-Tests.md](Phase-10-Unit-Tests.md) 闁?xUnit 闁告娲栭崢鎾趁圭€ｎ厾妲搁弶鈺€鑳朵簺
- [Phase-11-Scene-Integration-Tests-REVISED.md](Phase-11-Scene-Integration-Tests-REVISED.md) 闁?**GdUnit4 + xUnit 闁告瑥鐭佸娲捶閻戞ɑ鐝繛鏉戭儓閻?*闁挎稑鐗嗛崙锟犲绩绾懐绠婚柨娑欏哺閸ｄ即鎮?GdUnit4 闁兼澘鐭傚?GdUnit4闁挎稑鐡沞adless 濞戞挴鍋撶紒娑橆槸閸欐洖顫濋幋顖滅
- [Phase-12-Headless-Smoke-Tests.md](Phase-12-Headless-Smoke-Tests.md) 闁?**Godot Headless 闁告劖甯為崕顐⒚圭€ｎ厾妲稿☉鎾冲閳ь儸鍡楀幋闂佹彃娲▔?*闁挎稑鐗嗛幆搴ㄥ礉?闁兼寧绮屽畷?濞ｅ洠鈧啿濞?闁谎嗘閹洟宕￠弴銏㈠矗閻犲洣绶ょ槐?
- [VERIFICATION_REPORT_Phase11-12.md](VERIFICATION_REPORT_Phase11-12.md) 闁?[OK] 闁告瑯鍨甸、鎴﹀箑瑜旈悰娆戞嫚娴ｇ懓袚闁告稑顭槐姗甴ase 11-12 闁瑰灈鍋撻柡鍫灠瑜拌尙鎮扮仦閿亾瑜戦惁搴㈠鐢喚绀夌紓浣哄帶閹海鎷犻崟顐㈢€?91/100闁挎稑鏈敮褰掓嚒閹邦剛鏉介柡鍌涙灮缁?
- [CODE_EXAMPLES_VERIFICATION_Phase1-12.md](CODE_EXAMPLES_VERIFICATION_Phase1-12.md) 闁?[OK] Phase 1-12 濞寸媴绲块悥婊呯矆鏉炴壆浼愬Δ鐘茬焷閻﹀鏁嶉崼婊冩暕闁活喕绀侀悾顒勫极鐎涙ǚ鍋撹椤ュ懘寮婚妷顖滅91% 閻庣懓鏈弳锝嗘償閿旇偐绀夐悶娑栧劚閸樻牕顕欐ウ娆惧敶婵炴挸鎳庡畷鐔兼晬?

### 缂佹鍏涚花鏌ユ⒓閼告鍞介柨娑欎亢瀹告繈鏌岃箛娑欙紝缂佸倷娴囩缓鑲╃矓?
- [Phase-13-22-Planning.md](Phase-13-22-Planning.md) 闁?**Phase 13-22 閻熸瑥瀚崹婵囶殽閵婏妇浠?*闁挎稑鐗愰娑氭喆娴ｉ鐟撻柡鍌滄嚀閻秴顕ｉ埀顒勬晬?
- [Phase-13-Quality-Gates-Script.md](Phase-13-Quality-Gates-Script.md) 闁?[OK] Phase 13 閻犲浄濡囩划蹇曟喆閸曨偄鐏婇柨娑樼墣瀹告繈鏌岃箛娑欙紝缂佸倷娴囬崜濂稿嫉椤掑喚鍟庨悹浣叉缁?0濡炪倗鎳撳閬嶅礆閸洘锛岀紒鍌欑筏缁辨繄鈧懓鏈弳锝夋嚇濮橆厽鎷辩紒鈧潪鎵紣闁?
- [Phase-14-Godot-Security-Baseline.md](Phase-14-Godot-Security-Baseline.md) 闁?[OK] Phase 14 閻犲浄濡囩划蹇曟喆閸曨偄鐏婇柨娑樻箼odot 閻庣懓顦崣蹇涘春閾忕懓娈犻悹浣瑰礃椤撴悂鏁?濞戞搩浜Σ璇差嚗閳ュ磭鍘甸柨娑橆劔ecurity.cs Autoload闁?0+ GdUnit4婵炴潙顑堥惁顖炴晬?
- [VERIFICATION_REPORT_Phase13-14.md](VERIFICATION_REPORT_Phase13-14.md) 闁?[OK] Phase 13-14 缂備胶鍘ч幃搴㈩殽瀹€鍐闁硅翰鍎遍幉锟犳晬閸喐娈诲ù锝嗘尰閻忥箓寮搁崟顔炬濞寸厧搴滅槐婵堢磼閻撳孩鍊ら悹鍥у閸?94/100闁挎稑鐭佸婵嬫煂韫囨稒锛岀紒鍌欑窔閻涙瑧鎷犳笟濠勭
- [MIGRATION_FEASIBILITY_SUMMARY.md](MIGRATION_FEASIBILITY_SUMMARY.md) 闁?**妫ｅ啯灏?闁轰胶绻濈紞瀣交娴ｇ洅鈺呭矗椤栨繍鏀介柟顑懏鍋呴柛姘墛閻綊骞€?*闁挎稑鐗嗛悾顒勫极閹绢喓鈧秹鎯勯璺ㄦ闁?92/100闁靛棔鑳堕幃锝夊触閸儳宕ｉ悹鍥﹂檷閳ь兛绀侀悿鍕棘閸婄喓鐔呯紒鎯х仢濞存﹢鏁?
- [Phase-15-Performance-Budgets-and-Gates.md](Phase-15-Performance-Budgets-and-Gates.md) 闁?[OK] Phase 15 閻犲浄濡囩划蹇曟喆閸曨偄鐏婇柨娑樼墛閳ь儸鍡楀幋濡澘瀚悾缁樼▔鎼淬劍锛岀紒鍌欐缂嶅鍖栨导娆戠10濡炪倗鐡圥I闁挎稑鑻悢鈧柛鎴濇缂傛挾绮╃€ｎ偄鐦归柛妤侇殣缁?
- [Phase-16-Observability-Sentry-Integration.md](Phase-16-Observability-Sentry-Integration.md) 闁?[OK] Phase 16 閻犲浄濡囩划蹇曟喆閸曨偄鐏婇柨娑樼墕瑜拌尙鎲撮崒娑氥偞闁诡儸鍌滅憿Sentry闂傚棗妫欓崹姘舵晬?閻忕偛鍊归悘锕傚几閸曞墎绀塕elease Health闂傚倶鍔庨々锕傛晬瀹€鍕吅缂佸绀侀幃搴ｆ喆閸曞墎绀?
- [Phase-17-Build-System-and-Godot-Export.md](Phase-17-Build-System-and-Godot-Export.md) 闁?[OK] Phase 17 閻犲浄濡囩划蹇曟喆閸曨偄鐏婇柨娑樼墛閻庮垰顕欓搹褰掑厙缂備胶鍠嶇粭瀛弌dot閻庣數鍘ч崵顓㈡晬鐎规敍port_presets.cfg闂佹澘绉堕悿鍡涙晬鐎涚搨thon闁哄瀚紓鎾淬仚閸楃偛袟闁挎稑鐡榠tHub Actions鐎规悶鍎扮紞鏂棵规笟濠勭
  - Windows-only 闊浂鍋婇埀顒傚枑鐎垫艾顕ｉ弴顏嗙獥閻?[Phase-17-Windows-Only-Quickstart.md](Phase-17-Windows-Only-Quickstart.md)
- [Phase-18-Staged-Release-and-Canary-Strategy.md](Phase-18-Staged-Release-and-Canary-Strategy.md) 闁?[OK] Phase 18 閻犲浄濡囩划蹇曟喆閸曨偄鐏婇柨娑樼墕閸ㄥ酣姊奸懜娈垮斀闁告瑦鍨电粩閿嬬▔瀹ヮ槆nary缂佹稒鐗滈弳鎰版晬鐎涚棜lease鐎规悶鍎扮紞鏂棵规笟濠勭闁煎浜滄慨鈺呭疾鐎ｎ亜纾抽悷娆忓閸垶鏁嶇€涘┉闂傚棗妫欓崹姘舵晬?
- [Phase-19-Emergency-Rollback-and-Monitoring.md](Phase-19-Emergency-Rollback-and-Monitoring.md) 闁?[OK] Phase 19 閻犲浄濡囩划蹇曟喆閸曨偄鐏婇柨娑樼墕缁ㄦ煡骞€閵夈儲绀€婵犲﹥鐭粭宀勬儎閹寸偛浠橀柨娑樼焷閸ゆ粓宕濋妸銊愭洟宕ｉ幋鐐寸皻闁告帟顔愮槐婕卭llbackTrigger閻犲洤瀚崣濠囨晬瀹€鈧晶妤呭嫉椤掆偓閻ｃ劑宕楅妸鈺傛嚑闁挎稑鑻ぐ鍌滄暜閸愩劋娣幖瀵稿厴濡剛绮嬫笟濠勭
- [Phase-20-Functional-Acceptance-Testing.md](Phase-20-Functional-Acceptance-Testing.md) 闁?[OK] Phase 20 閻犲浄濡囩划蹇曟喆閸曨偄鐏婇柨娑樼墕婵盯鎳楁禒瀣矗闁衡偓閼哥數銈撮悹鍥ㄦ穿缁辨繈宕跺☉姘▕閻庝絻顫夐悥锝夋晬鐏炶偐瀹夐梻鍐煐椤斿苯顔忛妷銈囩▕婵炵繝绶ょ槐婕?/P1/P2闁告帒妫涙鍥晬?
- [Phase-21-Performance-Optimization.md](Phase-21-Performance-Optimization.md) 闁?[OK] Phase 21 閻犲浄濡囩划蹇曟喆閸曨偄鐏婇柨娑樼墛閳ь儸鍡楀幋濞村吋锚鐎垫煡鏁?婵縿鍎辨导鎰媴濠婂嫮銈﹂柨娑橆劍rofiler闂傚棗妫欓崹姘舵晬?缂侇偉顔婄槐顓㈠礌閺嶎偆鎽滈柣锝冨劵缁辨徊efore/After濡ょ姴鐭侀惁澶愭晬?
  - **Phase 13**: 閻犳劑鍔戦崳娲⒒閵娧屾矗闁煎瓨纰嶅﹢浼存晬閸хnit + GdUnit4 + SonarQube闁?
  - **Phase 14**: Godot 閻庣懓顦崣蹇涘春閾忕懓娈犻柨娑樻汞ecurity.cs + 閻庡銈庡悁闁?
  - **Phase 15**: 闁诡儸鍡楀幋濡澘瀚悾缁樼▔鎼淬劍锛岀紒鍌欑筏缁辨┊erformanceTracker + 闁糕晛鎼崳顖炲炊閻愯尙绉洪柨?
  - **Phase 16**: 闁告瑯鍨甸～鍥圭€ｎ偀鍋撹缁?Sentry闁挎稑婀servability.cs + Release Health闁?
  - **Phase 17**: 闁哄瀚紓鎾跺寲閼姐倗鍩犻柨娑樻箼odot Export + .exe 闁瑰灚鎸哥€垫﹢鏁?
  - **Phase 18**: 闁告帒妫濆Ο浣糕枔闂堟稑绲洪悽顖氬枦缁辨anary/Beta/Stable闁?
  - **Phase 19**: 閹煎瓨姊归埀顑惧劚濞叉牕顭ㄥ鍓х闁煎浜滄慨鈺呭炊閻愬娉?+ 闁烩晜鍨剁敮鍫曟晬?
  - **Phase 20**: 闁告梻鍠曢崗妯活殽鐏炵偓鏆柨娑樼墦閳ь剚鍔曟慨娑㈡嚄閽樺鍤犻柡宥呮喘閻涙瑧鎷犳笟濠勭
  - **Phase 21**: 闁诡儸鍡楀幋濞村吋锚鐎垫煡鏁嶉崷顧竜filer 闁告帒妫欓悗?+ 濞村吋锚鐎垫煡寮憴鍕垫敵闁?
  - **Phase 22**: 闁哄倸娲﹂妴鍌炲即鐎涙ɑ鐓€闁挎稑鐗婂〒鍓佺磼閸喓顏搁柛妤佹磻缁楀矂宕ｉ幋婵堫伌閻犲洤鐡ㄥΣ鎴︽晬?

---

## 閺夆晙鑳朵簺闁告鍠庨崹?

### 濞戞挸绉磋ぐ鏌ュ炊閻愯　鍋撻埀顒勫春閸濆嫰鐛撳ǎ鍥ㄧ箖婵?
1. **ADR 濡炵懓宕慨?*闁挎稒纰嶆晶宥夊嫉婢跺浠搁柡瀣閸犲懐绮甸弽褏绠戝銈囩帛閺屽﹥鏅?闁哄洤鐡ㄩ弻?ADR
2. **Base/Overlay 闁告帒妫涢‖?*闁挎稒顑宎se 闁哄倸娲﹂妴鍌涚┍濠靛洤鐦繛鎾虫噺绾俱儵鏁嶉崼鐔革骏 PRD 闁汇儲娲濋幎妤呮晬?
3. **闁告瑥绉撮幃婊堟煣閻愵剙澶嶅Δ鐘茬焷閻?*闁挎稒鐡朼sk 闁?ADR/CH 闁哄稄绻濋悰娆掔疀閸涙番鈧繘鏌呭宕囩畺
4. **閻犳劑鍔戦崳娲⒒閵娧屾矗濞戞挸绉瑰椋庣棯?*闁挎稒淇洪々顐︽儎閺嶎偄鑺?闂佹彃绉撮ˇ鏌ユ偝?濠㈣泛绉靛鍛償閿曞倹顫岄柛濠囨？缁绘岸骞愭担鐟扮仐闁圭粯鍔欓悵?

### TDD 濞村吋锚閸樻稓绮甸弽顐ｆ
1. **闁告帒妫楅惇浼存⒕閺冨偆鐎?*闁挎稒顑揳me.Core闁挎稑鐗忛崙?C#闁挎稑顦粭?Godot 濞撴碍绻嗙粋鍡欌偓鐟拌嫰閸欏繘宕氶崱娆樼€?
2. **缂佷勘鍨荤挒銏ゆ倶椤栨碍鍎曢柣?*闁挎稒鑹鹃崢娑㈠礃?xUnit 婵炴潙顑堥惁顖炴晬閸垹顒㈤柨娑橆槴閸?閻庡湱鍋熼獮鍥晬閸垼闆归柨娑橆槴閸?闂佹彃绉甸悗?
3. **闁规亽鍎辫ぐ娑樷枖閵娿儱寮?*闁挎稒纰嶆晶宥夊嫉?Godot API 闂侇偅淇虹换鍐箳閵夈儱缍撻柨娑樻箿Time/IInput/IResourceLoader闁挎稑顦靛▓褏绮?
4. **闁革妇鍎ゅ▍娆徝圭€ｎ厾妲搁柛姘捣閻?*闁挎稒纰嶉悧瀹犵疀閸愵喒鍋撻弰蹇曞竼閺夊牊鍎抽崺?80% 閻熸洖妫涘ú濠囨偝閸パ勫€甸柛鎰Х钘熼柛?GdUnit4 婵炴潙顑堥惁?

### 婵炴挻鍔樼换妯侯嚕韫囨氨璁ｇ紒澶嬫閻儳顕?
1. **闁稿繐鐗忛崙浠嬪触鎼淬垼绌?*闁挎稒鐭槐顓㈠礂閸絿璁ｇ紒澶庮唺缁楀绗熷┑濠勵洬 Godot 闁汇劌瀚崙浠嬫焻閺勫繒甯嗛柨娑樻箼ame.Core闁?
2. **闁稿繐鐗婄粊鎾触鎼粹€愁潬闁?*闁挎稒纰嶇粊瀵告嫚閺囩噥鏀遍柡瀣构缁楀矂姊婚妸褜娲ｉ柛蹇撶墛閹苯顕欓悮瀵哥闁告劕绉风缓鑲╃矓鐠佸磭鐟归柛鏂衡偓鍐差潬闁?
3. **闁稿繐鐗嗛崯瀣倻閻旈攱鍊甸柛蹇嬪姂閸?*闁挎稒顑?E 闁告瑯浜滈崢娑㈠磻濮橆剚鍎欓柛?闂侇偀鍋撻柛?闁稿繑濞婇弫顓熺┍閳ュ啿濞囬柛鎰笧閸庮偄霉鐎ｎ厾妲?
4. **闁告帒妫欓弫顕€鐛幆閭︽斀**闁挎稒鐭换姘舵偩?vitegame 濞戞捁顕ч崹搴ㄥ绩椤栥倗绀塯odotgame 闁革负鍔庣€氼厾绮╃€ｎ亜鐎婚柡鈧姘辩；闁?

### Windows 妤犵偛鍟胯ぐ瀛樺濡搫甯?
1. **闁煎瓨纰嶅﹢鏉款啅閵夈儱寰?*闁挎稒鐭槐顓㈠礂閸粌鈻忛柣?Python 3闁挎稑娼穣 -3闁挎稑顦幏?.NET CLI闁挎稑娼恛tnet闁?
2. **閻犱警鍨扮欢鐐村緞閸曨厽鍊?*闁挎稒姘ㄧ划鐑樼▔閳ь剚鎷呯捄銊︽殢缂備焦绻傞顔炬崉椤栨氨绐為柨娑樼焸娴尖晠宕?Shell 闁绘鎳撻悾鍓ф嫚椤撶喓銆?
3. **CI 缂傚倹鎸搁悺?*闁挎稒鐭槐顓㈠礌?Windows Runner 缂傚倹鎸搁悺銊х驳閺嶎偅娈ｉ柨娑樻箼odot Export Templates闁?
4. **闁稿繒鍘ч鎰板箑瑜庣粊瀵告嫚?*闁挎稒纰嶆晶宥夊嫉婢跺骸澹栭柡鍫墮濠€?Windows 11 + PowerShell 濡ょ姴鐭侀惁?

---

## 闁稿繑濞婇弫顓㈠礃瀹曞洨鎽滈柣?

### 鐎规瓕灏欓垾妯尖偓瑙勮壘閸犲懐绮?
[OK] 閺夆晜鍔橀、鎴﹀籍鐠佸湱绐桮odot 4.5闁挎稑婀痗ene Tree + Node 缂侇垵宕电划娲晬?
[OK] 濞戞挻妲掗銏㈡嚊閳ь剟鏁嶅▎? (.NET 8) 闁?鐎殿喛娅ｇ悮顐﹀垂?+ 闁瑰瓨鍔楅崯娑橆啅閵夈儱寰旈梺?
[OK] 闁告娲栭崢鎾趁圭€ｎ厾妲搁柨娑欘劤Unit + FluentAssertions + NSubstitute
[OK] 闁革妇鍎ゅ▍娆徝圭€ｎ厾妲搁柨娑欘儞dUnit4闁挎稑婀歟adless 闁告鍠撻弫鎾绘晬?
[OK] 閻熸洖妫涘ú濠囨偝閸ラ绐梒overlet闁挎稑鐗撳▔锕傚箣閹邦剙鐓?dotnet test闁?
[OK] 妤犵偛鍟胯ぐ鎾晬濮濇亼ndows Desktop闁挎稑鐗嗗畷鐔肩嵁閸愭彃閰遍梻鍕С缂嶅棙寰勫鍡樼到閹艰揪璁ｇ槐?
[OK] 闁轰胶澧楀畵浣规償閹垮嫮绐梘odot-sqlite闁挎稑婀疩Lite wrapper闁?
[OK] 閻熸瑥鍊圭粊鎾箑瑜濈槐鐧漞ntry Godot SDK + 缂備焦鎸婚悗顖炲礌閺嶃劍锛夐煫?

### 鐎垫澘鎳愰垾妯兼媼閵堝懎鏋€缂?
闁?E2E 婵℃妫欓悘锕傛晬濞嗙珡Unit4 headless vs 闁煎浜滅紓?TestRunner闁?
闁?闂傚牊鐟﹂埀顑跨閸ㄥ酣寮搁幇鍓佺獥SonarQube Community vs Cloud闁?
闁?闁诡儸鍡楀幋闁告帒妫欓悗浠嬫晬濞嗙珳dot Profiler vs 闁煎浜滅紓鎾舵媼閳╁啯顦х紓浣哄枙椤撴悂鏁?
闁?閻犙冨缁喚绮婚敍鍕€為柨娑欑摂treamTexture vs 濡澘瀚慨鐐存姜閼恒儳娼ㄧ紒娑欑墱閺嗘劙鏁?
闁?濠㈣埖姘ㄩ崵搴ｇ矙鐎ｅ墎绐梂orkerThreadPool闁挎稑鐗婄敮褰掓嚒閹板墎绀唙s Thread闁挎稑鐗婃晶婊堝礉閵娧屽悁闁荤偛妫寸槐姘舵晬?

---

## 闁哄啫鐖煎Λ鎸庡閹殿喚鏆柨娑樼墛鐎垫粓姊奸懜娈垮斀闁?

| 闂傚啳鍩栭?| 鐎规悶鍎扮紞鏃堟煂韫囥儳绀勫ù婊冩惈閵囧鏁?| 闁稿繑濞婇弫顓㈡煂瀹€鈧埢鑲╁枈?| 濡炲閰ｅ▍鎾剁驳婢跺矂鐛?|
|------|-------------|-----------|---------|
| Phase 1-3: 闁告垵妫楅ˇ顒佺▔鎼达紕鍞ㄩ幖?| 3-5 | ADR 閻庣懓鏈崹?+ 濡炪倕婀卞ú浼村礆濠靛棭娼楅柛?| 濞?|
| Phase 4-6: 闁哄秶顭堢缓鍓т沪閸屾繄璁ｇ紒?| 10-15 | Game.Core + 80% 闁告娲栭崢鎾趁圭€ｎ厾妲?| 濞?|
| Phase 7-9: UI/闁革妇鍎ゅ▍娆愭交娴ｇ洅?| 15-20 | 濞戞捁顕у┃鈧柡鍜佸灠瑜板弶娼婚幇顖ｆ斀 + 闁糕晞娅ｉ、?UI | 濡?|
| Phase 10-12: 婵炴潙顑堥惁顖炴煂瀹ュ懐绱?| 8-12 | 闁告娲栭崢?闁革妇鍎ゅ▍?E2E 闁告劖甯為崕顐︽焻濮樺磭绠?| 濞?|
| Phase 13: 閻犳劑鍔戦崳娲⒒閵娧屾矗闁煎瓨纰嶅﹢?| 4-5 | 10 濡炪倕缍婂Λ顒傜矉娴ｈ棄娈伴柛鏂诲妼鐎?+ CI 闂傚棗妫欓崹?| 濞?|
| Phase 14: Godot 閻庣懓顦崣蹇涘春閾忕懓娈?| 5-7 | Security.cs + 閻庡銈庡悁闁哄啨鍎辩换?+ 20+ 婵炴潙顑堥惁?| 濞?|
| Phase 15: 闁诡儸鍡楀幋濡澘瀚悾缁樼▔鎼淬劍锛岀紒?| 5-6 | 10 濡?KPI + 闁糕晛鎼崳顖氼嚈閾忓湱褰?+ 闁搞儳鍋涚紞濠偽涢埀顒€霉?| 濞?|
| Phase 16: 闁告瑯鍨甸～鍥圭€ｎ偀鍋撹缁?Sentry | 4-5 | Release Health 闂傚倶鍔庨々?+ 缂備焦鎸婚悗顖炲礌閺嶃劍锛夐煫?| 濞?|
| Phase 17-19: 闁哄瀚紓鎾诲矗閹存繄顏?| 3-5 | Windows .exe 闁告瑯鍨辨晶锕傚礌?+ 闁告帒妫濆Ο浣糕枔闂堟稑绲洪悽?| 濞?|
| Phase 20-22: 濡ょ姴鏈弫瑙勫濡搫顕?| 5-7 | 闁告梻鍠曢崗妯尖偓闈涚秺缂?+ 闁诡儸鍡楀幋閺夊牏鍋撻悥?| 濞?|
| **闁诡剚妲掗?* | **52-80 濠?* | **閻庣懓鏈弳锝夊礉閻旇鍘撮弶鈺€鑳朵簺 + 閻犳劑鍔戦崳鐑樼┍濠靛顔?* | 濞?|

婵炲鐓夌槐鐗堢▔婵犲懎鐗氬☉鎾虫惈瀹曠喐绂嶉崫鍕伎闁煎崬鑻导鎰媴濠婂牆娅ゅù鍏煎閻ｅ鏁嶅☉妯兼澖闂傚嫬鎳庤ぐ鏌ユ嚄閽樺绀堥柛銉ｅ灲濡诧妇鎲撮崟顑?妤犵偞鍎奸、鎴炴償?濡炲閰ｅ▍鎾寸鐎ｂ晜顐介柤鏉跨焷閻ㄧ喖寮ǎ顑藉亾?

---

## 闁告艾娴烽悽璇差潰閵夆晩鈧?
- 閻?Taskmaster 濞寸姾顕ф慨鐔兼煣閻愵剛澧″Δ鐘插缁?C# 濠靛倹鍨圭€规娊寮介敓鐘靛矗缂佹儳鍟块崣?Phase-13 闂傚倶鍔庨々锕傛晬閸ф悥ard_ci.py 闁?quality_gates.py闁挎稑顧€缁辨繈骞庨妷銉﹀暈缂備胶鍠嶇粩鎾媰閻ｅ本纾?logs/ci/YYYY-MM-DD/闁挎稑鐗嗛々?taskmaster-report.json闁靛棔鎭璷ntracts-report.json闁挎稑顧€缁?
- 閻?GdUnit4 闁革妇鍎ゅ▍娆徝圭€ｎ厾妲搁柟韬插劚閹诧繝鏁嶉崸鎻箄nit4-report.xml/json闁挎稑顦粭宀勫箑瑜戦崗姗€骞庨妷銉﹀暈闁挎稑娼積rf.json闁挎稑顦粩鎾嵁閺堢數绋婂☉鎾虫惈瑜版煡鏌呮径搴ｇ炕闁稿繈鍎扮槐鍫曞礂閵夈劋绮甸柛姘墣閸撳ジ寮甸濠勫耿
- 闁?Godot + C# 闁烩晩鍠栫紞宥囩棯閿曗偓閻ｅ墽绱掗崟顓犵煆 Contracts闁挎稑鐗嗛々?Game.Core/Contracts/**闁挎稑顧€缁辨繈鐛捄鐑樿含 CI 濞戞搩鍘烘禍?dotnet/Python 濡炵懓宕慨鈺呭冀閿熺姷宕ｅ☉鎾冲閻綊骞€濮瑰洠鍋?


1. **闂傚啫鎳撻浼村触閸曨垱鈻夋繛鍫滅祷椤曟稓绱掗崱妯荤€俊?*闁挎稒纰嶇€?Phase-1 闁?Phase-22 濡炪倕鎼花顓㈠箥瑜戦、?
2. **闁告帗绋戠紓?ADR 闁艰棄顦伴、?*闁挎稒鑹惧顒勬嚀?[Phase-2-ADR-Updates.md](Phase-2-ADR-Updates.md)
3. **闁圭⒈鍘肩紓?Godot 濡炪倕婀卞ú鐗堫殽閵婏妇浠?*闁挎稒鑹惧顒勬嚀?[Phase-3-Project-Structure.md](Phase-3-Project-Structure.md)
4. **鐎点倛娅ｉ悵娑㈠嫉閳ь剛浜?CI 缂佺媴绻濇禍?*闁挎稒鑹惧顒勬嚀?[Phase-13-Quality-Gates-Script.md](Phase-13-Quality-Gates-Script.md)

---

## 闁告瑥鍊介埀顒€鍟崇粊顐⑩攦?

### 闁告鍠栭妴宥夋儎椤旇姤鐎俊?
- [PROJECT_DOCUMENTATION_INDEX.md](../PROJECT_DOCUMENTATION_INDEX.md) 闁?vitegame 閻庣懓鏈弳锝夊棘閸ャ劊鈧倻妲愰姀鐘电┛
- [CLAUDE.md](../../CLAUDE.md) 闁?AI 濞村吋锚閸樻稑顕ｉ埀顒勫矗閹达綆娼愰柤?
- [docs/adr/](../adr/) 闁?闁绘粎澧楀﹢?ADR 閻犱焦婢樼紞宥夋晬閸︽弴R-0001~0017闁?

### Godot 閻庤蓱閺岀喓鎸ч崟顒傜埍
- [Godot 4.5 闁哄倸娲﹂妴淇?https://docs.godotengine.org/en/stable/)
  - [C# 鐎殿喒鍋撻柛娆愬灦鐎垫岸宕″?https://docs.godotengine.org/en/stable/tutorials/scripting/c_sharp/index.html)
  - [GdUnit4 闁哄倸娲﹂妴淇?https://github.com/MikeSchulze/gdUnit4)

---

> Windows-only 闊浂鍋婇埀顒傚枑鐎垫艾顕?/ Quickstart: 閻?See [Phase-17-Windows-Only-Quickstart.md](Phase-17-Windows-Only-Quickstart.md)
> 閺夆晜鐩Ο浣烘偘閵夈儱甯?/ Addendum: [Phase-17-Windows-Only-Quickstart-Addendum.md](Phase-17-Windows-Only-Quickstart-Addendum.md)

## 闁哄倹婢橀·?闁哄洤鐡ㄩ弻?ADR 缂佷究鍨圭槐鈺呮晬閸︽獣dot 閻庨潧缍婄紞鍫ユ晬?
Accepted闁挎稑鐗婇弻濠囨晬?- [ADR-0018: Godot Runtime and Distribution](../adr/ADR-0018-godot-runtime-and-distribution.md)
- [ADR-0019: Godot Security Baseline](../adr/ADR-0019-godot-security-baseline.md)
- [ADR-0020: Godot Test Strategy (TDD + GdUnit4)](../adr/ADR-0020-godot-test-strategy.md)
- [ADR-0021: C# Domain Layer Architecture](../adr/ADR-0021-csharp-domain-layer-architecture.md)
- [ADR-0022: Godot Signal System and Contracts](../adr/ADR-0022-godot-signal-system-and-contracts.md)

Addenda闁挎稑鐗愯棢闁稿繐鎳撻鈺呭及鎼搭垳绀?
- [ADR-0005 Addendum 闁?Quality Gates for Godot+C#](../adr/addenda/ADR-0005-godot-quality-gates-addendum.md)
- [ADR-0006 Addendum 闁?Data Storage for Godot](../adr/addenda/ADR-0006-godot-data-storage-addendum.md)
- [ADR-0015 Addendum 闁?Performance Budgets for Godot](../adr/addenda/ADR-0015-godot-performance-budgets-addendum.md)

### 鐎规悶鍎遍崣鍧楁煣閻愵剚鐎俊?
- [xUnit 闁哄倸娲﹂妴淇?https://xunit.net/)
- [coverlet 闁哄倸娲﹂妴淇?https://github.com/coverlet-coverage/coverlet)
- [SonarQube C# 閻熸瑥瀚崹鐥?https://rules.sonarsource.com/csharp/)
- [Sentry Godot SDK](https://docs.sentry.io/platforms/godot/)

---

> **闂佹彃绉烽々锕傚箵閹邦喓浠?*闁挎稒纰嶅﹢鐗堟交娴ｇ洅鈺冩媼閳ュ啿鐏婇柛瀣搐閻ｇ偓鎷呴悩鎻掑殥闁绘梻鍠愰崐?Godot 4.5 闁糕晞娅ｉ、鍛村箼瀹ュ嫮绋婂☉?C# 鐎殿喒鍋撻柛娆愬灟閳ь剙鍊搁々褔妫侀埀顒勫礂閵夆晜锛岄柛鈺冾攰椤斿嫰鏁嶇仦鐣岀处閻犱緡鍠栭崢娑氣偓鐟版湰閸ㄦ氨鈧蓱閺岀喖寮▎鎴旀煠闁告艾楠搁崯鈧柛姘煎灠婵晜娼绘担鐩掆晠濡?

- 导出清单：见 [Phase-17-Export-Checklist.md](Phase-17-Export-Checklist.md)
- Headless 冒烟：见 [Phase-12-Headless-Smoke-Tests.md](Phase-12-Headless-Smoke-Tests.md)

#!/usr/bin/env python3
"""Synchronize Knowledge/Impact workflow, CLI, skills, and Project Health UI.

This file intentionally patches only bounded marker/exact-match regions. It never
wholesale-replaces the template workflow or unrelated dev CLI behavior.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from patch_workflow_knowledge_impact import patch_text as patch_workflow_text
from workflow_chapter_knowledge_overlay import BEGIN as SKILL_BEGIN
from workflow_chapter_knowledge_overlay import END as SKILL_END
from workflow_chapter_knowledge_overlay import OVERLAYS
from workflow_chapter_knowledge_overlay import _strip_existing

CLI_FUNCTION_BEGIN = "# KNOWLEDGE_IMPACT_CLI_FUNCTIONS_BEGIN"
CLI_FUNCTION_END = "# KNOWLEDGE_IMPACT_CLI_FUNCTIONS_END"
CLI_PARSER_BEGIN = "    # KNOWLEDGE_IMPACT_CLI_PARSERS_BEGIN"
CLI_PARSER_END = "    # KNOWLEDGE_IMPACT_CLI_PARSERS_END"

CLI_FUNCTION_BLOCK = r'''# KNOWLEDGE_IMPACT_CLI_FUNCTIONS_BEGIN
def _knowledge_impact_script(script: str, *values: str) -> list[str]:
    return ["py", "-3", f"scripts/python/{script}", *values]


def cmd_knowledge_publish(args: argparse.Namespace) -> int:
    return run(_knowledge_impact_script("publish_knowledge_catalog.py", "--repository-root", args.repo_root, "--publish"))


def cmd_knowledge_check(args: argparse.Namespace) -> int:
    return run(_knowledge_impact_script("publish_knowledge_catalog.py", "--repository-root", args.repo_root, "--check"))


def cmd_knowledge_restore_lkg(args: argparse.Namespace) -> int:
    return run(_knowledge_impact_script("publish_knowledge_catalog.py", "--repository-root", args.repo_root, "--restore-lkg"))


def cmd_knowledge_locate(args: argparse.Namespace) -> int:
    cmd = _knowledge_impact_script(
        "knowledge_locator.py", "--repository-root", args.repo_root,
        "--consumer", args.consumer, "--query", args.query,
    )
    if args.task_id:
        cmd.extend(["--task-id", args.task_id])
    if args.require_published:
        cmd.append("--require-published")
    return run(cmd)


def cmd_knowledge_context(args: argparse.Namespace) -> int:
    cmd = _knowledge_impact_script(
        "prepare_knowledge_context.py", "--repository-root", args.repo_root,
        "--consumer", args.consumer, "--query", args.query,
    )
    if args.task_id:
        cmd.extend(["--task-id", args.task_id])
    if args.output:
        cmd.extend(["--output", args.output])
    if args.allow_unpublished:
        cmd.append("--allow-unpublished")
    return run(cmd)


def cmd_impact_build_index(args: argparse.Namespace) -> int:
    cmd = _knowledge_impact_script(
        "build_impact_index.py", "--repository-root", args.repo_root,
        "--revision", args.revision, "--output-root", args.output_root,
    )
    if args.trusted_ref:
        cmd.extend(["--trusted-ref", args.trusted_ref])
    if args.reuse_only:
        cmd.append("--reuse-only")
    return run(cmd)


def cmd_impact_analyze(args: argparse.Namespace) -> int:
    cmd = _knowledge_impact_script("analyze_impact.py", "--repo-root", args.repo_root, "--target", args.target)
    if args.strict:
        cmd.append("--strict")
    if args.frozen_context:
        cmd.extend(["--frozen-context", args.frozen_context])
    if args.output:
        cmd.extend(["--output", args.output])
    return run(cmd)
# KNOWLEDGE_IMPACT_CLI_FUNCTIONS_END'''

CLI_PARSER_BLOCK = r'''    # KNOWLEDGE_IMPACT_CLI_PARSERS_BEGIN
    knowledge_consumers = ["repository-session", "chapter4", "chapter5", "chapter6", "review"]

    p_kpub = sub.add_parser("knowledge-publish", help="publish a hash-bound Knowledge generation from trusted local main")
    p_kpub.add_argument("--repo-root", default=".")
    p_kpub.set_defaults(func=cmd_knowledge_publish)

    p_kcheck = sub.add_parser("knowledge-check", help="validate the current Knowledge publication and its hashes")
    p_kcheck.add_argument("--repo-root", default=".")
    p_kcheck.set_defaults(func=cmd_knowledge_check)

    p_klkg = sub.add_parser("knowledge-restore-lkg", help="restore Knowledge current pointer from last-known-good after validation")
    p_klkg.add_argument("--repo-root", default=".")
    p_klkg.set_defaults(func=cmd_knowledge_restore_lkg)

    p_klocate = sub.add_parser("knowledge-locate", help="locate policy-aware candidate evidence without semantic acceptance")
    p_klocate.add_argument("--repo-root", default=".")
    p_klocate.add_argument("--consumer", default="repository-session", choices=knowledge_consumers)
    p_klocate.add_argument("--query", required=True)
    p_klocate.add_argument("--task-id", default="")
    p_klocate.add_argument("--require-published", action="store_true")
    p_klocate.set_defaults(func=cmd_knowledge_locate)

    p_kcontext = sub.add_parser("knowledge-context", help="prepare consumer-scoped Knowledge candidates for explicit decisions/freeze")
    p_kcontext.add_argument("--repo-root", default=".")
    p_kcontext.add_argument("--consumer", required=True, choices=knowledge_consumers)
    p_kcontext.add_argument("--query", required=True)
    p_kcontext.add_argument("--task-id", default="")
    p_kcontext.add_argument("--output", default="")
    p_kcontext.add_argument("--allow-unpublished", action="store_true")
    p_kcontext.set_defaults(func=cmd_knowledge_context)

    p_iindex = sub.add_parser("impact-build-index", help="build/reuse an immutable revision-bound Impact Index")
    p_iindex.add_argument("--repo-root", default=".")
    p_iindex.add_argument("--revision", required=True)
    p_iindex.add_argument("--trusted-ref", default="refs/heads/main")
    p_iindex.add_argument("--output-root", default="logs/ci")
    p_iindex.add_argument("--reuse-only", action="store_true")
    p_iindex.set_defaults(func=cmd_impact_build_index)

    p_impact = sub.add_parser("impact-analyze", help="run exploratory or frozen-context strict Impact analysis")
    p_impact.add_argument("--repo-root", default=".")
    p_impact.add_argument("--target", required=True)
    p_impact.add_argument("--strict", action="store_true")
    p_impact.add_argument("--frozen-context", default="")
    p_impact.add_argument("--output", default="")
    p_impact.set_defaults(func=cmd_impact_analyze)
    # KNOWLEDGE_IMPACT_CLI_PARSERS_END'''


def _remove_marker_block(text: str, begin: str, end: str) -> str:
    while begin in text and end in text:
        start = text.index(begin)
        finish = text.index(end, start) + len(end)
        text = text[:start].rstrip() + "\n\n" + text[finish:].lstrip("\n")
    return text


def expected_dev_cli(text: str) -> str:
    text = _remove_marker_block(text, CLI_FUNCTION_BEGIN, CLI_FUNCTION_END)
    text = _remove_marker_block(text, CLI_PARSER_BEGIN, CLI_PARSER_END)
    function_anchor = "def build_parser() -> argparse.ArgumentParser:\n"
    index = text.find(function_anchor)
    if index < 0:
        raise ValueError("dev_cli.py build_parser anchor not found")
    text = text[:index].rstrip() + "\n\n\n" + CLI_FUNCTION_BLOCK + "\n\n\n" + text[index:]
    parser_anchor = "    # run-chapter7-ui-wiring\n"
    index = text.find(parser_anchor)
    if index < 0:
        raise ValueError("dev_cli.py Chapter 7 parser anchor not found")
    text = text[:index].rstrip() + "\n\n" + CLI_PARSER_BLOCK + "\n\n" + text[index:]
    return text


def _replace_once_or_current(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise ValueError(f"Project Health JS patch anchor missing: {label}")
    return text.replace(old, new, 1)


def expected_project_health_js(text: str) -> str:
    old_image = """function imageLink(path) {
  const wrapper=document.createElement('span');wrapper.className='image-reference';const link=document.createElement('a');link.textContent=path;link.href='/api/knowledge/image?path='+encodeURIComponent(path);link.target='_blank';link.rel='noopener';"""
    new_image = """function imageLink(path) {
  const wrapper=document.createElement('span');wrapper.className='image-reference';const link=document.createElement('a');link.textContent=path;const revision=activeTaskDetail?.revision ? '&revision='+encodeURIComponent(activeTaskDetail.revision) : '';link.href='/api/knowledge/image?path='+encodeURIComponent(path)+revision;link.target='_blank';link.rel='noopener';"""
    text = _replace_once_or_current(text, old_image, new_image, "snapshot-bound image link")

    old_scene = """  navGroup(box,'场景与节点',nav.scenes,(section,item)=>{const d=document.createElement('details');const s=document.createElement('summary');s.textContent=`${item.path} · ${item.evidence_kind}`;d.append(s,sourceButton(item.path,'Open scene source'));for(const node of item.nodes || []){const nd=document.createElement('details');const ns=document.createElement('summary');ns.textContent=`${node.node_path} (${node.type}) · line ${node.line}`;nd.append(ns);for(const prop of node.properties || []){textParagraph(nd,`${prop.name} = ${prop.value} · line ${prop.line}`,'field-help');renderResourceChain(nd,prop.resources);}renderResourceChain(nd,node.instance);d.append(nd);}section.append(d);});"""
    new_scene = """  navGroup(box,'场景与节点',nav.scenes,(section,item)=>{const d=document.createElement('details');const s=document.createElement('summary');s.textContent=`${item.path} · ${item.evidence_kind}`;const semantic=semanticEntry(data,'scene',item.path);d.append(s,sourceButton(item.path,'Open scene source'));if(semantic){textParagraph(d,'Generated semantic note (non-authoritative): '+String(semantic.explanation || ''));if(semantic.modification_guidance)textParagraph(d,'Modification guidance: '+semantic.modification_guidance,'field-help');if(semantic.modification_impact)textParagraph(d,'Modification impact: '+semantic.modification_impact,'field-help');}for(const node of item.nodes || []){const nd=document.createElement('details');const ns=document.createElement('summary');ns.textContent=`${node.node_path} (${node.type}) · line ${node.line}`;nd.append(ns);const binding=(semantic?.bindings || []).find(row=>row.node_path===node.node_path && Number(row.line)===Number(node.line));if(binding)textParagraph(nd,'Semantic binding: '+String(binding.meaning || ''),'field-help');for(const prop of node.properties || []){textParagraph(nd,`${prop.name} = ${prop.value} · line ${prop.line}`,'field-help');renderResourceChain(nd,prop.resources);}renderResourceChain(nd,node.instance);d.append(nd);}section.append(d);});"""
    text = _replace_once_or_current(text, old_scene, new_scene, "scene semantic evidence")

    old_asset = """  navGroup(box,'素材',nav.assets,(section,item)=>{const d=document.createElement('details');const s=document.createElement('summary');if(/\\.(png|jpe?g|webp|svg)$/i.test(item.path))s.append(imageLink(item.path),document.createTextNode(` · ${item.evidence_kind}`));else s.textContent=`${item.path} · ${item.evidence_kind}`;d.append(s);for(const user of item.users || [])textParagraph(d,`${user.source}:${user.line} · ${user.evidence}`,'field-help');section.append(d);});"""
    new_asset = """  navGroup(box,'素材',nav.assets,(section,item)=>{const d=document.createElement('details');const s=document.createElement('summary');const semantic=semanticEntry(data,'asset',item.path);if(/\\.(png|jpe?g|webp|svg)$/i.test(item.path))s.append(imageLink(item.path),document.createTextNode(` · ${item.evidence_kind}`));else s.textContent=`${item.path} · ${item.evidence_kind}`;d.append(s);if(semantic){textParagraph(d,'Generated semantic note (non-authoritative): '+String(semantic.explanation || ''));if(semantic.modification_guidance)textParagraph(d,'Modification guidance: '+semantic.modification_guidance,'field-help');if(semantic.modification_impact)textParagraph(d,'Modification impact: '+semantic.modification_impact,'field-help');}for(const user of item.users || []){textParagraph(d,`${user.source}:${user.line} · ${user.evidence}`,'field-help');const binding=(semantic?.bindings || []).find(row=>row.source===user.source && Number(row.line)===Number(user.line));if(binding)textParagraph(d,'Semantic binding: '+String(binding.meaning || ''),'field-help');}section.append(d);});"""
    text = _replace_once_or_current(text, old_asset, new_asset, "asset semantic evidence")

    old_resource = """  if(data.resource_knowledge){const d=document.createElement('details');const s=document.createElement('summary');s.textContent='Reviewed resource knowledge';const pre=document.createElement('pre');pre.textContent=pretty(data.resource_knowledge);d.append(s,pre);box.append(d);} """.rstrip()
    new_resource = """  if(data.resource_knowledge){const d=document.createElement('details');const s=document.createElement('summary');s.textContent='Reconstructed task-resource knowledge';const pre=document.createElement('pre');pre.textContent=pretty(data.resource_knowledge);d.append(s,pre);box.append(d);}
  if(data.reviewed_resources){const d=document.createElement('details');const s=document.createElement('summary');s.textContent='Explicit reviewed resources';const pre=document.createElement('pre');pre.textContent=pretty(data.reviewed_resources);d.append(s,pre);box.append(d);}"""
    text = _replace_once_or_current(text, old_resource, new_resource, "resource knowledge labels")
    return text


def expected_skill(text: str, body: str) -> str:
    cleaned = _strip_existing(text)
    anchor = "\n## Idempotent Procedure\n"
    if anchor not in cleaned:
        raise ValueError("skill Idempotent Procedure anchor not found")
    block = f"\n{SKILL_BEGIN}\n{body.rstrip()}\n{SKILL_END}\n"
    return cleaned.replace(anchor, block + anchor, 1)


def collect_expected(root: Path) -> dict[Path, str]:
    files: dict[Path, str] = {}
    workflow = root / "workflow.md"
    files[workflow] = patch_workflow_text(workflow.read_text(encoding="utf-8"))

    dev_cli = root / "scripts/python/dev_cli.py"
    files[dev_cli] = expected_dev_cli(dev_cli.read_text(encoding="utf-8"))

    javascript = root / "scripts/python/project_health_knowledge.js"
    files[javascript] = expected_project_health_js(javascript.read_text(encoding="utf-8"))

    for name, body in OVERLAYS.items():
        path = root / ".agents/skills" / name / "SKILL.md"
        files[path] = expected_skill(path.read_text(encoding="utf-8"), body)
    return files


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    root = args.repo_root.resolve()
    expected = collect_expected(root)
    changed = []
    for path, target in expected.items():
        current = path.read_text(encoding="utf-8")
        if current == target:
            continue
        changed.append(path.relative_to(root).as_posix())
        if args.write:
            path.write_text(target, encoding="utf-8", newline="\n")
    print(json.dumps({"status": "current" if not changed else ("updated" if args.write else "stale"), "changed": changed}, ensure_ascii=False, indent=2))
    return 1 if args.check and changed else 0


if __name__ == "__main__":
    raise SystemExit(main())

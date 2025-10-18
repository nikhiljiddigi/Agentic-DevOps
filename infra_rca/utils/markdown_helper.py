def build_markdown_generic(kind, name, namespace, root_cause, reasoning, recommendations, patch_yaml, category=None):
    lines = [
        f"# RCA Report for {kind}: `{name}`" + (f" (Namespace: `{namespace}`)" if namespace else ""),
    ]

    if category:
        lines.append(f"### 🧩 Category: {category}")

    lines.append("\n## 🧠 Root Cause\n" + root_cause)
    lines.append("\n## 💡 Reasoning\n" + reasoning)
    lines.append("\n## 🛠 Recommendations\n" + "\n".join(f"- {r}" for r in recommendations))

    # Add patch section only if meaningful
    if patch_yaml and not patch_yaml.strip().startswith("# No manifest change") and patch_yaml.strip():
        lines.append("\n## 🧩 Suggested Manifest Patch\n```yaml\n" + patch_yaml.strip() + "\n```")

    return "\n".join(lines)

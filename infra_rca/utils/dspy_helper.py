"""
InfraRCAHelper
---------------
Unified helper for Agentic Infra RCA reasoning using Gemini models.
• Works with gemini-2.5-flash (fast) and gemini-1.5-pro (deep)
• Structured outputs: root cause, reasoning, recommendations, patch
• Safe parsing + fallback + verbose debug logging
"""

import os
import google.generativeai as genai
import time


class InfraRCAHelper:
    def __init__(self, primary_model="gemini-2.5-flash", fallback_model="gemini-1.5-pro-latest"):
        key = os.getenv("GEMINI_API_KEY")
        if not key:
            raise EnvironmentError("❌ Missing GEMINI_API_KEY")
        genai.configure(api_key=key)

        self.primary_model_name = primary_model
        self.fallback_model_name = fallback_model
        self.primary = genai.GenerativeModel(primary_model)
        self.fallback = genai.GenerativeModel(self.fallback_model_name)

    # ------------------------------------------------------------------ #
    # Prompt construction
    # ------------------------------------------------------------------ #
    def build_prompt(self, kind: str, name: str, namespace: str, describe: str, events: str, logs: str, metrics: str, signals: str) -> str:
        """Compose structured RCA reasoning prompt."""
        return f"""
You are an expert Site Reliability Engineer performing Root Cause Analysis on Kubernetes infrastructure.

### Context
Resource Kind: {kind}
Name: {name}
Namespace: {namespace}
Detected Signals: {signals}

### Cluster Describe
{describe}

### Events
{events}

### Logs
{logs}

### Metrics
{metrics}

---

### Instruction
Analyze the above data and identify:
1. Root cause — concise one-line diagnosis.
2. RCA Category: <Infra | Config | Application | Network | Image | Resource>
3. Reasoning — 2-5 sentence summary explaining the causal chain.
4. Recommendations — bullet points of actionable fixes.
5.  YAML patch — minimal manifest changes to remediate (if relevant).  
If no manifest change is required (e.g., node or service issue), respond with:
`Patch: # none`


Respond **exactly** in this format:

Root Cause: <one-line>
RCA Category: <Infra | Config | Application | Network | Image | Resource>
Reasoning: <multi-line short paragraph>
Recommendations:
- <item1>
- <item2>
Patch:
```yaml
<YAML fix or leave '# none'>
"""

    # ------------------------------------------------------------------ #
    # Main reasoning method
    # ------------------------------------------------------------------ #
    def run_rca(self, kind, name, namespace, describe, events, logs, metrics, signals) -> dict:
        """
        Run RCA reasoning with robust parsing, smart retry, and YAML cleanup.
        Supports multi-model fallback (Gemini flash → pro) and patch extraction.
        """
        import re
        from time import sleep

        # 1️⃣ --- Prompt generation ---
        prompt = self.build_prompt(kind, name, namespace, describe, events, logs, metrics, signals)

        # 2️⃣ --- Primary generation ---
        text = self._generate(prompt, self.primary)
        if not text or text.startswith("[Gemini error"):
            print("⚠️ Retrying with fallback model:", getattr(self.fallback, "model_name", "gemini-1.5-pro"))
            text = self._generate(prompt, self.fallback)

        print("\n🧠 Raw Gemini RCA Output:\n", text, "\n")

        # 3️⃣ --- Initialize parsed fields ---
        fields = {
            "root_cause": "",
            "reasoning": "",
            "recommendations": [],
            "patch_yaml": "",
            "category": "",
        }

        patch_lines = []
        capture_patch = False
        capture_recs = False
        reasoning_lines = []

        # 4️⃣ --- Parse model output ---
        for raw_line in text.splitlines():
            line = raw_line.strip()
            low = line.lower()

            if not line:
                continue

            if low.startswith("root cause:"):
                fields["root_cause"] = line.split(":", 1)[1].strip()
                capture_patch = capture_recs = False

            elif low.startswith("rca category:") or low.startswith("category:"):
                cat = line.split(":", 1)[1].strip().capitalize()
                if "network" in cat:
                    fields["category"] = "Network Issue"
                elif "image" in cat:
                    fields["category"] = "Image Issue"
                elif "resource" in cat:
                    fields["category"] = "Resource Pressure"
                elif "application" in cat:
                    fields["category"] = "Application Failure"
                elif "probe" in cat:
                    fields["category"] = "Health Probe Failure"
                else:
                    fields["category"] = cat

            elif low.startswith("reasoning:"):
                fields["reasoning"] = line.split(":", 1)[1].strip()
                reasoning_lines.append(fields["reasoning"])
                capture_patch = capture_recs = False

            elif low.startswith("recommendations:"):
                capture_recs = True
                capture_patch = False

            elif low.startswith("patch:") or low.startswith("suggested manifest patch:"):
                capture_patch = True
                capture_recs = False

            elif capture_recs and line.startswith("- "):
                rec = line[2:].strip()
                if rec and not rec.lower().startswith("name:"):
                    fields["recommendations"].append(rec)

            elif capture_patch:
                patch_lines.append(line)

            else:
                reasoning_lines.append(line)

        # 5️⃣ --- Fallback regex extraction for RootCause/Reasoning/Rec/Patch ---
        if not fields["root_cause"]:
            rc_match = re.search(r"Root\s*Cause\s*:\s*(.*?)(?:Reasoning:|Recommendations:|Patch:|$)",
                                text, re.IGNORECASE | re.DOTALL)
            if rc_match:
                fields["root_cause"] = rc_match.group(1).strip()

        if not fields["reasoning"]:
            r_match = re.search(r"Reasoning\s*:\s*(.*?)(?:Recommendations:|Patch:|$)",
                                text, re.IGNORECASE | re.DOTALL)
            if r_match:
                fields["reasoning"] = r_match.group(1).strip()
            else:
                fields["reasoning"] = "\n".join(reasoning_lines).strip()

        if not fields["recommendations"]:
            recs = re.findall(r"-\s+([^\n]+)", text)
            fields["recommendations"] = [r.strip() for r in recs if r.strip()] or ["No actionable recommendations found."]

        # Extract YAML from fenced blocks
        fence_pattern = re.compile(r"```(?:yaml)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)
        fenced = fence_pattern.findall(text)
        for block in fenced:
            if re.search(r"\b(spec|containers|image|metadata|apiVersion)\b", block):
                patch_lines.append(block.strip())

        # Combine all patch sections
        patch_yaml = "\n\n".join([p for p in patch_lines if p.strip()])

        # 6️⃣ --- Patch cleanup (dedup + strip fences) ---
        patch_yaml = patch_yaml.strip()
        patch_yaml = re.sub(r"```+yaml", "", patch_yaml)
        patch_yaml = re.sub(r"```+", "", patch_yaml)

        # Deduplicate repeated lines
        seen = set()
        clean_lines = []
        for line in patch_yaml.splitlines():
            if line.strip() not in seen:
                seen.add(line.strip())
                clean_lines.append(line)
        patch_yaml = "\n".join(clean_lines).strip()

        # Keep longest YAML block if multiple
        yaml_blocks = re.findall(r"(spec:.*?)(?=\n\S|$)", patch_yaml, flags=re.DOTALL)
        if len(yaml_blocks) > 1:
            patch_yaml = max(yaml_blocks, key=len).strip()

        if not patch_yaml or patch_yaml.lower() in ["# none", "none", ""]:
            patch_yaml = "# none"
        fields["patch_yaml"] = patch_yaml

        # 7️⃣ --- Category heuristics if empty ---
        combined_text = (fields["root_cause"] + " " + fields["reasoning"]).lower()
        if not fields["category"]:
            if any(k in combined_text for k in ("imagepull", "imagepullbackoff", "errimagepull", "image not found", "failed to pull")):
                fields["category"] = "Image Issue"
            elif any(k in combined_text for k in ("probe", "readiness", "liveness")):
                fields["category"] = "Health Probe Failure"
            elif any(k in combined_text for k in ("memory", "oom", "pressure", "oomkilled", "out of memory")):
                fields["category"] = "Resource Pressure"
            elif any(k in combined_text for k in ("dns", "connection", "timeout")):
                fields["category"] = "Network Issue"
            else:
                fields["category"] = "General Anomaly"

        # 8️⃣ --- Smart Retry (only if too generic or no actions) ---
        retry_needed = False
        if ("not identified" in fields["root_cause"].lower()) or (
            any("no actionable" in r.lower() for r in fields["recommendations"])
        ):
            retry_needed = True

        if retry_needed:
            print("🔁 RCA result too weak — retrying with refined prompt (deep mode)...")
            refined_prompt = (
                f"Focus only on finding a concrete root cause and actionable fix.\n"
                f"If metrics or events imply a cause, infer it.\n"
                f"Object: {kind}/{name} (ns={namespace})\n"
                f"Describe:\n{describe}\n\nEvents:\n{events}\n\nLogs:\n{logs}\n\nMetrics:\n{metrics}\n\nSignals:\n{signals}\n"
            )
            sleep(2)
            retry_text = self._generate(refined_prompt, self.fallback)
            print("🧠 Retry Gemini Output:\n", retry_text, "\n")

            rc_match = re.search(r"Root\s*Cause\s*:\s*(.*?)(?:\n|$)", retry_text, re.IGNORECASE)
            recs = re.findall(r"-\s+(.*)", retry_text)
            if rc_match:
                fields["root_cause"] = rc_match.group(1).strip()
            if recs:
                fields["recommendations"] = [r.strip() for r in recs if r.strip()]

            if not fields["root_cause"]:
                fields["root_cause"] = "Root cause could not be inferred even after retry."
            if not fields["recommendations"]:
                fields["recommendations"] = ["Manual investigation recommended."]

        # 9️⃣ --- Final validation
        if not fields["root_cause"]:
            fields["root_cause"] = "Root cause not identified."
        if not fields["reasoning"]:
            fields["reasoning"] = "No reasoning extracted from RCA output."

        print("🧩 Parsed RCA fields:",
            {k: (v[:100] + "..." if isinstance(v, str) and len(v) > 100 else v)
            for k, v in fields.items()})

        return fields


    # ------------------------------------------------------------------ #
    # Updated _generate with variable temperature
    # ------------------------------------------------------------------ #
    def _generate(self, prompt: str, model, temperature=0.5) -> str:
        """Safe Gemini generation with adjustable creativity."""
        try:
            resp = model.generate_content(
                contents=[{"role": "user", "parts": [{"text": prompt}]}],
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": 4096,
                    "top_p": 0.9,
                },
                safety_settings={
                    "HARASSMENT": "BLOCK_NONE",
                    "HATE": "BLOCK_NONE",
                    "SEXUAL": "BLOCK_NONE",
                    "DANGEROUS": "BLOCK_NONE",
                },
            )

            if hasattr(resp, "resolve"):
                try:
                    resp.resolve()
                except Exception:
                    pass

            if hasattr(resp, "text") and resp.text:
                return resp.text.strip()

            if hasattr(resp, "candidates") and resp.candidates:
                candidate = resp.candidates[0]
                if hasattr(candidate, "content") and candidate.content and candidate.content.parts:
                    return "\n".join([p.text for p in candidate.content.parts if hasattr(p, "text")]).strip()
                finish_reason = getattr(candidate, "finish_reason", "unknown")
                return f"(Gemini returned no text. finish_reason={finish_reason})"

            return "No valid Gemini response."

        except Exception as e:
            return f"[Gemini error: {e}]"

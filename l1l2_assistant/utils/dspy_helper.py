"""
DSPyHelper
-----------
Unified helper for Agentic L1/L2 triage reasoning using Gemini models.
• Works with gemini-2.5-flash (fast) and gemini-1.5-pro (deep)
• Provides structured reasoning outputs
• Safe parsing + model fallback
"""

import os
import google.generativeai as genai


class DSPyHelper:
    def __init__(self, primary_model="gemini-2.5-flash", fallback_model="gemini-1.5-pro"):
        key = os.getenv("GEMINI_API_KEY")
        if not key:
            raise EnvironmentError("❌ Missing GEMINI_API_KEY")
        genai.configure(api_key=key)

        self.primary_model_name = primary_model
        self.fallback_model_name = fallback_model
        self.primary = genai.GenerativeModel(primary_model)
        self.fallback = genai.GenerativeModel(fallback_model)

    # ------------------------------------------------------------------ #
    # Prompt construction
    # ------------------------------------------------------------------ #
    def build_prompt(self, title: str, body: str, kb: str) -> str:
        """Rich reasoning instruction prompt with example."""
        return f"""
You are an experienced Site Reliability Engineer performing incident triage.

### Example
Incident: Database connection timeout
Severity: Medium
Probable Cause: Connection pool exhaustion under heavy load.
Recommended Fix: Increase max connections and add retry logic.
Resolution Time: 30 minutes

---

### New Incident
Title: {title}

Description and Logs:
{body}

Knowledge Base Reference:
{kb}

Respond **exactly** in this format:

Severity: <Low/Medium/High/Critical>
Probable Cause: <1–2 concise technical sentences>
Recommended Fix: <clear actionable remediation steps>
Resolution Time: <estimate like '30m', '2h', '1 day'>
"""

    # ------------------------------------------------------------------ #
    # Core reasoning call
    # ------------------------------------------------------------------ #
    def run_reasoning(self, title: str, body: str, kb: str, timestamp: str) -> dict:
        """Generate structured triage output with automatic fallback."""
        prompt = self.build_prompt(title, body, kb)

        text = self._generate(prompt, self.primary)
        if not text or "[Empty" in text or text.startswith("[Gemini error"):
            print("⚠️ Retrying with fallback model:", self.fallback_model_name)
            text = self._generate(prompt, self.fallback)

        fields = {"severity": "", "probable_cause": "", "recommended_fix": "", "resolution_time": ""}
        for line in text.splitlines():
            l = line.strip()
            if l.lower().startswith("severity:"):
                fields["severity"] = l.split(":", 1)[1].strip()
            elif l.lower().startswith("probable cause:"):
                fields["probable_cause"] = l.split(":", 1)[1].strip()
            elif l.lower().startswith("recommended fix:"):
                fields["recommended_fix"] = l.split(":", 1)[1].strip()
            elif l.lower().startswith("resolution time:"):
                fields["resolution_time"] = l.split(":", 1)[1].strip()

        print("\n🧩 Raw Gemini Output:\n", text, "\n")
        return fields

    # ------------------------------------------------------------------ #
    # Internal generation util
    # ------------------------------------------------------------------ #
    def _generate(self, prompt: str, model) -> str:
        """Low-level Gemini call with safe parsing."""
        try:
            resp = model.generate_content(
                contents=[{"role": "user", "parts": [{"text": prompt}]}],
                generation_config={
                    "temperature": 0.8,
                    "max_output_tokens": 2048,
                    "top_p": 0.9,
                },
            )

            # Extract text safely
            if hasattr(resp, "text") and resp.text:
                return resp.text.strip()
            if hasattr(resp, "candidates") and resp.candidates:
                parts = resp.candidates[0].content.parts
                return "\n".join([p.text for p in parts if hasattr(p, "text")]).strip()
            return str(resp)
        except Exception as e:
            return f"[Gemini error: {e}]"


# ---------------------------------------------------------------------- #
# Local quick test
# ---------------------------------------------------------------------- #
if __name__ == "__main__":
    helper = DSPyHelper()
    title = "High CPU usage on worker node"
    body = (
        "Prometheus alert: CPU usage above 95% for 10m on worker-3.\n"
        "Java process using 320% CPU; pods restarting with GC overhead errors."
    )
    kb = "KB: High CPU Usage — verify CPU limits and JVM heap size."
    ts = "2025-10-18T14:45:00Z"

    result = helper.run_reasoning(title, body, kb, ts)

    print("🧠 Reasoning Output\n------------------")
    for k, v in result.items():
        print(f"{k}: {v}")

# { "Depends": "py-genlayer:test" }

import json
from genlayer import *


class LegalAnalyzer(gl.Contract):

    owner: Address
    analysis_counter: u256
    analysis_data: DynArray[str]

    def __init__(self, owner_address: Address):
        self.owner = owner_address
        self.analysis_counter = u256(0)

    @gl.public.view
    def get_analysis(self, analysis_id: str) -> str:
        title = self._get(analysis_id, "title")
        if not title:
            return "Analysis not found"
        return (
            f"ID: {analysis_id} | "
            f"Title: {title} | "
            f"Status: {self._get(analysis_id, 'status')} | "
            f"Risk Level: {self._get(analysis_id, 'risk_level')} | "
            f"Favorable For: {self._get(analysis_id, 'favorable_for')} | "
            f"Financial Risk: {self._get(analysis_id, 'financial_risk')} | "
            f"Liability Risk: {self._get(analysis_id, 'liability_risk')} | "
            f"IP Risk: {self._get(analysis_id, 'ip_risk')} | "
            f"Termination Risk: {self._get(analysis_id, 'termination_risk')} | "
            f"Red Flags: {self._get(analysis_id, 'red_flags')} | "
            f"Recommendations: {self._get(analysis_id, 'recommendations')} | "
            f"Summary: {self._get(analysis_id, 'summary')}"
        )

    @gl.public.view
    def get_analysis_count(self) -> u256:
        return self.analysis_counter

    @gl.public.view
    def get_summary(self) -> str:
        return (
            f"GenLayer AI Legal Contract Analyzer v2\n"
            f"Total Analyses: {int(self.analysis_counter)}"
        )

    @gl.public.write
    def submit_contract(
        self,
        title: str,
        party_a: str,
        party_b: str,
        contract_url: str,
        analysis_focus: str,
    ) -> str:
        assert len(title) >= 5, "Title too short"
        assert len(contract_url) >= 10, "Contract URL too short"
        assert len(analysis_focus) >= 10, "Analysis focus too short"

        analysis_id = str(int(self.analysis_counter))
        caller = str(gl.message.sender_address)

        self._set(analysis_id, "title", title)
        self._set(analysis_id, "party_a", party_a)
        self._set(analysis_id, "party_b", party_b)
        self._set(analysis_id, "contract_url", contract_url)
        self._set(analysis_id, "analysis_focus", analysis_focus[:300])
        self._set(analysis_id, "submitter", caller)
        self._set(analysis_id, "status", "pending")
        self._set(analysis_id, "risk_level", "")
        self._set(analysis_id, "favorable_for", "")
        self._set(analysis_id, "financial_risk", "")
        self._set(analysis_id, "liability_risk", "")
        self._set(analysis_id, "ip_risk", "")
        self._set(analysis_id, "termination_risk", "")
        self._set(analysis_id, "red_flags", "")
        self._set(analysis_id, "recommendations", "")
        self._set(analysis_id, "summary", "")

        self.analysis_counter = u256(int(self.analysis_counter) + 1)
        return f"Contract {analysis_id} submitted for analysis: {title}"

    @gl.public.write
    def analyze(self, analysis_id: str) -> str:
        assert self._get(analysis_id, "status") == "pending", "Analysis is not pending"

        title = self._get(analysis_id, "title")
        party_a = self._get(analysis_id, "party_a")
        party_b = self._get(analysis_id, "party_b")
        contract_url = self._get(analysis_id, "contract_url")
        analysis_focus = self._get(analysis_id, "analysis_focus")

        def leader_fn():
            web_data = ""
            try:
                response = gl.nondet.web.get(contract_url)
                raw = response.body.decode("utf-8")
                web_data = raw[:4000]
            except Exception:
                web_data = "Could not fetch contract content."

            prompt = f"""You are a senior legal analyst specializing in contract law.
Your task is to perform a structured multi-category risk analysis on the contract below.

Contract Title: {title}
Party A: {party_a}
Party B: {party_b}
User-defined analysis focus: {analysis_focus}

Contract content from {contract_url}:
{web_data}

Perform a structured analysis evaluating each of these four categories independently.

CATEGORY 1 - FINANCIAL TERMS
Look for: payment schedules, late payment penalties, currency clauses, escalation rights,
hidden fees, refund obligations, and price modification rights.
Question: Are the financial terms balanced or do they expose one party to disproportionate financial risk?

CATEGORY 2 - LIABILITY AND INDEMNIFICATION
Look for: liability caps, indemnification clauses, warranty disclaimers, exclusions of damages,
force majeure provisions, and insurance requirements.
Question: Does either party bear unlimited or unfair liability exposure?

CATEGORY 3 - INTELLECTUAL PROPERTY RIGHTS
Look for: ownership of work product, license grants, copyleft requirements, derivative works,
patent obligations, confidentiality clauses, and trademark usage.
Question: Are IP rights clearly assigned and do they restrict either party unreasonably?

CATEGORY 4 - TERMINATION AND DISPUTE RESOLUTION
Look for: termination conditions, notice periods, post-termination obligations, dispute resolution
mechanisms, governing law, and jurisdiction clauses.
Question: Can either party exit the agreement fairly and how are disputes handled?

For each category assign a risk score using these criteria:
LOW means the clauses are balanced and standard for this type of agreement.
MEDIUM means there are some unusual clauses that warrant attention but are not deal-breakers.
HIGH means there are clauses that expose one party to significant or disproportionate risk.

Respond ONLY with this JSON:
{{
  "risk_level": "MEDIUM",
  "favorable_for": "Party A",
  "financial_risk": "LOW",
  "liability_risk": "MEDIUM",
  "ip_risk": "HIGH",
  "termination_risk": "LOW",
  "red_flags": "one sentence describing the single most critical issue across all categories",
  "recommendations": "one sentence describing the most important change to negotiate",
  "summary": "two sentences summarizing the overall balance and main concerns"
}}

risk_level is the overall risk and must be exactly LOW, MEDIUM, or HIGH.
favorable_for must be exactly Party A, Party B, or Balanced.
Each category risk must be exactly LOW, MEDIUM, or HIGH.
No extra text."""

            result = gl.nondet.exec_prompt(prompt)
            clean = result.strip().replace("```json", "").replace("```", "").strip()
            data = json.loads(clean)

            risk_level = data.get("risk_level", "MEDIUM")
            favorable_for = data.get("favorable_for", "Balanced")
            financial_risk = data.get("financial_risk", "MEDIUM")
            liability_risk = data.get("liability_risk", "MEDIUM")
            ip_risk = data.get("ip_risk", "MEDIUM")
            termination_risk = data.get("termination_risk", "MEDIUM")
            red_flags = data.get("red_flags", "")
            recommendations = data.get("recommendations", "")
            summary = data.get("summary", "")

            valid_risks = ("LOW", "MEDIUM", "HIGH")
            if risk_level not in valid_risks:
                risk_level = "MEDIUM"
            if financial_risk not in valid_risks:
                financial_risk = "MEDIUM"
            if liability_risk not in valid_risks:
                liability_risk = "MEDIUM"
            if ip_risk not in valid_risks:
                ip_risk = "MEDIUM"
            if termination_risk not in valid_risks:
                termination_risk = "MEDIUM"
            if favorable_for not in ("Party A", "Party B", "Balanced"):
                favorable_for = "Balanced"

            return json.dumps({
                "risk_level": risk_level,
                "favorable_for": favorable_for,
                "financial_risk": financial_risk,
                "liability_risk": liability_risk,
                "ip_risk": ip_risk,
                "termination_risk": termination_risk,
                "red_flags": red_flags,
                "recommendations": recommendations,
                "summary": summary
            }, sort_keys=True)

        def validator_fn(leader_result) -> bool:
            if not isinstance(leader_result, gl.vm.Return):
                return False
            try:
                validator_raw = leader_fn()
                leader_data = json.loads(leader_result.calldata)
                validator_data = json.loads(validator_raw)
                if leader_data["risk_level"] != validator_data["risk_level"]:
                    return False
                if leader_data["favorable_for"] != validator_data["favorable_for"]:
                    return False
                return True
            except Exception:
                return False

        raw = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)
        data = json.loads(raw)

        self._set(analysis_id, "status", "analyzed")
        self._set(analysis_id, "risk_level", data["risk_level"])
        self._set(analysis_id, "favorable_for", data["favorable_for"])
        self._set(analysis_id, "financial_risk", data["financial_risk"])
        self._set(analysis_id, "liability_risk", data["liability_risk"])
        self._set(analysis_id, "ip_risk", data["ip_risk"])
        self._set(analysis_id, "termination_risk", data["termination_risk"])
        self._set(analysis_id, "red_flags", data["red_flags"])
        self._set(analysis_id, "recommendations", data["recommendations"])
        self._set(analysis_id, "summary", data["summary"])

        return (
            f"Analysis {analysis_id} complete. "
            f"Overall Risk: {data['risk_level']}. "
            f"Favorable for: {data['favorable_for']}. "
            f"Financial: {data['financial_risk']} | "
            f"Liability: {data['liability_risk']} | "
            f"IP: {data['ip_risk']} | "
            f"Termination: {data['termination_risk']}. "
            f"Red Flags: {data['red_flags']}. "
            f"Recommendations: {data['recommendations']}. "
            f"{data['summary']}"
        )

    def _get(self, analysis_id: str, field: str) -> str:
        key = f"{analysis_id}_{field}:"
        for i in range(len(self.analysis_data)):
            if self.analysis_data[i].startswith(key):
                return self.analysis_data[i][len(key):]
        return ""

    def _set(self, analysis_id: str, field: str, value: str) -> None:
        key = f"{analysis_id}_{field}:"
        for i in range(len(self.analysis_data)):
            if self.analysis_data[i].startswith(key):
                self.analysis_data[i] = f"{key}{value}"
                return
        self.analysis_data.append(f"{key}{value}")

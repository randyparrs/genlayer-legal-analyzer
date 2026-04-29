# { "Depends": "py-genlayer:test" }

import json
from genlayer import *


class LegalAnalyzer(gl.Contract):

    owner: Address
    analysis_counter: u256
    analysis_data: DynArray[str]

    def __init__(self, owner_address: str):
        self.owner = Address(owner_address)
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
            f"Red Flags: {self._get(analysis_id, 'red_flags')} | "
            f"Summary: {self._get(analysis_id, 'summary')}"
        )

    @gl.public.view
    def get_analysis_count(self) -> u256:
        return self.analysis_counter

    @gl.public.view
    def get_summary(self) -> str:
        return (
            f"GenLayer AI Legal Contract Analyzer\n"
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
        self._set(analysis_id, "red_flags", "")
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
                web_data = raw[:3000]
            except Exception:
                web_data = "Could not fetch contract content."

            prompt = f"""You are an AI legal analyst reviewing a contract between two parties.
Your job is to identify risks, problematic clauses, and determine which party
the contract favors based on the content provided.

Contract Title: {title}
Party A: {party_a}
Party B: {party_b}

Analysis Focus: {analysis_focus}

Contract content from {contract_url}:
{web_data}

Analyze the contract and identify the following:
1. Overall risk level for both parties
2. Which party the contract favors more
3. Any red flags or problematic clauses
4. A brief summary of the key terms

Respond ONLY with this JSON:
{{
  "risk_level": "LOW",
  "favorable_for": "Party A",
  "red_flags": "one sentence describing the main risk or problematic clause found",
  "summary": "two sentences summarizing the key terms and overall balance of the contract"
}}

risk_level must be exactly LOW, MEDIUM, or HIGH.
favorable_for must be exactly Party A, Party B, or Balanced.
No extra text."""

            result = gl.nondet.exec_prompt(prompt)
            clean = result.strip().replace("```json", "").replace("```", "").strip()
            data = json.loads(clean)

            risk_level = data.get("risk_level", "MEDIUM")
            favorable_for = data.get("favorable_for", "Balanced")
            red_flags = data.get("red_flags", "")
            summary = data.get("summary", "")

            if risk_level not in ("LOW", "MEDIUM", "HIGH"):
                risk_level = "MEDIUM"
            if favorable_for not in ("Party A", "Party B", "Balanced"):
                favorable_for = "Balanced"

            return json.dumps({
                "risk_level": risk_level,
                "favorable_for": favorable_for,
                "red_flags": red_flags,
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

        risk_level = data["risk_level"]
        favorable_for = data["favorable_for"]
        red_flags = data["red_flags"]
        summary = data["summary"]

        self._set(analysis_id, "status", "analyzed")
        self._set(analysis_id, "risk_level", risk_level)
        self._set(analysis_id, "favorable_for", favorable_for)
        self._set(analysis_id, "red_flags", red_flags)
        self._set(analysis_id, "summary", summary)

        return (
            f"Analysis {analysis_id} complete. "
            f"Risk Level: {risk_level}. "
            f"Favorable for: {favorable_for}. "
            f"Red Flags: {red_flags}. "
            f"{summary}"
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

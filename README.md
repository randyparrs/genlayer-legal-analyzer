# GenLayer AI Legal Contract Analyzer

A decentralized legal contract analyzer where AI validators read the actual contract content and identify risks, problematic clauses, and which party the agreement favors. Built on GenLayer Testnet Bradbury.

---

## What is this

Reading a legal contract and understanding the risks is something most people cannot do without hiring a lawyer. I built this to explore whether AI validators on GenLayer could analyze real contract content from a URL and give a structured risk assessment that lives onchain, verified by multiple independent validators before being committed.

The interesting part is that the AI reads the actual document, not a description of it. You submit a URL pointing to the contract, the contract fetches the content, and the AI evaluates it across four specific legal categories with concrete questions for each.

---

## How it works

You submit a contract for analysis by providing a title, the names of both parties, a URL pointing to the contract document, and a focus describing what aspects to analyze. The contract fetches that URL and an AI legal analyst evaluates the content across four structured categories.

The AI analyzes Financial Terms looking at payment schedules, late penalties, escalation rights and hidden fees. It analyzes Liability and Indemnification looking at liability caps, warranty disclaimers, force majeure provisions and insurance requirements. It analyzes Intellectual Property Rights looking at ownership of work product, license grants, copyleft requirements and confidentiality clauses. It analyzes Termination and Dispute Resolution looking at termination conditions, notice periods, dispute mechanisms and governing law.

Each category gets its own risk score of LOW, MEDIUM, or HIGH along with a specific red flag, recommendation, and summary. Multiple validators independently read the same contract and run the same analysis through Optimistic Democracy. They must agree on both the overall risk level and which party is favored before the result is committed onchain.

---

## Functions

submit_contract takes a title, the names of Party A and Party B, a URL pointing to the contract, and an analysis focus describing what to look for.

analyze takes an analysis id and triggers the AI evaluation through Optimistic Democracy. The AI fetches the contract URL, reads the content, and produces a structured risk assessment across four categories.

get_analysis shows the full result including overall risk level, which party is favored, individual risk scores for financial, liability, IP and termination categories, the main red flag identified, recommendations for negotiation, and a summary of the key terms.

get_summary shows the total number of analyses performed.

---

## Test results

Tested the analyzer with the GNU General Public License v3 from gnu.org. The AI returned a HIGH overall risk level favoring the developer (Party B) with this category breakdown: Financial Risk LOW, Liability Risk MEDIUM, IP Risk HIGH, and Termination Risk MEDIUM. The main red flag identified was that the license imposes unlimited liability on the client and restrictive copyleft obligations creating significant asymmetric risk. The recommendation was to negotiate a mutual limitation of liability and a more permissive IP license that allows proprietary use or includes clear payment terms. The summary noted that the agreement heavily favors the software developer leaving the client with substantial financial, liability, and IP risks.

The previous version returned just an overall MEDIUM risk and Balanced favorability without category breakdowns. The new structured approach catches nuances that the simpler version missed.

---

## Recent improvements

This version includes a significantly improved prompt structure based on community feedback. The original prompt was too generic and produced surface-level analyses. The new prompt provides four explicit legal categories with specific elements to look for in each, concrete questions the AI must answer per category, and clear criteria for what constitutes LOW, MEDIUM, and HIGH risk. The output now includes a per-category risk breakdown plus actionable recommendations for negotiation rather than just a single overall risk score.

---

## How to run it

Go to GenLayer Studio at https://studio.genlayer.com and create a new file called legal_analyzer.py. Paste the contract code and set execution mode to Normal Full Consensus. Deploy with your address as owner_address.

Follow this order and wait for FINALIZED at each step. Run get_summary first, then submit_contract with your contract details, then get_analysis to confirm it is pending, then analyze to trigger the AI evaluation, then get_analysis again to see the full result with the four risk categories.

For best results use URLs that point directly to plain text or simple HTML documents. PDF files and pages that require JavaScript to render may not return usable content.

Note: the contract in this repository uses the Address type in the constructor as required by genvm-lint. When deploying in GenLayer Studio use a version that receives str in the constructor and converts internally with Address(owner_address) since Studio requires primitive types to parse the contract schema correctly.

---

## Resources

GenLayer Docs: https://docs.genlayer.com

Optimistic Democracy: https://docs.genlayer.com/understand-genlayer-protocol/core-concepts/optimistic-democracy

Equivalence Principle: https://docs.genlayer.com/understand-genlayer-protocol/core-concepts/optimistic-democracy/equivalence-principle

GenLayer Studio: https://studio.genlayer.com

Discord: https://discord.gg/8Jm4v89VAu
    

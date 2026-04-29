# GenLayer IA Legal Contract Analyzer

A decentralized legal contract analyzer where AI validators read the actual contract content and identify risks, problematic clauses, and which party the agreement favors. Built on GenLayer Testnet Bradbury.

---

## What is this

Reading a legal contract and understanding the risks is something most people cannot do without hiring a lawyer. I built this to explore whether AI validators on GenLayer could analyze real contract content from a URL and give a structured risk assessment that lives onchain, verified by multiple independent validators before being committed.

The interesting part is that the AI reads the actual document, not a description of it. You submit a URL pointing to the contract, the contract fetches the content, and the AI evaluates it against whatever focus you specify, whether that is payment terms, liability clauses, intellectual property, or anything else.

---

## How it works

You submit a contract for analysis by providing a title, the names of both parties, a URL pointing to the contract document, and a focus describing what aspects to analyze. The contract fetches that URL and an AI legal analyst evaluates the content. It identifies the overall risk level, determines which party the contract favors, flags any problematic clauses, and produces a summary of the key terms.

Multiple validators independently read the same contract and run the same analysis. They must agree on both the risk level and which party is favored before the result is committed onchain. This means the analysis is not just one AI's opinion but a consensus across several independent evaluations.

---

## Functions

submit_contract takes a title, the names of Party A and Party B, a URL pointing to the contract, and an analysis focus describing what to look for.

analyze takes an analysis id and triggers the AI evaluation through Optimistic Democracy. The AI fetches the contract URL, reads the content, and produces a structured risk assessment.

get_analysis shows the full result including risk level, which party is favored, the main red flag identified, and a summary of the key terms.

get_summary shows the total number of analyses performed.

---

## Test results

First test submitted a Software Development Service Agreement using a URL that returned a 404 error. The AI correctly identified that the content was missing, flagged this as HIGH risk since no actual clauses could be reviewed, and reported it as Balanced since it could not determine favorability without the contract text. This shows the system is honest when evidence is insufficient rather than making up an analysis.

Second test submitted the GNU General Public License version 3 using the official text file from gnu.org. The AI returned a MEDIUM risk level and Balanced favorability. The main red flag identified was the copyleft requirement that forces Party B to release any modifications under the same license terms if they distribute the software. The summary accurately described the tradeoff between the extensive freedoms granted and the strict source code disclosure obligations imposed on derivative works.

---

## How to run it

Go to GenLayer Studio at https://studio.genlayer.com and create a new file called legal_analyzer.py. Paste the contract code and set execution mode to Normal Full Consensus. Deploy with your address as owner_address.

Follow this order and wait for FINALIZED at each step. Run get_summary first, then submit_contract with your contract details, then get_analysis to confirm it is pending, then analyze to trigger the AI evaluation, then get_analysis again to see the full result.

For best results use URLs that point directly to plain text or simple HTML documents. PDF files and pages that require JavaScript to render may not return usable content.

Note: the contract in this repository uses the Address type in the constructor as required by genvm-lint. When deploying in GenLayer Studio use a version that receives str in the constructor and converts internally with Address(owner_address) since Studio requires primitive types to parse the contract schema correctly.

---

## Resources

GenLayer Docs: https://docs.genlayer.com

Optimistic Democracy: https://docs.genlayer.com/understand-genlayer-protocol/core-concepts/optimistic-democracy

Equivalence Principle: https://docs.genlayer.com/understand-genlayer-protocol/core-concepts/optimistic-democracy/equivalence-principle

GenLayer Studio: https://studio.genlayer.com

Discord: https://discord.gg/8Jm4v89VAu

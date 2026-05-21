// ReasonGraph Neo4j constraints.
//
// What this file does:
// - Creates uniqueness constraints for core ReasonGraph graph nodes.
// - Makes graph writes safer and more idempotent.
// - Supports MERGE-based writes later in the project.
//
// How it fits into ReasonGraph:
// - Neo4j stores the reasoning graph: issues, positions, claims,
//   assumptions, evidence, risks, criteria, options, and LLM POVs.

CREATE CONSTRAINT reasongraph_issue_id IF NOT EXISTS
FOR (n:Issue) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT reasongraph_stakeholder_id IF NOT EXISTS
FOR (n:Stakeholder) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT reasongraph_position_id IF NOT EXISTS
FOR (n:Position) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT reasongraph_claim_id IF NOT EXISTS
FOR (n:Claim) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT reasongraph_assumption_id IF NOT EXISTS
FOR (n:Assumption) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT reasongraph_evidence_id IF NOT EXISTS
FOR (n:Evidence) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT reasongraph_concept_id IF NOT EXISTS
FOR (n:Concept) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT reasongraph_decision_criterion_id IF NOT EXISTS
FOR (n:DecisionCriterion) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT reasongraph_option_id IF NOT EXISTS
FOR (n:Option) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT reasongraph_risk_id IF NOT EXISTS
FOR (n:Risk) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT reasongraph_question_id IF NOT EXISTS
FOR (n:Question) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT reasongraph_source_id IF NOT EXISTS
FOR (n:Source) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT reasongraph_llm_pov_id IF NOT EXISTS
FOR (n:LLMPOV) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT reasongraph_analysis_run_id IF NOT EXISTS
FOR (n:AnalysisRun) REQUIRE n.id IS UNIQUE;
import google.generativeai as genai
import json
from typing import Dict, Any

# 🔐 Replace with your actual Gemini API Key
GEMINI_API_KEY = ""

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")


def _extract_json_block(text: str) -> Dict[str, Any]:
    """
    Try to extract the first valid JSON object from the model response text.
    """
    first = text.find("{")
    last = text.rfind("}")
    if first == -1 or last == -1:
        raise ValueError("No JSON object found in model response")

    json_str = text[first:last + 1]
    return json.loads(json_str)


def extract_fields_from_text(doc_text: str) -> Dict[str, Any]:
    """
    Call Gemini to extract ALL required RFP / solicitation fields
    based on:
      - Expanded Information to Extract From Each New Solicitation
      - SYSTEM DATA SCHEMA (Database-Level Structure) for RFP Automation

    Returns a Python dict with a flat JSON structure of fields.
    Keys are snake_case and grouped logically.
    """

    # This JSON template describes ALL the fields we want.
    # The model is instructed to fill this exact structure.
    json_template = {
        # =========================
        # 1. Basic Solicitation Metadata (Doc 1 + solicitations table)
        # =========================
        "solicitation_id": "",
        "solicitation_number": "",
        "title": "",
        "agency": "",
        "procurement_type": "",           # RFP / RFI / RFQ / Bid / ITB
        "category": "",                  # IT, Healthcare, HR, Construction, etc.
        "publish_date": "",
        "due_date": "",
        "pre_bid_meeting": "",
        "document_url": "",
        "reference_numbers": "",         # could be multiple
        "funding_source": "",            # Federal/State/Grant/CMS/ARPA etc.
        "procurement_vehicle": "",       # Open, GSA, IDIQ, BPA, etc.
        "notice_type": "",               # Solicitation, Amendment, Addendum, etc.
        "contracting_method": "",        # Best value, LPTA, etc.
        "naics_codes": "",
        "psc_commodity_codes": "",
        "geographic_preference_requirements": "",
        "submission_timezone": "",
        "contract_ceiling_value": "",
        "budget_range_or_estimate": "",
        "amendment_numbers_and_versions": "",

        # =========================
        # 2. Contacts & Submission Details (Doc 1 + contacts table)
        # =========================
        "primary_contact_name": "",
        "primary_contact_title": "",
        "primary_contact_email": "",
        "primary_contact_phone": "",
        "backup_contacts": "",                   # free text or JSON-like string
        "submission_instructions": "",
        "clarification_period_deadline": "",
        "deadline_for_questions": "",
        "pre_bid_meeting_requirement": "",       # mandatory / optional / none
        "pre_bid_meeting_location": "",
        "pre_bid_meeting_datetime": "",
        "physical_delivery_instructions": "",
        "packaging_instructions": "",
        "signatory_authority_requirements": "",
        "notary_seal_requirements": "",
        "submission_checklist": "",

        # =========================
        # 3. Scope of Work / Requirements (scope_requirements table)
        # =========================
        "scope_text": "",
        "deliverables": "",
        "mandatory_requirements": "",
        "technical_specs": "",
        "staffing_ratios": "",
        "performance_locations": "",
        "emergency_response_requirements": "",
        "report_delivery_cadence": "",
        "deliverable_dependencies": "",
        "tools_software_required": "",
        "technology_stack_requirements": "",
        "governing_policies": "",
        "travel_and_expense_rules": "",
        "subcontracting_rules": "",
        "sla_escalation_workflows": "",

        # =========================
        # 4. Questionnaire / Forms / Q&A Sections
        # =========================
        "questionnaire_sections": "",
        "table_form_field_requirements": "",
        "signature_fields_required": "",
        "compliance_certifications": "",    # E-Verify, SAM.gov, OFAC, etc.
        "tabs_section_numbering": "",
        "multi_part_question_patterns": "",
        "word_page_limits": "",
        "font_formatting_requirements": "",
        "excel_table_extraction_notes": "",
        "mandatory_narrative_sections": "",
        "disqualifying_questions": "",

        # =========================
        # 5. Pricing Information (pricing table + Doc 1)
        # =========================
        "pricing_tables": "",
        "pricing_templates": "",
        "payment_terms": "",
        "price_escalation_clauses": "",
        "discounts_or_rebate_structures": "",
        "travel_reimbursement_policy": "",
        "multi_year_pricing_requirements": "",
        "labor_category_mappings": "",
        "units_of_measure": "",
        "cost_realism_requirements": "",
        "pricing_uploadable_formats": "",
        "pricing_template_constraints": "",

        # =========================
        # 6. Evaluation & Scoring (evaluation table + Doc 1)
        # =========================
        "evaluation_criteria": "",
        "scoring_matrix": "",
        "evaluation_committee_roles": "",
        "tie_breaking_rules": "",
        "weighted_vs_non_weighted_scoring": "",
        "pass_fail_criteria": "",
        "ranking_methodology": "",
        "presentation_interview_requirements": "",
        "bafo_requirements": "",
        "oral_presentation_scoring": "",

        # =========================
        # 7. Legal / Contractual Requirements (legal_compliance table + Doc 1)
        # =========================
        "terms_and_conditions": "",
        "governing_law_jurisdiction": "",
        "insurance_requirements": "",
        "compliance_certifications_list": "",
        "contract_start_date": "",
        "contract_duration": "",
        "risk_sharing_clauses": "",
        "background_check_rules": "",
        "termination_clauses": "",
        "subcontractor_usage_rules": "",
        "non_performance_penalties": "",
        "liquidated_damages": "",
        "security_privacy_requirements": "",
        "audit_rights_requirements": "",
        "data_retention_policies": "",
        "ip_ownership_rules": "",

        # =========================
        # 8. Attachments & Appendices (attachments table + Doc 1)
        # =========================
        "required_attachments": "",
        "optional_attachments": "",
        "forms_requiring_signatures": "",
        "mandatory_returnable_documents": "",
        "templates_requiring_inputs": "",
        "compliance_checklists": "",
        "exhibit_mapping": "",
        "amendment_files_and_versions": "",

        # =========================
        # 9. AI-Powered Learning / Company Content Library (Doc 1 – B Section)
        # These will often be blank for a single RFP doc, but we keep keys.
        # =========================
        "company_vision_mission_mentions": "",
        "technology_stack_descriptions": "",
        "case_studies_referenced": "",
        "contract_performance_metrics": "",
        "staffing_methodologies": "",
        "sops_and_workflows": "",
        "success_benchmarks": "",
        "diversity_inclusion_requirements": "",
        "iso_soc_hipaa_policies": "",
        "transition_exit_strategy_requirements": "",
        "security_compliance_statements": "",

        "reusable_answer_style_preferences": "",
        "multipart_answer_expectations": "",
        "agency_specific_preferred_wording": "",
        "historical_reviewer_comments_clues": "",

        "pricing_history_signals": "",
        "regional_pricing_variance_notes": "",
        "margin_or_cost_sensitivity": "",
        "competitor_pricing_signals": "",

        "historical_awardees_if_mentioned": "",
        "agency_critical_priorities": "",
        "evaluation_tendencies": "",
        "incumbency_indicators": "",
        "political_or_funding_context": "",

        # =========================
        # 10. Opportunity Classification & Risk Detection (Doc 1 – 14, 15)
        # =========================
        "opportunity_alignment_indicators": "",
        "resource_capacity_signals": "",
        "compliance_risk_signals": "",
        "required_certifications_list": "",
        "competitive_landscape_indicators": "",
        "risk_detection_staffing_penalties": "",
        "risk_detection_performance_bonds": "",
        "risk_detection_unrealistic_slas": "",
        "risk_detection_unlimited_liability": "",
        "risk_detection_247_operations": "",
        "risk_detection_high_complexity_pricing": "",
        "risk_detection_exclusivity_restrictions": "",

        # =========================
        # 11. Workflow / To-Do / Compliance Gaps / Intelligence (Doc 1 – 16, 19, 20)
        # =========================
        "required_approvals_or_signoffs": "",
        "deadline_related_tasks": "",
        "checklist_of_required_sections": "",
        "missing_signature_warnings": "",
        "required_attachments_list": "",
        "compliance_gaps_summary": "",
        "qa_checkpoints": "",
        "document_hierarchy_summary": "",
        "section_level_grouping_notes": "",
        "table_detection_notes": "",
        "cross_reference_mappings": "",
        "version_alignment_notes": "",

        "compliance_can_meet": "",
        "compliance_cannot_meet": "",
        "compliance_needs_review": "",
        "compliance_mitigation_recommendations": "",

        "proposal_recommended_structure": "",
        "proposal_auto_win_themes": "",
        "proposal_auto_graphics_ideas": "",
        "proposal_formatting_constraints": ""
    }

    # Build the prompt for the model
    prompt = f"""
You are an RFP / Solicitation document intelligence engine.

Using the following document text, extract ALL relevant information and
populate the following JSON template.

IMPORTANT RULES:
- Return ONLY a single JSON object.
- Use the SAME KEYS and structure as in the template below.
- For any value that is not present in the document, use an empty string "".
- Values can be short text, lists serialized as strings, or brief summaries.
- Do NOT add extra keys.

JSON TEMPLATE (with example keys, but empty string values):

{json.dumps(json_template, indent=2)}

Document Text:
\"\"\"{doc_text}\"\"\"
"""

    response = model.generate_content(prompt)
    raw_text = response.text

    # Parse out the JSON from the model response
    fields = _extract_json_block(raw_text)
    # Ensure all template keys exist (fill missing with "")
    for key in json_template.keys():
        if key not in fields:
            fields[key] = ""

    return fields


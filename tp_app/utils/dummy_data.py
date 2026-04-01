"""
dummy_data.py
=============
Realistic dummy data for testing the TP Local File Generator.
Company: PT Sakura Manufaktur Indonesia (SMI) — fictional Indonesian
         contract manufacturer of automotive precision components,
         subsidiary of Sakura Holdings Corporation (Japan).

All monetary figures are in IDR unless noted.
"""

DUMMY_DATA = {

    # ── Company identity ──────────────────────────────────────────────────────
    "company_name": "PT Sakura Manufaktur Indonesia",
    "company_short_name": "SMI",
    "company_address": (
        "Kawasan Industri MM2100, Jl. Irian Blok FF-3, "
        "Cikarang Barat, Bekasi 17520, Jawa Barat, Indonesia"
    ),
    "establishment_info": (
        "Established under Deed of Incorporation No. 45 dated 15 March 2010, "
        "Notary Dra. Ratna Sari Dewi, S.H., M.Kn., approved by the Minister "
        "of Law and Human Rights of the Republic of Indonesia No. "
        "AHU-12345.AH.01.01.TAHUN 2010 dated 20 April 2010. "
        "Business License (NIB): 1234567890123. "
        "Authorized capital: IDR 100,000,000,000; Issued & paid-up: IDR 100,000,000,000."
    ),
    "fiscal_year": "2024",
    "parent_company": "Sakura Industries Co., Ltd.",
    "parent_group": "Sakura Holdings Corporation",

    # ── Shareholders ──────────────────────────────────────────────────────────
    "shareholders": [
        {
            "name": "Sakura Industries Co., Ltd.",
            "shares": "9,500",
            "capital": "IDR 95,000,000,000",
            "percentage": "95%",
        },
        {
            "name": "PT Mitra Investasi Nusantara",
            "shares": "500",
            "capital": "IDR 5,000,000,000",
            "percentage": "5%",
        },
    ],
    "shareholders_source": "Source: Management SMI, 31 December 2024",

    # ── Management ────────────────────────────────────────────────────────────
    "management": [
        {"position": "President Commissioner",   "name": "Takeshi Yamamoto"},
        {"position": "Commissioner",             "name": "Ir. Budi Santoso"},
        {"position": "President Director",       "name": "Hiroshi Tanaka"},
        {"position": "Finance Director",         "name": "Siti Nurhaliza, S.E., M.Ak."},
        {"position": "Operations Director",      "name": "Kenji Watanabe"},
    ],
    "management_source": "Source: Management SMI, 31 December 2024",
    "employee_count": "385 permanent employees, 120 contract employees",

    # ── Affiliated parties ────────────────────────────────────────────────────
    "affiliated_parties": [
        {
            "name": "Sakura Industries Co., Ltd.",
            "country": "Japan",
            "relationship": "Parent company (95% ownership)",
            "transaction_type": "Purchase of raw materials; royalty payment",
        },
        {
            "name": "Sakura Trading (Singapore) Pte. Ltd.",
            "country": "Singapore",
            "relationship": "Fellow subsidiary under Sakura Holdings",
            "transaction_type": "Sale of finished goods",
        },
        {
            "name": "Sakura Tech Vietnam Co., Ltd.",
            "country": "Vietnam",
            "relationship": "Fellow subsidiary under Sakura Holdings",
            "transaction_type": "Purchase of sub-components",
        },
        {
            "name": "Sakura Holdings Corporation",
            "country": "Japan",
            "relationship": "Ultimate parent company",
            "transaction_type": "Management fee",
        },
    ],

    # ── Business activities ───────────────────────────────────────────────────
    "business_activities_description": (
        "PT Sakura Manufaktur Indonesia (SMI) is engaged in the manufacturing of "
        "precision automotive components, including bearings, bushings, seals, and "
        "other precision metal parts for the automotive and heavy-equipment industries. "
        "SMI operates as a contract manufacturer, producing goods to the technical "
        "specifications and designs provided by its parent company, Sakura Industries "
        "Co., Ltd. (Japan). Finished products are sold to affiliated trading companies "
        "in the ASEAN region as well as to domestic third-party customers. "
        "The company is certified to ISO 9001:2015 and IATF 16949:2016 standards "
        "and operates two production facilities with a combined floor area of 42,000 m²."
    ),

    "products": [
        {
            "name": "Automotive Bearings",
            "description": (
                "Ball bearings and roller bearings for automotive transmissions, "
                "wheel hubs, and engine applications (OEM specifications)."
            ),
        },
        {
            "name": "Industrial Bushings",
            "description": (
                "Precision bronze and sintered-metal bushings for construction "
                "machinery, agricultural equipment, and industrial motors."
            ),
        },
        {
            "name": "Precision Components",
            "description": (
                "CNC-machined metal components including shafts, housings, and "
                "brackets manufactured to tight tolerances (±0.005 mm)."
            ),
        },
        {
            "name": "Seal & Gasket Kits",
            "description": (
                "Rubber and PTFE sealing components for automotive drivetrains, "
                "hydraulic systems, and industrial pumps."
            ),
        },
    ],

    "business_strategy": (
        "SMI's business strategy focuses on three pillars: (1) Operational excellence "
        "through lean manufacturing and kaizen continuous-improvement programs; "
        "(2) Quality leadership by maintaining IATF 16949 certification and pursuing "
        "zero-defect targets; and (3) Capacity expansion through investment in "
        "CNC machining centers and robotic assembly lines to serve growing ASEAN "
        "automotive demand. The company targets a 15% increase in production capacity "
        "by FY 2026 and a diversification of its customer base to reduce dependence "
        "on intra-group sales to below 60% of total revenue."
    ),

    "business_restructuring": (
        "During Fiscal Year 2024, SMI was not involved in any business restructuring, "
        "legal entity changes, or transfers of intangible assets within the Sakura Group. "
        "No functions, risks, or assets were transferred to or from related parties "
        "during the Fiscal Year."
    ),

    # ── Organization structure (Appendix 1) ──────────────────────────────────
    "org_structure_description": (
        "SMI's organizational structure is led by the Board of Commissioners and "
        "Board of Directors. Under the President Director, the company is organized "
        "into five functional divisions: Finance & Accounting, Production & Operations, "
        "Quality Assurance, Sales & Marketing, and Human Resources & General Affairs. "
        "Each division is headed by a Division Manager who reports directly to a Director."
    ),
    "org_structure_departments": [
        {"name": "Finance & Accounting",          "head": "Siti Nurhaliza, S.E., M.Ak.", "employees": "28"},
        {"name": "Production & Operations",        "head": "Kenji Watanabe",             "employees": "312"},
        {"name": "Quality Assurance",              "head": "Agus Prabowo, S.T.",         "employees": "45"},
        {"name": "Sales & Marketing",              "head": "Dewi Rahayu, M.B.A.",        "employees": "22"},
        {"name": "Human Resources & General Affairs", "head": "Maria Susanti, S.Psi.",  "employees": "18"},
        {"name": "Research & Development",         "head": "Ryo Kimura",                 "employees": "20"},
    ],

    # ── Affiliated transactions (Table 4.1) ──────────────────────────────────
    # aff.value  = "Type of Product" column
    # aff.note   = "Amount (in IDR)" column
    "affiliated_transactions": [
        {
            "no": "1",
            "name": "Sakura Industries Co., Ltd.",
            "country": "Japan",
            "affiliation_type": "A special relationship because it is under the same control (95% ownership)",
            "transaction_type": "Purchase",
            "value": "Specialty steel alloys; bearing-grade steel rods",
            "note": "180,000,000,000",
        },
        {
            "no": "2",
            "name": "Sakura Trading (Singapore) Pte. Ltd.",
            "country": "Singapore",
            "affiliation_type": "A special relationship because it is under the same control",
            "transaction_type": "Sale",
            "value": "Automotive bearings; precision components",
            "note": "220,000,000,000",
        },
        {
            "no": "3",
            "name": "Sakura Industries Co., Ltd.",
            "country": "Japan",
            "affiliation_type": "A special relationship because it is under the same control (95% ownership)",
            "transaction_type": "Royalty payment",
            "value": "Manufacturing technology; know-how; patents",
            "note": "12,600,000,000",
        },
        {
            "no": "4",
            "name": "Sakura Holdings Corporation",
            "country": "Japan",
            "affiliation_type": "A special relationship because it is under the same control (ultimate parent)",
            "transaction_type": "Management fee",
            "value": "Shared services (treasury, legal, IT, HR)",
            "note": "8,500,000,000",
        },
    ],

    # ── Independent transactions (Table 4.2) ─────────────────────────────────
    # ind.value = "Amount (in IDR)" column
    "independent_transactions": [
        {
            "no": "1",
            "name": "PT Astra Honda Motor",
            "country": "Indonesia",
            "transaction_type": "Sale",
            "value": "95,400,000,000",
        },
        {
            "no": "2",
            "name": "PT Toyota Motor Manufacturing Indonesia",
            "country": "Indonesia",
            "transaction_type": "Sale",
            "value": "72,600,000,000",
        },
        {
            "no": "3",
            "name": "PT Yamaha Indonesia Motor Manufacturing",
            "country": "Indonesia",
            "transaction_type": "Sale",
            "value": "32,000,000,000",
        },
    ],

    # ── Transactions ──────────────────────────────────────────────────────────
    "transaction_type": "Purchase of tangible goods",
    "transaction_counterparties": [
        {"name": "Sakura Industries Co., Ltd.",        "country": "Japan",     "type": "Purchase of raw materials"},
        {"name": "Sakura Trading (Singapore) Pte. Ltd.", "country": "Singapore", "type": "Sale of finished goods"},
        {"name": "Sakura Holdings Corporation",        "country": "Japan",     "type": "Management fee"},
    ],
    "transaction_details_text": (
        "During Fiscal Year 2024, SMI conducted the following affiliated-party transactions:\n\n"
        "1. Purchase of raw materials (specialty steel alloys, bearing-grade steel rods) "
        "from Sakura Industries Co., Ltd. (Japan): IDR 180,000,000,000. "
        "These materials are not commercially available from independent suppliers at "
        "equivalent quality and specification levels.\n\n"
        "2. Sale of finished goods (automotive bearings, precision components) "
        "to Sakura Trading (Singapore) Pte. Ltd.: IDR 220,000,000,000. "
        "Products are sold at cost-plus pricing per intercompany agreement.\n\n"
        "3. Royalty payment for the use of manufacturing technology, know-how, "
        "and patents to Sakura Industries Co., Ltd.: 3% of Net Sales = "
        "IDR 12,600,000,000. Based on License Agreement dated 1 January 2015.\n\n"
        "4. Management fee to Sakura Holdings Corporation for shared services "
        "(treasury, legal, IT, HR): IDR 8,500,000,000 (actual cost + 5% markup).\n\n"
        "Total affiliated-party transactions in FY 2024: IDR 421,100,000,000."
    ),
    "pricing_policy": (
        "SMI determines transfer prices for each transaction type as follows:\n\n"
        "- Raw material purchases: Benchmarked against third-party market prices "
        "(CUP method) with adjustments for volume discounts and material grade. "
        "Prices are reviewed semi-annually.\n\n"
        "- Sale of finished goods: Cost-plus methodology. The cost base comprises "
        "direct materials, direct labor, and allocated manufacturing overhead. "
        "A mark-up consistent with the arm's length range identified through TNMM "
        "benchmarking is applied.\n\n"
        "- Royalty: Fixed at 3% of Net Sales per the License Agreement, "
        "consistent with comparable royalty rates observed in the automotive "
        "components industry (1%–5% range per OECD benchmarks).\n\n"
        "- Management fee: Calculated on actual cost-sharing basis plus a 5% "
        "mark-up to reflect routine service activities with no significant risk."
    ),

    # ── Financial data (current year - FY 2024) ───────────────────────────────
    # Key names must match docx_export.py's pl_items list
    "financial_data": {
        "sales":               "IDR 420,000,000,000",
        "cogs":                "IDR 315,000,000,000",
        "gross_profit":        "IDR 105,000,000,000",
        "gross_margin_pct":    "25.0%",
        "operating_expenses":  "IDR 58,800,000,000",
        "operating_profit":    "IDR 46,200,000,000",
        "financial_income":    "(IDR 3,780,000,000)",   # net interest expense
        "other_income":        "IDR 840,000,000",
        "other_expense":       "IDR 0",
        "income_before_tax":   "IDR 43,260,000,000",
        "income_tax":          "IDR 10,815,000,000",    # 25% corporate tax rate
        "net_income":          "IDR 32,445,000,000",
    },

    # ── Financial data (prior year - FY 2023) ────────────────────────────────
    "financial_data_prior": {
        "sales":               "IDR 390,000,000,000",
        "cogs":                "IDR 296,400,000,000",
        "gross_profit":        "IDR 93,600,000,000",
        "gross_margin_pct":    "24.0%",
        "operating_expenses":  "IDR 54,600,000,000",
        "operating_profit":    "IDR 39,000,000,000",
        "financial_income":    "(IDR 4,290,000,000)",
        "other_income":        "IDR 780,000,000",
        "other_expense":       "IDR 0",
        "income_before_tax":   "IDR 35,490,000,000",
        "income_tax":          "IDR 8,872,500,000",
        "net_income":          "IDR 26,617,500,000",
    },

    # ── Comparable companies (BvD Orbis screening) ───────────────────────────
    "comparable_companies": [
        {
            "name": "PT Astra Otoparts Tbk",
            "country": "Indonesia",
            "description": (
                "Listed Indonesian manufacturer of automotive components including "
                "bearings, filters, brake systems, and stamped parts for OEM and "
                "aftermarket customers. Low related-party dependence."
            ),
            "ros_data": "8.5%, 9.2%, 10.1%",
        },
        {
            "name": "PT Indospring Tbk",
            "country": "Indonesia",
            "description": (
                "Manufacturer of automotive leaf springs, coil springs, and precision "
                "metal stampings. Serves both domestic and export markets."
            ),
            "ros_data": "7.8%, 8.4%, 9.0%",
        },
        {
            "name": "Thai Steel Cable Public Co., Ltd.",
            "country": "Thailand",
            "description": (
                "Thai manufacturer of automotive control cables, bearings, and metal "
                "assemblies. Supplies OEM customers across Southeast Asia."
            ),
            "ros_data": "6.2%, 7.5%, 8.8%",
        },
        {
            "name": "Vietnam Precision Industrial No. 1 JSC",
            "country": "Vietnam",
            "description": (
                "Manufacturer of precision turned parts, bearings, and industrial "
                "metal components. ISO 9001 certified."
            ),
            "ros_data": "5.9%, 6.8%, 7.4%",
        },
        {
            "name": "Siam Bearing Co., Ltd.",
            "country": "Thailand",
            "description": (
                "Specialist bearing manufacturer for automotive, agricultural, and "
                "industrial applications. Sells to third-party distributors and OEMs."
            ),
            "ros_data": "7.1%, 8.0%, 9.3%",
        },
    ],

    "search_criteria_results": [
        {"step": "1", "criteria": "Region: ASEAN + South Asia",                    "result_count": "2,450"},
        {"step": "2", "criteria": "NACE Rev. 2 codes: 2815, 2562, 2932",           "result_count": "385"},
        {"step": "3", "criteria": "Operating revenue: > USD 10,000,000",           "result_count": "142"},
        {"step": "4", "criteria": "Independence indicator: BvD B+ or higher",      "result_count": "78"},
        {"step": "5", "criteria": "Active companies with 3 consecutive years data", "result_count": "45"},
        {"step": "6", "criteria": "Manual review: functional comparability",        "result_count": "5"},
    ],

    "rejection_matrix": [
        {"name": "PT Multistrada Arah Sarana",   "limited_financial_statement": False, "negative_margin": False, "consolidated_financial_statement": False, "different_main_activity": True,  "non_comparable_line_of_business": False, "limited_information_website": False, "accepted": False},
        {"name": "PT Selamat Sempurna Tbk",       "limited_financial_statement": False, "negative_margin": False, "consolidated_financial_statement": False, "different_main_activity": True,  "non_comparable_line_of_business": False, "limited_information_website": False, "accepted": False},
        {"name": "Hana Microelectronics PCL",     "limited_financial_statement": False, "negative_margin": False, "consolidated_financial_statement": False, "different_main_activity": True,  "non_comparable_line_of_business": True,  "limited_information_website": False, "accepted": False},
        {"name": "PT Astra Komponen Indonesia",   "limited_financial_statement": False, "negative_margin": False, "consolidated_financial_statement": False, "different_main_activity": False, "non_comparable_line_of_business": False, "limited_information_website": False, "accepted": True},
        {"name": "PT Showa Indonesia Mfg",        "limited_financial_statement": False, "negative_margin": False, "consolidated_financial_statement": False, "different_main_activity": False, "non_comparable_line_of_business": False, "limited_information_website": False, "accepted": True},
        {"name": "PT Inti Ganda Perdana",         "limited_financial_statement": False, "negative_margin": False, "consolidated_financial_statement": False, "different_main_activity": False, "non_comparable_line_of_business": False, "limited_information_website": False, "accepted": True},
    ],

    # ── TP Analysis parameters ────────────────────────────────────────────────
    "selected_method": "TNMM",
    "selected_pli": "ROS",
    "tested_party": "PT Sakura Manufaktur Indonesia",
    "analysis_period": "2022-2024",
    "quartile_range": {"q1": 6.8, "median": 8.0, "q3": 9.2},
    # SMI ROS = Operating Profit / Net Sales = 46,200 / 420,000 = 11.0%
    "tested_party_ratio": 11.0,

    # ── Non-financial events ──────────────────────────────────────────────────
    "non_financial_events": (
        "During Fiscal Year 2024, there were no material non-financial events that "
        "had a significant impact on SMI's pricing or profit levels. The company "
        "continued to operate normally without any change in organizational structure, "
        "government regulations specifically affecting its business, or extraordinary "
        "market conditions. Global commodity steel prices declined by approximately "
        "8% year-on-year, which modestly reduced SMI's cost of goods sold relative "
        "to the prior year, partially explaining the improvement in gross profit margin "
        "from 24.0% (FY 2023) to 25.0% (FY 2024)."
    ),

    # ── Supply Chain Management (AI-generated) ──────────────────────────────
    "supply_chain_management": (
        "- Product Development: Product development for automotive precision components is carried out "
        "by Sakura Metal Industries Co., Ltd. (SMI Japan), the parent company, with a dedicated R&D "
        "centre focused on material innovation and OEM specification compliance.\n"
        "- Material Procurement: Raw materials including steel billets and aluminum alloys are sourced "
        "globally by SMI Japan and its group entities, leveraging group-wide procurement efficiencies "
        "and volume discounts.\n"
        "- Manufacturing: SMI Indonesia performs all manufacturing activities in-house, including "
        "machining, pressing, and quality inspection under IATF 16949 certification.\n"
        "- Distribution: SMI distributes finished components directly to Indonesian OEM customers and "
        "the broader ASEAN aftermarket through its own logistics network.\n"
        "- After-Sales Services: SMI provides product warranty support, technical assistance, and "
        "on-site quality audits to key OEM customers in Indonesia."
    ),

    # ── Comparable Company AI Descriptions (AI-generated via Tavily) ────────
    "comparable_descriptions": {
        "PT Astra Komponen Indonesia": (
            "PT Astra Komponen Indonesia is an Indonesian manufacturer specializing in precision metal "
            "components for the automotive industry, supplying major OEMs including Toyota and Honda. "
            "The company operates multiple production facilities across Java and employs lean "
            "manufacturing principles to maintain competitive cost structures. Its product portfolio "
            "includes stamped parts, brackets, and structural assemblies for passenger and commercial vehicles."
        ),
        "PT Showa Indonesia Mfg": (
            "PT Showa Indonesia Manufacturing is a contract manufacturer of steering and suspension "
            "components, established as a joint venture with Showa Corporation of Japan. The company "
            "serves major automotive OEMs in Indonesia and exports a portion of its output to ASEAN "
            "markets. It bears routine manufacturing risks with key strategic and demand risks assumed "
            "by its Japanese principal."
        ),
        "PT Inti Ganda Perdana": (
            "PT Inti Ganda Perdana is a leading Indonesian manufacturer of axles and driveshafts for "
            "commercial and passenger vehicles, with long-standing supply relationships with major "
            "Indonesian OEMs. The company invests continuously in production automation to improve "
            "throughput and product quality. It operates as a full-risk manufacturer with its own "
            "sales and marketing function."
        ),
        "PT Denso Indonesia": (
            "PT Denso Indonesia is a subsidiary of Denso Corporation Japan, manufacturing a broad "
            "range of automotive components including air conditioning systems, fuel systems, and "
            "electronic control units. The company supplies both the OEM and aftermarket segments "
            "in Indonesia and selectively exports to regional markets. It operates under a limited-risk "
            "manufacturing model with strategic direction from Denso Japan."
        ),
        "PT Yorozu Automotive Indonesia": (
            "PT Yorozu Automotive Indonesia specializes in the manufacture of suspension parts and "
            "pressed metal components for passenger vehicles, operating as a Tier-1 supplier to major "
            "Japanese-brand OEMs assembled in Indonesia. The company is a subsidiary of Yorozu "
            "Corporation Japan and follows group-wide quality and cost management standards. "
            "Its manufacturing operations are concentrated in a single integrated facility in West Java."
        ),
        "PT Aisin Indonesia": (
            "PT Aisin Indonesia is a manufacturer of transmission components, door frames, and body "
            "parts, operating as part of the Aisin Group under Toyota Industries Corporation. The "
            "company produces components primarily for Toyota and Daihatsu vehicles assembled in "
            "Indonesia and has progressively expanded its local content ratio in line with government "
            "TKDN requirements. It functions as a limited-risk manufacturer under technical and "
            "commercial oversight from Aisin Japan."
        ),
    },

    # ── Table 5.1: Comparability Analysis Factors (manual) ──────────────────
    "comparability_factors": [
        {
            "factor": "Contract Terms and Conditions",
            "description": (
                "The purchase transaction of automotive precision components from SMI to "
                "affiliated party is based on contracts with each affiliated party. Contract "
                "terms include volume commitments, delivery schedules, and warranty provisions "
                "consistent with arm's length arrangements."
            ),
        },
        {
            "factor": "Product Characteristics",
            "description": (
                "The products provided are in the form of automotive bearings, industrial "
                "bushings, precision components, and seal & gasket kits manufactured to OEM "
                "specifications. Products are functionally comparable across the benchmark set."
            ),
        },
        {
            "factor": "Functional Analysis",
            "description": (
                "SMI functions as a contract manufacturer bearing limited market and inventory "
                "risks, while the affiliated party assumes demand and strategic risks. "
                "Comparable companies perform similar routine manufacturing functions."
            ),
        },
        {
            "factor": "Business Strategy",
            "description": (
                "SMI implements general business strategies such as operational excellence "
                "through lean manufacturing, quality leadership (IATF 16949), and capacity "
                "expansion to serve growing ASEAN automotive demand. Strategy is consistent "
                "with comparable independent manufacturers."
            ),
        },
        {
            "factor": "Economic Conditions",
            "description": (
                "Influenced by local and global economic conditions, including Indonesian GDP "
                "growth, inflation rates, and Rupiah exchange rate movements. Comparable "
                "companies operate in similar ASEAN economic environments."
            ),
        },
    ],
}

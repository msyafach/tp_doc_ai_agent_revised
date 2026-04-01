"""
Template sections for Transfer Pricing Local File documentation.
These sections contain standard regulatory text that remains largely identical
across different companies' TP documentation.

Placeholders use {variable_name} format for company-specific substitution.
"""

GLOSSARY = {
    "Affiliated/Related Parties": "Parties categorized as having special relationship among them as set out in Article 18 Paragraph (4) Law of Republic Indonesia Number 7 Year 1983 concerning Income Tax as amended several times and the latest by Law of Republic Indonesia Number 7 Year 2021",
    "ALP": "Arm's Length Principles",
    "APA": "Advance Pricing Agreement",
    "Benchmarking": "Arm's length price/profit reference",
    "Berry Ratio": "Ratio of Gross Margin compared to its Operating Expenses",
    "CbCR": "Country-by-Country Report",
    "CPM": "Cost-Plus Method",
    "CUP": "Comparable Uncontrolled Price Method",
    "GPM": "Gross Profit Margin",
    "Income Tax Law": "Consolidation of Law of the Republic of Indonesia No. 7 Year 1983 Concerning Income Tax as Lastly Amended by Law No. 7 Year 2021",
    "Independent/Third Parties": "Parties which are not included as having special relationship among them as set out in Article 18 Paragraph (4) Law of Republic Indonesia Number 7 Year 1983 concerning Income Tax as amended several times and the latest by Law of Republic Indonesia Number 7 Year 2021",
    "NCPM": "Net Cost Plus Mark-up",
    "OECD TPG": "Organization for Economic Cooperation and Development Transfer Pricing Guidelines 2022",
    "PER-22/PJ/2013": "Directorate General of Taxation Regulation No. PER-22/PJ/2013 regarding Audit Guidelines for Taxpayers with Affiliate Party Transactions",
    "PER-32/PJ/2011": "Directorate General of Taxation Regulation No. PER-43/PJ/2010 as latest amended by Directorate General of Taxation (DGT) Regulation No. PER-32/PJ/2011 regarding the Implementation of Arm's Length Principle in Transaction Between Associate Enterprises",
    "PLI": "Profit Level Indicator/Indikator Tingkat Laba",
    "PMK 172 Year 2023": "Regulation of the Minister of Finance of the Republic of Indonesia Number 172 of 2023 on the Application of the Principles of Arm's Length Principle in Transactions Affected by Special Relationships",
    "PSM": "Profit Split Method",
    "ROA": "Return on Assets",
    "ROCE": "Return on Capital Employed",
    "ROS": "Return On Sales",
    "RPM": "Resale Price Method",
    "SE-50/PJ/2013": "Circular No. SE-50/PJ/2013 regarding Technical Audit Guidance for Taxpayers with Affiliate Party Transactions",
    "Tested Party": "The entity that is under reviewed for the purpose of the transfer pricing analysis",
    "TNMM": "Transactional Net Margin Method",
    "Transfer Pricing": "Setting of prices of goods and services that are exchanged among the subsidiary, affiliate or commonly controlled companies or legal entities that are part of the multinational enterprise.",
}

STATEMENT_LETTER = """The Transfer Pricing Documentation prepared by the management of {company_name} represents the management's understanding of {company_short_name}'s affiliated transactions and the application of the arm's length principle to these transactions.

This Transfer Pricing Documentation in the form of Local File covers the Affiliated Party transactions conducted by {company_short_name} in Fiscal Year {fiscal_year} as described in the scope of this report. Some numbers which are calculated are the result of the available data; some other numbers are only based on the management's representation and information. Our work does not constitute a legal opinion on any transactions examined.

In connection with the preparation of the Transfer Pricing Documentation, the Local File is not intended to be used in connection with legal proceedings under any jurisdiction.

There may be qualitative considerations relevant to the Transfer Pricing analysis that cannot be expressed quantitatively. To the extent that any quantitative analysis is considered, it may need to be reviewed in conjunction with the qualitative analysis presented in this report.

This Local File was prepared based on currently available facts, data, and circumstances. Reassessment would be needed if there are significant changes to the facts, data and circumstances in the future.

{company_name}
{fiscal_year}"""

# ─── Chapter 2: Transfer Pricing Regulations ──────────────────────────────────

TP_REGULATIONS_INTRO = """Specific rules regarding Transfer Pricing are stipulated in the Indonesian Tax Regulations, article 18 of the Income Tax Law. As stated in Article 18 paragraph (3) of the Income Tax Law, the Tax Authority has the authority to re determine the amount of taxable income related to transactions between Related Parties not carried out in accordance with Arm's Length Principle.

In amendment to Article 18 paragraph 3 of the Income Tax Law, the Tax Authority is authorized to re determine the amount of income and expense/deduction and the amount of debt used as capital to calculate the amount of taxable income for Taxpayers who have affiliations with other Taxpayers in accordance with Arm's Length Principle compared to Independent transactions using the price comparison method between independent parties, using the resale price method, the cost-plus method, or other methods.

The Directorate General of Taxation (DGT) issued Circular Letter Number SE-04/PJ.7/1993 dated March 9, 1993 concerning "Guidelines for Handling Transfer Pricing Cases" amended by Circular Letter Number SE-50/2013 containing technical guidelines for examining Taxpayers who have Affiliations. The Government Regulation Number 80 of 2007 issued on December 28, 2007 which took effect on January 1, 2008 and amended by Government Regulation Number 74 of 2011, explicitly states that in the case of Taxpayers making transactions with Related Parties, the Taxpayer is obliged to keep documentations and information that supports that transactions carried out with Related Parties are in accordance with Arm's Length Principle.

Furthermore, the Directorate General of Taxes issued PER-39/PJ/2009 on July 2, 2009 and PER-34/PJ/2010 on July 27, 2010 which obliged companies that have controlled transactions with Related Parties to prepare Transfer Pricing documentations, valid since Fiscal Year 2009.

In accordance with DGT Regulation Number PER-43/PJ/2010 dated September 6, 2010 and amended by PER-32/PJ/2011 dated November 11, 2011, in a transaction with an Affiliated Party within a Fiscal Year not exceeding IDR 10,000,000,000.00 (ten billion rupiah) for transactions with one counterparty, the Taxpayer is not required to make Transfer Pricing documentation. However, the availability of adequate documentations is required to support the Arm's Length Principle. If transactions with Related Parties exceed IDR 10,000,000,000 (ten billion rupiah), the Taxpayer is required to make Transfer Pricing documentations.

Without replacing the Directorate General of Taxes Regulation PER-43/PJ/2010 as amended by PER-32/PJ/2011, which regulates the Arm's Length Principle, the Indonesian Minister of Finance issued PMK-213/PMK.03/2016 on December 30, 2016. This regulation addresses the types of documents and/or additional information that taxpayers conducting transactions with related parties must maintain, along with their management procedures. The implementation of the Arm's Length Principle is further governed by Minister of Finance Regulation Number 22/PMK.03/2020. In 2023, PMK-172 Year 2023 was issued to adjust the regulations concerning the application of the arm's length principle in transactions influenced by special relationships, as well as provisions on the types of documents and/or additional information that taxpayers must maintain for such transactions."""

TP_DOCUMENTATION_TYPES = """Documents that must be kept and maintained by the Taxpayer are:

1. Master File, consisting of information about:
   - Ownership structure and chart as well as the state or jurisdiction of each member of the Business Group;
   - Business activities carried out by the Business Group;
   - Intangible assets owned by the Business Group;
   - Financial and financing activities within the Business Group; and
   - Consolidated financial statements of parent entities and information related to Advance Pricing Agreements (APA) and other tax regulations related to the allocation of income between countries.

2. Local File, consisting of information about:
   - Identity and business activities carried out;
   - Information on Affiliated Party transactions and Independent transactions carried out;
   - Application of Arm's Length Principle;
   - Financial information from Taxpayer;
   - Non-financial events/events/facts that affect the formation of prices or profit levels.

3. Country-by-Country Report, consisting of information about:
   - Allocation of income, taxes paid, and business activities of all Business Group members per country or jurisdiction both domestically and abroad;
   - List of members of the Business Group and main business activities per country or jurisdiction."""

MF_LF_THRESHOLD_TABLE = [
    {"no": "1", "criteria": "Gross Turnover of Previous Fiscal Year", "threshold": "More than IDR 50,000,000,000 (Fifty Billion Rupiah)"},
    {"no": "2", "criteria": "Transactions of tangible goods in the previous Fiscal Year (Purchases or Sales of Goods)", "threshold": "More than IDR 20,000,000,000 (Twenty Billion Rupiah)"},
    {"no": "3", "criteria": "Intangible goods transaction for the previous Fiscal Year (Services, royalties, interest or other transactions)", "threshold": "More than IDR 5,000,000,000 (Five Billion Rupiah)"},
    {"no": "4", "criteria": "Transactions with Related Parties domiciled in jurisdictions with lower income tax rates than Indonesia", "threshold": "All transactions, both tangible goods and intangible goods, regardless of the amount"},
]

TP_DEADLINE_TEXT = """Taxpayers who are required to prepare and administer Master File and Local File based on PMK-172 Year 2023 are not required to include these documents immediately at the time of Annual Income Tax Return reporting but should be provided by the Taxpayer if requested by the tax authority. Master File and Local File must be available within 4 (four) months after the end of the Fiscal Year and must be accompanied by a statement of the availability of these documents. While the Country-by-Country Report must be reported together with the Annual Income Tax Return reporting, but the tax authority stipulates that the Country-by-Country Report must be available no later than 12 (twelve) months after the end of the Fiscal Year. Master File and Local File must be made summaries and submitted as attachments to the Annual Income Tax Return of the relevant Fiscal Year."""

SPECIAL_RELATIONSHIP = """The criteria for special relationships from an Indonesian tax perspective are regulated under Article 18 Paragraph (4) of the Income Tax Law (UU PPh), Article 2 of the VAT Law (UU PPN), and Article 2 of PMK-172 Year 2023, which serves as a technical regulation for further elaboration. According to Article 2 of PMK-172 Year 2023, two or more entities are considered to have a special relationship if they meet the following criteria:

According to Article 2, paragraph (2) of PMK-172 Year 2023, a special relationship is a condition of dependence or connection between one party and another, arising from three main factors: ownership or capital participation, control, or familial relationships through blood or marriage.

1) A special relationship due to ownership or capital participation is considered to occur when a taxpayer holds at least 25% direct or indirect capital participation in another taxpayer. Additionally, such a relationship exists if there is at least 25% participation in two or more taxpayers, creating an ownership relationship between these parties, as regulated in Article 2, paragraph (4) of PMK-172 Year 2023.

2) A special relationship due to control occurs in several conditions, such as one party controlling or being controlled by another party, two or more parties being under the same control, or control through management, technology, or participation in managerial decision-making. This relationship also applies if the parties are financially or commercially part of the same business group, as stated in Article 2, paragraph (5) of PMK-172 Year 2023.

3) Finally, a special relationship due to familial ties through blood or marriage is considered to exist when there is a family relationship, either direct or collateral, up to the first degree. This includes family relationships that have a significant influence on decision-making or the operations of the involved parties, as outlined in Article 2, paragraph (6) of PMK-172 Year 2023."""

SANCTIONS_TEXT = """Regarding sanctions and non-compliance in implementing PMK-172 Year 2023 it is regulated that:

- If the Master File and Local File upon request by the relevant tax authorities in the process of monitoring taxpayer compliance, tax audits, examination of preliminary evidence, investigation, objection research process, reduction or elimination of administrative sanctions, reduction or cancellation of incorrect tax bills, or correction is given but past the stipulated period, the Transfer Pricing Documentation submitted is only considered to be miscellaneous document. The consequence of this violation is that the Tax Authorities are entitled to conduct the Arm's Length Principle testing arbitrarily and a 2% interest penalty per month will be issued if the result of the test results in underpaid tax;

- If the Master File and Local File upon request by the relevant tax authorities in the process of monitoring taxpayer compliance, tax audits, examination of preliminary evidence, investigation, objection research process, reduction or elimination of administrative sanctions, reduction or cancellation of incorrect tax bills, or the correction is not given by the Taxpayer, the consequence of this violation is that the Taxpayer does not fulfil the obligation to prepare and keep the Transfer Pricing Documentation and a sanction in the form of an increase of 50% will be issued if there is underpaid tax from the test results;

If the Taxpayer does not use the data and information available at the time of the transaction, the Taxpayer is not considered to apply the Arm's Length Principle. The consequence of this violation is that the Tax Authority has the right to conduct the Arm's Length Principle test and a 2% interest penalty per month will be issued if from the test results there is underpaid tax."""

# ─── TP Methods Standard Descriptions ─────────────────────────────────────────

CUP_METHOD_DESC = """CUP method is a transfer pricing determination method conducted by comparing prices in transactions conducted between affiliated parties with prices of goods or services in transactions conducted between independent parties under comparable conditions or circumstances. If comparable independent transactions are available, the CUP method is the most direct and reliable method in applying the Arm's Length Principle.

The CUP method can be applied using internal or external comparable. Internal comparable refers to comparable transactions from the taxpayer itself while external comparable refers to comparable transactions from a third party. This method can be used when reliable internal comparable data is available.

The CUP method is the most applicable method when: (i) there are transactions conducted between independent parties involving the same type of property under similar conditions; and/or (ii) there is a price difference that can be reliably adjusted in the comparison of the conditions between the transactions. Otherwise, using other TP methods would be more appropriate."""

RPM_METHOD_DESC = """RPM is a method conducted by comparing the gross margin in a transaction of goods and/or services carried out between Affiliated Parties with the gross margin in a transaction of goods and/or services carried out between Independent parties in comparable conditions. In this method, the arm's length gross margin is calculated from the selling price in an independent transaction to the end customer.

The RPM is preferred when the goods are purchased in a controlled transaction and then resold to a third party. Its application is more appropriate when: (i) the reseller does not add substantial value to the goods; and (ii) the comparable transactions have a high degree of comparability in functional analysis.

The RPM is applicable when: (i) the reseller does not add substantially to the goods/services; (ii) the products are resold without significant physical alteration; and (iii) the reseller does not own valuable intangible property related to the products."""

CPM_METHOD_DESC = """CPM is a method conducted by comparing the gross margin in a transaction between Affiliated Parties with the gross margin in a transaction between Independent Parties in comparable conditions. The gross margin is determined using the cost of goods sold incurred by the party conducting the transaction.

The CPM is best applied when: (i) goods or services are sold to affiliated parties; (ii) the tested party provides services or manufactures products; and (iii) the tested party does not contribute unique and valuable intangible property. This method is commonly used for contract manufacturers or service providers.

To apply the CPM, it is important to ensure that costs included in the cost base are consistent between the tested party and comparable companies. Different accounting practices may necessitate adjustments to ensure comparability."""

PSM_METHOD_DESC = """PSM is used to determine the arm's length allocation of profits earned by each Affiliated Party in a transaction by identifying and allocating the combined profit from the transaction based on the functions performed, assets used, and risks assumed by each party.

The PSM is typically applied when: (i) transactions are highly integrated and cannot be analyzed independently; (ii) both parties contribute unique and valuable intangible property; and (iii) there is no sufficiently comparable independent transaction to apply another method.

There are two common approaches to the PSM: the Contribution Analysis and the Residual Analysis. The Contribution Analysis divides the combined profits based on each party's relative contribution. The Residual Analysis first allocates routine returns to each party, then divides the remaining profits based on each party's contribution of non-routine functions, assets, and risks."""

TNMM_METHOD_DESC = """TNMM is a method conducted by comparing the net profit margin of a transaction between Affiliated Parties with the net profit margin of a transaction between Independent Parties in comparable conditions. The net profit margin is determined by a suitable profit level indicator (PLI).

The TNMM is commonly used when: (i) one of the parties in the transaction performs routine functions and does not contribute valuable intangible property; (ii) reliable gross margin data is not available; and (iii) the tested party can be clearly identified.

The TNMM has the advantage of being less sensitive to differences in functions between related party transactions and independent transactions compared to traditional transaction methods (CUP, RPM, CPM), as net margins are less affected by transactional differences. However, the TNMM requires accurate financial information and proper identification of the profit level indicator (PLI)."""

# ─── Functional Analysis Standard Framework ───────────────────────────────────

FUNCTIONAL_ANALYSIS_INTRO = """Functional analysis is an analysis to identify economically significant functions, assets employed, and risks assumed by parties engaged in the transaction. Another purpose of function analysis is to look for companies/comparable transactions that have economically comparable activities and responsibilities to taxpayers and the selection of the most appropriate Transfer Pricing method.

In addition, functional analysis aims to determine the arm's length remuneration received by parties engaged in the transaction. For example, the higher risk borne by a party in the transactions, associated with greater probability of higher profit. However, what needs to be considered is the appropriateness of risk allocation in the agreed contract with the actual conditions assumed by the parties in transaction so that it can affect the actual profit generated. Therefore, it is very important to conduct a detailed risk analysis based on the facts and economic conditions of the transactions carried out by parties that have a special relationship.

This functional analysis is important because it provides an overview of value creation in the supply chain in general and transactions carried out by related parties. Functional analysis provides an understanding of the relative contribution of parties in transactions and their role in the creation of overall value.

In conducting the assessment and analysis of functions, the following factors should be taken into account:
a) the organizational structure and position of the company tested in the business group as well as the supply chain management of the business group;
b) the main functions carried out by a company such as design, processing, assembly, research, development, service, purchasing, distribution, marketing, promotion, transportation, finance, and management as well as the main characteristics of the company such as toll manufacturing, manufacturing with limited functions and risks (contract manufacturing), and manufacturing with full functions and risks (fully fledge manufacturing);
c) the type of assets used or to be used such as land, buildings, equipment, and intangible property, as well as the nature of those assets such as age, market price, and location;
d) risks that may arise and must be borne by each party conducting transactions such as market risk, investment loss risk, and financial risk."""

# ─── Search Criteria Template ─────────────────────────────────────────────────

SEARCH_CRITERIA_DESCRIPTIONS = {
    "legal_status": "In looking for a comparison company, the first thing that must be ensured is that the company chosen is a company with an active legal status. This is because the condition of a company that is in liquidation or inactive status has the potential to distort the company's financial results.",
    "independence": "The independence indicator criteria are needed to eliminate companies that are not independent as stipulated in Article 18 (4) of the Income Tax Law, namely companies that are listed as having shareholders with more than 25% ownership. In line with this, criteria are used in the database with independence indicators A+, A, A-.",
    "geography": "The arm's length price for the same property or service may differ in different market locations. Therefore, in order to obtain comparable conditions between related party transactions and independent transactions, the geographical locations selected are those that can reflect the level of market equivalence between the two transactions.",
    "industry": "One of the comparables criteria that need to be considered is related to the industry in which the company operates. As such, the selected comparable companies are those operating in industries comparable to the tested party.",
    "financial_availability": "Information on the financial statements of comparable companies that will be used in applying the arm's length principles for the tested party related party transactions.",
    "business_description": "Companies that do not have business description information (full overview) are not included in the analysis, because the company's business profile is not reliable to use.",
}

# ─── Affiliated Parties Criteria (Article 18 paragraph 4) ────────────────────

AFFILIATED_PARTIES_CRITERIA_INTRO = (
    "The criteria for related party in the perspective of Indonesian taxation have been regulated "
    "in Article 18 paragraph (4) of the Income Tax Law. Based on this article, two or more entities "
    "are considered to have a related party if they meet the following criteria:"
)

AFFILIATED_PARTIES_CRITERIA = [
    "Taxpayer who owns directly or indirectly at least 25% of equity of other Taxpayers, "
    "a relationship between Taxpayer through ownership of at least 25% of equity of two or more "
    "Taxpayer, as well as relationship between two or more Taxpayer concerned;",
    "Taxpayer who controls other Taxpayer, or two or more Taxpayers are directly or indirectly "
    "under the same control;",
    "Family relationship either through blood or through marriage within one degree of direct or "
    "indirect lineage.",
]

# ─── References ───────────────────────────────────────────────────────────────

REFERENCES = [
    "Law of the Republic of Indonesia Number 7 Year 1983 Concerning Income Tax as last amended by Law Number 7 Year 2021",
    "Regulation of the Minister of Finance of the Republic of Indonesia Number 172 of 2023 on the Application of the Principles of Arm's Length Principle in Transactions Affected by Special Relationships",
    "Government Regulation Number 74 of 2011",
    "Directorate General of Taxation Regulation No. PER-43/PJ/2010 as latest amended by PER-32/PJ/2011 regarding the Implementation of Arm's Length Principle in Transaction Between Associate Enterprises",
    "Directorate General of Taxation Regulation No. PER-22/PJ/2013 regarding Audit Guidelines for Taxpayers with Affiliate Party Transactions",
    "Circular No. SE-50/PJ/2013 regarding Technical Audit Guidance for Taxpayers with Affiliate Party Transactions",
    "OECD Transfer Pricing Guidelines for Multinational Enterprises and Tax Administrations 2022",
]

# ─── Method selection helper ──────────────────────────────────────────────────

METHOD_DESCRIPTIONS = {
    "CUP": CUP_METHOD_DESC,
    "RPM": RPM_METHOD_DESC,
    "CPM": CPM_METHOD_DESC,
    "PSM": PSM_METHOD_DESC,
    "TNMM": TNMM_METHOD_DESC,
}

# ─── Section 5.3: Comparability Analysis Introduction ────────────────────────

COMPARABILITY_ANALYSIS_INTRO = """\
Transfer Pricing Analysis aims to ensure that related party transactions are in accordance with arm's length principles. The main component of this process is comparability analysis, which compares related party transactions with independent transactions based on comparability factors. This analysis is an important element in the application of the arm's length principle, as stipulated in Article 8 of PMK-172 Year 2023.

Based on the regulation, independent transactions can be used as a comparison if: (a) transaction conditions are similar, (b) differences in conditions do not affect the price, or (c) differences can be adjusted to eliminate material impacts. The analysis process includes identifying transaction characteristics, selecting comparables, adjusting for differences, and determining the relevant independent transaction (Article 3 paragraphs (3) and (4)). Comparables can be internal (between taxpayers and independent parties) or external (between other independent parties) transactions.

Referring to PER-32/PJ/2011, comparability occurs if there are no material differences that affect prices or profits, or if the differences can be adjusted to eliminate their impact. This process includes steps such as identification of transaction details, selection of potential comparables, application of the Transfer Pricing method, and evaluation of the arm's length of the compared transactions.

As the core of applying the arm's length principle, the comparability analysis ensures that the selected comparables have a high degree of comparability to produce reliable results. As such, this analysis is key in maintaining the integrity of the Transfer Pricing process.

In order to obtain a reliable comparable, the application of comparability analysis is aimed at obtaining a high degree of comparability between affiliate transactions and independent transactions. In determining the degree of comparability, it is necessary to compare the factors of the transaction or company that materially affect the price or profit. These factors refer to five comparability factors. Based on the OECD TPG, the five factors of comparability in this context are:

a) Terms and Conditions in the Contract
Comparability analysis requires detailed information about transaction terms and conditions. For this reason, the analysis should start from the contents of the contract of agreement of the related party transaction, with the aim to see in detail the agreement. Some important things to note are: (i) pricing policy; (ii) sales requirement; (iii) guarantee; (iv) transaction period; (v) payment; (vi) possible changes in agreement; etc.

b) Functional Analysis (Function, Asset, and Risk)
The results of the functional analysis will provide better understanding of the extent to which functions (along with the inherent risks and assets) of independent transactions are comparable to the related party transaction being analyzed. Review of the function and risk comparability requires an understanding of the market situation when a related party transaction is conducted. In other words, identification of market structure, level of competition, industry value drivers, and business development is needed to assess the company's functions and risks.

c) Transaction of Products/Services
Things that need to be considered with respect to products or services are as follows: (i) physical characteristics of goods; (ii) quality of goods; (iii) availability of goods; (iv) durability of goods; and (v) number of product offers. In case of services and intangible assets, in general it can be seen from the benefits, nature, type and type of agreement. Product comparison will be less difficult when it is conducted on products that do not have much added value or on commodity products and raw materials.

d) Business Strategy
Business strategies and business schemes are one of the factors that are difficult to compare, because they are unique and include all economic considerations faced by multinational companies. Some important information in business strategies, for example: market penetration policies, market expansion or going concern strategies, new product launches that are innovative, business diversification, package sales, etc.

e) Economic Conditions
If the business strategy observes more at the operations of multinational companies, the economic situation factor emphasizes the economic conditions when the transaction is carried out or the effect on the price level or profit level indicator. Some examples of comparable economic situations are: (i) market size; (ii) geographical location; (iii) level of business competition; (iv) market level; (v) availability of substitute goods or services; (vi) consumer purchasing power; (vii) the level of demand and supply in the market as a whole as well as regionally; (viii) the nature and scope of government regulations in the market; (ix) production costs (including land costs, labour costs and capital) and transportation costs; (x) transaction date and time; etc.\
"""

# ─── Section 5.3.1: Use of Internal and External Comparable ──────────────────

INTERNAL_EXTERNAL_COMPARABLE = """\
One important step that must be done in comparability analysis is search and selection of comparables. The source of the comparison can come from transactions conducted with internal Independent Parties (internal comparable) or transactions conducted between external Independent Parties (external comparable). The choice of using an internal or external comparable must meet the factors that can influence the level of comparability.

Internal Comparable
Internal comparable is a comparable obtained from company's data that is analyzed for its arm's length transaction. However, internal comparable can also obtained from transactions conducted by related party (which are the counter-party of transactions) with independent parties.

Basically, internal comparable is preferred compared to external comparable. However, the reliability of internal comparable must still refer to the five existing comparability factors.

External Comparable
External comparable data is an arm's length reference price data or arm's length profit in comparable transactions conducted by other taxpayers with parties that have no special relationship. In this case, the source of the data used to find external comparables obtained from the outside of the tested company. To use external comparables, information of comparable transaction conducted by an independent party to related party is required. In practice, the use of external comparable is very dependent on the availability of data sources, either in the form of market prices or financial data obtained through commercial databases.

In this case, the external comparable analysis uses information (financial or non-financial) of comparable companies through the selection in an external database using Bureau Van Dijk TP Catalyst Database.

Furthermore, if the results of the comparability analysis show that the internal comparable is not comparable and unreliable, then the external comparable will be selected in the transfer pricing analysis.\
"""


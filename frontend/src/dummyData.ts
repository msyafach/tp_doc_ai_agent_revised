import type { ProjectState } from "./types";

export const DUMMY_DATA: Partial<ProjectState> = {
  company_name: "PT Sakura Manufaktur Indonesia",
  company_short_name: "PT SMI",
  company_address: "Jalan Industri Raya No. 12, Kawasan Industri MM2100, Cikarang Barat, Bekasi 17520",
  establishment_info: "Deed of Establishment No. 45, dated 12 March 2010, by Notary Santoso, S.H., M.Kn. — approved by Ministry of Law and Human Rights No. AHU-123456.AH.01.01",
  fiscal_year: "2024",
  parent_company: "Sakura Manufacturing Holdings Pte. Ltd.",
  parent_group: "Sakura Group",
  brand_name: "Sakura",
  employee_count: "856",

  shareholders: [
    { name: "Sakura Manufacturing Holdings Pte. Ltd.", shares: "99,000", capital: "99,000,000,000", percentage: "99.00%" },
    { name: "PT Mitra Sakura Indonesia",               shares: "1,000",  capital: "1,000,000,000",  percentage: "1.00%" },
  ],
  management: [
    { position: "President Director", name: "Hiroshi Tanaka" },
    { position: "Director",           name: "Budi Santoso" },
    { position: "Commissioner",       name: "Yuki Yamamoto" },
  ],

  affiliated_parties: [
    { name: "Sakura Manufacturing Holdings Pte. Ltd.", country: "Singapore", relationship: "Parent Company (99% shareholder)", transaction_type: "Royalty/License fees" },
    { name: "Sakura Components Co., Ltd.",             country: "Japan",     relationship: "Affiliated entity (same group)",   transaction_type: "Purchase of raw materials" },
  ],

  business_activities_description: "PT Sakura Manufaktur Indonesia (PT SMI) is a manufacturing company engaged in the production of precision automotive components. The company operates as a contract manufacturer, producing components to the specifications provided by its parent company and affiliated entities. Products are primarily distributed to affiliated parties and third-party original equipment manufacturers (OEMs) in the automotive sector.",

  products: [
    { name: "Precision Gear Components",  description: "High-precision gears for automotive transmission systems" },
    { name: "Engine Bracket Assemblies",  description: "Structural brackets for engine mounting systems" },
  ],

  transaction_type: "Purchase of tangible goods",
  transaction_details_text: "In FY 2024, PT SMI purchased raw materials (steel billets and aluminum alloys) from Sakura Components Co., Ltd. (Japan) with a total value of IDR 145,000,000,000. The purchased raw materials are used exclusively in the production of precision automotive components sold to affiliated and third-party customers.",
  pricing_policy: "The purchase price of raw materials from Sakura Components Co., Ltd. is determined based on a cost-plus arrangement, where the price equals the supplier's production cost plus a mark-up. The mark-up percentage is reviewed annually and agreed upon by both parties at arm's length.",

  affiliated_transactions: [
    { name: "Sakura Components Co., Ltd.", country: "Japan", affiliation_type: "Affiliated entity (same group)", transaction_type: "Purchase of raw materials", value: "145,000,000,000", note: "" },
    { name: "Sakura Manufacturing Holdings Pte. Ltd.", country: "Singapore", affiliation_type: "Parent Company", transaction_type: "Royalty/License fees", value: "8,700,000,000", note: "" },
  ],
  independent_transactions: [
    { name: "PT Logam Utama",     country: "Indonesia", transaction_type: "Purchase of raw materials", type_of_product: "Steel billets",      amount_idr: "12,000,000,000", quantity: "2,400", avg_price_per_unit: "5,000,000" },
    { name: "PT Jasa Kirim Cepat", country: "Indonesia", transaction_type: "Logistics services",        type_of_product: "Freight & handling", amount_idr: "3,500,000,000",  quantity: "",      avg_price_per_unit: "" },
  ],

  financial_data: {
    sales: "285,000,000,000", cogs: "215,000,000,000", gross_profit: "70,000,000,000",
    gross_margin_pct: "24.56", operating_expenses: "45,000,000,000", operating_profit: "25,000,000,000",
    financial_income: "-2,500,000,000", income_before_tax: "22,500,000,000",
    income_tax: "5,625,000,000", net_income: "16,875,000,000",
  },
  financial_data_prior: {
    sales: "256,000,000,000", cogs: "196,000,000,000", gross_profit: "60,000,000,000",
    gross_margin_pct: "23.44", operating_expenses: "42,000,000,000", operating_profit: "18,000,000,000",
    financial_income: "-3,200,000,000", income_before_tax: "14,800,000,000",
    income_tax: "3,700,000,000", net_income: "11,100,000,000",
  },

  comparability_factors: [
    { factor: "Contract Terms and Conditions", description: "PT SMI purchases raw materials under a written supply agreement with Sakura Components Co., Ltd. The contract stipulates fixed pricing, delivery terms (FOB), and a 12-month agreement period with annual review." },
    { factor: "Product Characteristics",       description: "The raw materials are standardized steel billets and aluminum alloys, widely traded commodities with observable market prices." },
    { factor: "Functional Analysis",           description: "PT SMI acts as a contract manufacturer — it takes title to raw materials, bears inventory risk, and handles all manufacturing functions. The comparable companies identified also bear similar manufacturing risks." },
    { factor: "Business Strategy",             description: "PT SMI's strategy is to maintain its position as a reliable, high-quality contract manufacturer. No significant restructuring occurred in FY 2024." },
    { factor: "Economic Conditions",           description: "Both the tested party and comparables operate in the Indonesian automotive components industry, subject to similar market conditions, exchange rate risks, and regulatory environments." },
  ],

  search_criteria_results: [
    { step: "1", criteria: "All active companies in Indonesia",                          result_count: "12,345" },
    { step: "2", criteria: "NACE/ISIC: Manufacture of motor vehicle parts & accessories", result_count: "487" },
    { step: "3", criteria: "Independence indicator: A+, A, A-",                          result_count: "203" },
    { step: "4", criteria: "Accounts available for at least 3 years (2020-2022)",         result_count: "98" },
    { step: "5", criteria: "Companies with overview/description information",             result_count: "54" },
    { step: "6", criteria: "Manual review — excluding non-comparable business models",    result_count: "8" },
  ],
  comparable_companies: [
    { name: "PT Astra Komponen Indonesia",   country: "Indonesia", description: "Manufacturer of automotive metal components for OEMs",     ros_data: "4.21" },
    { name: "PT Showa Indonesia Mfg",        country: "Indonesia", description: "Contract manufacturer of steering and suspension parts",   ros_data: "3.87" },
    { name: "PT Inti Ganda Perdana",         country: "Indonesia", description: "Axle and driveshaft manufacturer for commercial vehicles", ros_data: "5.12" },
    { name: "PT Denso Indonesia",            country: "Indonesia", description: "Manufacturer of automotive components and systems",        ros_data: "6.34" },
    { name: "PT Yorozu Automotive Indonesia",country: "Indonesia", description: "Suspension parts and pressed components manufacturer",     ros_data: "3.45" },
    { name: "PT Aisin Indonesia",            country: "Indonesia", description: "Transmission and body parts manufacturer",                ros_data: "4.89" },
  ],

  rejection_matrix: [
    { name: "PT Astra Komponen Indonesia",    limited_financial_statement: false, negative_margin: false, consolidated_financial_statement: false, different_main_activity: false, non_comparable_line_of_business: false, limited_information_website: false, accepted: true },
    { name: "PT Showa Indonesia Mfg",         limited_financial_statement: false, negative_margin: false, consolidated_financial_statement: false, different_main_activity: false, non_comparable_line_of_business: false, limited_information_website: false, accepted: true },
    { name: "PT Inti Ganda Perdana",          limited_financial_statement: false, negative_margin: false, consolidated_financial_statement: false, different_main_activity: false, non_comparable_line_of_business: false, limited_information_website: false, accepted: true },
    { name: "PT Denso Indonesia",             limited_financial_statement: false, negative_margin: false, consolidated_financial_statement: false, different_main_activity: false, non_comparable_line_of_business: false, limited_information_website: false, accepted: true },
    { name: "PT Yorozu Automotive Indonesia", limited_financial_statement: false, negative_margin: false, consolidated_financial_statement: false, different_main_activity: false, non_comparable_line_of_business: false, limited_information_website: false, accepted: true },
    { name: "PT Aisin Indonesia",             limited_financial_statement: false, negative_margin: false, consolidated_financial_statement: false, different_main_activity: false, non_comparable_line_of_business: false, limited_information_website: false, accepted: true },
    { name: "PT Akebono Brake Astra Indonesia", limited_financial_statement: false, negative_margin: false, consolidated_financial_statement: true,  different_main_activity: false, non_comparable_line_of_business: false, limited_information_website: false, accepted: false },
    { name: "PT Mekar Armada Jaya",           limited_financial_statement: true,  negative_margin: false, consolidated_financial_statement: false, different_main_activity: false, non_comparable_line_of_business: false, limited_information_website: false, accepted: false },
    { name: "PT Trimitra Chitrahasta",        limited_financial_statement: false, negative_margin: true,  consolidated_financial_statement: false, different_main_activity: false, non_comparable_line_of_business: false, limited_information_website: false, accepted: false },
    { name: "PT Enkei Indonesia",             limited_financial_statement: false, negative_margin: false, consolidated_financial_statement: false, different_main_activity: true,  non_comparable_line_of_business: false, limited_information_website: false, accepted: false },
    { name: "PT Selamat Sempurna Tbk",        limited_financial_statement: false, negative_margin: false, consolidated_financial_statement: false, different_main_activity: false, non_comparable_line_of_business: true,  limited_information_website: false, accepted: false },
    { name: "PT Gajah Tunggal Tbk",          limited_financial_statement: false, negative_margin: false, consolidated_financial_statement: false, different_main_activity: true,  non_comparable_line_of_business: true,  limited_information_website: false, accepted: false },
  ],

  selected_method: "TNMM",
  selected_pli: "ROS",
  tested_party: "PT SMI",
  analysis_period: "2020-2022",
  quartile_range: { q1: 3.72, median: 4.55, q3: 5.50 },
  tested_party_ratio: 8.77,

  non_financial_events: "In FY 2024, PT SMI completed the installation of a new CNC machining line, increasing production capacity by 25%. No significant force-majeure events, restructuring transactions, or extraordinary items affected the company's operations during the fiscal year.",

  supply_chain_management: "",

  agent_ran: false,
};

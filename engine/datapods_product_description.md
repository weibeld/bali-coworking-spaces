# Datapods — Product Description

## 1. Problem

Creating useful datasets requires collecting **records that all share the same fields** (e.g. title, author, rating).

In practice, this is difficult and tedious:

- each new record requires manual research for all fields  
- ensuring consistency across records is hard  
- keeping data up to date requires ongoing effort  

As a result:
- datasets are often incomplete  
- inconsistent  
- or outdated  

**Datapods solves this problem** by providing a system that enables users to:

> **define structured datasets where all records conform to the same fields, and be actively supported in creating and maintaining them**

---

## 2. Core Features

### 2.1 Completion
- Automatically researches and extracts missing field values  
- Uses **user-defined data sources and instructions**  
- Ensures all records are **complete and consistent with the defined schema**  

---

### 2.2 Updates
- Re-extracts values for **volatile fields**  
- Keeps datasets up to date over time  
- Runs continuously or on demand  

---

### 2.3 Discovery
- Automatically discovers new records that match user-defined criteria  
- Based on **natural language instructions** (e.g. “find all X”)  
- For each discovered record, **extracts all defined fields according to the dataset schema**  

---

## 3. Data Definition & Extraction

Users define:

- the **schema** (fields of the dataset)  
- the **data sources** to use  
- **extraction instructions** for each field  

This allows the system to:

- automatically obtain data  
- fill missing values  
- maintain consistency across all records  

A key aspect is that:

> **the user explicitly defines how data is obtained and structured**

Discovery works via:

- natural-language instructions  
- arbitrary levels of specificity  

---

## 4. Interface

All datasets are:

- exposed via an **API as JSON**  
- accessible to any client application  

This allows the data to be:

- displayed in any format  
- used in any application  
- integrated into existing systems  

---

## 5. Automation and Manual Control

Datapods combines automation with user control:

- data can always be **edited manually**  
- users can add or override values  
- users decide:
  - what is automated  
  - what is manual  

This enables:

> **curation where necessary, automation where possible**

---

## 6. Data Evolution

Datasets are not static and can evolve over time:

- users can edit the schema  
- reshape datasets  
- update extraction instructions  

The system adapts and:

- re-extracts data  
- updates existing records  

This provides flexibility to:

> **continuously refine and improve structured datasets**

---

## 7. Backups & Version Control (Optional)

Datasets can optionally be:

- backed by Git repositories  

This enables:

- full version control  
- history tracking  
- recovery of previous states  

It provides:

> **confidence that no data is ever lost and encourages experimentation**

---

## 8. Related Solutions

- **Firecrawl Agent** — https://www.firecrawl.dev/app/agent  
  Firecrawl Agent focuses on automated web data extraction. Users can define targets (e.g. websites or pages), and the system crawls and extracts structured data from them. It is particularly useful for scraping and structuring information from the web, with an emphasis on automation and scalability.

- **rtrvr.ai** — https://www.rtrvr.ai/  
  rtrvr.ai provides tools for retrieving and extracting information from online sources. It enables users to query and gather data from across the web and transform it into usable structured outputs. The focus is on flexible retrieval and transformation of external data into formats suitable for further use.

- **Airtable AI Agents** — https://www.airtable.com/platform/ai-agents  
  Airtable AI Agents extend Airtable’s database-like environment with AI-driven automation. They allow users to enrich records, automate workflows, and extract information within Airtable bases. The system combines structured data management with AI-assisted operations directly inside a familiar spreadsheet-like interface.

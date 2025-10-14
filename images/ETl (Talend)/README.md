## 🧹 ETL & Data Cleaning  

The ETL process was developed using **Talend Open Studio** and includes three main jobs:  

- 🧽 **Data Cleaning Job:** Removes duplicates, corrects anomalies, validates data types.  
- 🧱 **Dimension Job:** Loads dimension tables (`DIM_CLIENT`, `DIM_CARTE`, `DIM_COMPTE`, `DIM_PACK`, etc.).  
- 💾 **Fact Job:** Integrates transactions into the **Fact Table** with lookups to all dimensions.  

All data transformations follow a structured model within the **`BANQUE`** schema in PostgreSQL.

---

## 🏦 Data Warehouse Design  

The **Data Warehouse** was modeled in a **Star Schema**, including:  

- **Fact Table:** `FACT_TRANSACTION`  
- **9 Dimension Tables:**  

This model supports **multidimensional analysis**.

---

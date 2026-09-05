# 🛒 Retail Pricing & Rolldown SQL Engine

## 📌 Project Overview
The **Retail Pricing & Rolldown SQL Engine** is a full-stack, data-driven application designed to simulate enterprise retail pricing changes and electronic shelf labeling systems. Developed by an internal Walmart associate, this project demonstrates how to connect scalable backend APIs with a real relational SQL database to manage live product data, calculate promotional discounts, and instantly update customer-facing digital signage.

## 💡 Business Value & Use Case
In physical and digital storefronts, price accuracy and clearance syncs must happen instantly across millions of store devices. This application showcases a direct architectural solution by:
- **Relational Data Management**: Implementing a structured SQLite database layer to store complex item definitions, baseline prices, and promotional status flags.
- **Dynamic Business Logic**: Running an automated backend script that scans database attributes and dynamically computes a 15% markdown for items tagged for a corporate 'Rolldown'.
- **Secure Parameterized Queries**: Utilizing secure SQL execution parameters to pull structural data safely, eliminating common database vulnerability vectors.

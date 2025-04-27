# MDFDS - Patient Follow-up System

## Project Overview

In Morocco, like many developing countries, healthcare systems face significant challenges in ensuring effective **patient follow-up** after medical consultations. This is particularly critical for patients with **chronic diseases** such as:

- Diabetes
- Hypertension
- Post-surgical recovery
- Mental health conditions

After hospital or clinic visits, many patients are left without consistent monitoring. Several barriers exacerbate this problem:

- Lack of infrastructure for remote patient monitoring
- Inconsistent communication between patients and healthcare providers
- Overburdened healthcare workers unable to manually track every patient's status
- Limited access to in-person healthcare, especially in rural or underserved areas

These issues lead to:

- Worsened health outcomes
- Increased hospital readmissions
- Higher healthcare costs

**The MDFDS Patient Follow-up System** aims to bridge these gaps by leveraging **Artificial Intelligence (AI)** to automate follow-up procedures, provide personalized monitoring, and equip doctors with **real-time dashboards** for timely interventions.

---

## Key Features

- **Automated Patient Follow-up**: Ensures continuous patient monitoring post-consultation without manual intervention.
- **Real-time Dashboard**: Provides healthcare providers with instant visibility into patient statuses, allowing proactive care.
- **AI-Powered Monitoring**: Predicts patient deterioration and flags high-risk cases.
- **Infrastructure-light Approach**: Designed to work even in resource-constrained environments, making it ideal for rural healthcare.

---

## Installation and Setup

Follow these steps to get the system up and running:

### 1. Clone the repository

```bash
git clone https://github.com/IDRISSELWAANABI/MDFDS-Patient-follow-up-system.git
cd MDFDS-Patient-follow-up-system
```

### 2. Give permission for setup automation

```bash
chmod +x ./orchestrator.sh
```

### 3. Run the automation script

```bash
./orchestrator.sh
```

The `orchestrator.sh` script will handle:

- Installing backend dependencies
- Launching the backend server
- Setting up the frontend application
- Running both services

> **Note:** Make sure you have Ollama installed and run:
```bash
ollama run gemma3:12b
```

---

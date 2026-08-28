# Program — Sensory Lab Workspace

> **Status:** Active (v1.0)
> **Source:** Derived from `docs/IDEAS.md` (letter of intention) plus the decisions recorded in Section 4. Every decision is marked with the question it answers, so nothing is silently assumed.

---

## 1. Purpose

The project is an application built for the operations of a Sensory lab.

The role of the lab is to support product development through:

- Defining sensory attributes.
- Developing sensory methods.
- Recruiting panelists.
- Running experiments.
- Analyzing data.

## 2. Objectives

1. Become a centralized workspace for the daily work of the Sensory Lab.
2. Support users in tracking the timeline and progress of experiments.
3. Track the performance of panels and panelists.
4. Analyze and support decision making based on sensory data.

## 3. Functional Groups

The application consists of **4 main groups of functions**.

### 3.1 Overview
Focuses on **experiments**, **projects**, and **workloads of individuals**.

### 3.2 Library
Contains **pre-prepared information** used before a test happens: test methods, panelists, panels, sets of attributes, etc.

### 3.3 Lab
Where **experiments and tests actually happen**, including results and sample information. Includes blind sample coding and serving order randomization (Decision D5).

### 3.4 Analyze
Shows **analytical results**: ANOVA tables, correlation matrix, panel performance, trends, etc. (first version scope: Decision D2).

## 4. Decisions

Each decision records the answer to a question in the earlier draft of this document.

| # | Decision | Answered by |
|---|---|---|
| **D1** | Analyze provides a set of **pre-defined analyses** that users choose and run. Result visualization and export are included. | Q1 |
| **D2** | First version analyses: **ANOVA tables, correlation matrix, panel performance, trends**. Detailed statistical definitions are discussed at implementation time. | Q2 |
| **D3** | Sensory data is collected via an **in-app ballot**: panelists use the application (via QR or link) to choose the correct test and input their answers. | Q3 |
| **D4** | **Panelists are managed in the Library**; their responses are recorded against them, so panel/panelist performance can be tracked. | Q3, Q5 |
| **D5** | **Blind sample coding and serving order randomization are in scope.** Session management (booth allocation, scheduling) is **out of scope**. | Q4 |
| **D6** | Main users are **sensory lab staff**. Panelists are temporary users who input answers during test sessions (via QR or link). | Q5 |
| **D7** | The Library contains only the registries stated in IDEAS.md: **test methods, attributes, panels, panelists**. No scales/SOPs/training logs for now. | Q6 |
| **D8** | **Technology:** Streamlit frontend; backend as **microservices** (separate deployable processes, which may include external services) that Streamlit interacts with; Python as the main language managed by `uv`; prefer built-in library functions over custom widgets/functions. | Q7 |
| **D9** | Deployment is for a **single lab**. | Q9 |
| **D10** | **No data migration/import** from existing systems is needed. | Q10 |
| **D11** | Minimal **test** concept: a test = experiment + method + a set of samples + a set of attributes + a set of panelists. The system generates each panelist's serving plan (blind codes + order) and ballot; responses are tagged to the test. | Discussion |

## 5. Developing Philosophies

- **Page-per-folder modularization:** each Streamlit page has its own folder.
- **Microservice backend:** separate deployable processes; Streamlit interacts with them via APIs.
- **Prefer built-ins:** use built-in functions from libraries wherever possible; avoid heavily customizing widgets or functions.
- **Python + `uv`** for the main language and dependency management.

## 6. Open Points

Items not yet decided; they will not be assumed.

- **Panelist identification mechanism:** how a panelist identifies themselves when answering (e.g., login vs. a per-panelist link) — to be decided.
- **Detailed analysis definitions:** statistical models, panel performance metrics, and what "trends" means — to be discussed at implementation time (per D2).

## 7. Revision Notes

- v1.0: Finalized from the IDEAS.md letter of intention and answers to the open questions; supersedes the earlier draft.
- Future changes to scope, decisions, or philosophies must be recorded here, marked with the discussion or decision that motivated them.

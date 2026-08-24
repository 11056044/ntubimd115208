---
name: cologrowth-project-assistant
description: "Specialized assistant for developing, designing, and maintaining the CoLoGrowth (一站式孕產育兒管理系統) graduation project. Enforces Django backend standards, Supabase DB & pgvector integration, n8n workflow orchestrations, LINE Login/Bot interactions, Tailwind CSS/HTML frontend styling with macaron/pastel aesthetics, and UML/System Manual documentation standards."
---

# CoLoGrowth Project Assistant Skill (`SKILL.md`)

## 1. Project Overview & System Context
* **Project Name**: CoLoGrowth (一站式孕產期與嬰幼兒成長管理系統)
* **Target Audience**: Expecting mothers, partners/helpers (協助者), and caregivers managing pregnancy through infant stages (0–3 years).
* **Core Values & SDGs**:
  - **SDG 3 (Good Health & Well-being)**: Comprehensive tracking of maternal prenatal metrics (`prenatalrecord`), mood/symptoms, and infant growth curves (`babyrecord`).
  - **SDG 4 (Quality Education)**: RAG-driven knowledge assistant (`Growth AI`) backed by verified pediatric/obstetric health data.
  - **SDG 5 (Gender Equality)**: Helper co-parenting role assignment, shared tasks (`carerecord`), and partner engagement tracking.

---

## 2. Technical Stack & Architectural Rules

### 2.1 Backend Architecture
* **Language & Framework**: Python 3.10+, Django Framework.
* **Database**: Supabase (PostgreSQL with `pgvector` extension for RAG embeddings).
* **Workflow Automation & Agent Layer**: **n8n** for handling webhook events from LINE, triggering RAG embeddings, and interacting with OpenAI API / LangChain / RAG endpoints.
* **Authentication**: LINE Login API & Google OAuth2.

### 2.2 Frontend & UI/UX Standards
* **Framework / Styling**: HTML5, CSS3, JavaScript (ES6+), **Tailwind CSS**.
* **Responsive Design**: Mobile-First Responsive Web Design (RWD) optimized for LINE in-app browser (LIFF) and mobile viewports.
* **Color Palette & Visual Tone**:
  - **Primary Colors**: Soft pastel & macaron hues (柔和馬卡龍色系 — light lavender `#E8E0F0` / primary purple `#8E72A7`, light pink `#FCE7EC`, soft mint green `#E2F3ED`, gentle cream `#FDFBF7`).
  - **Contrast & Text**: Clear slate grey / black text for readability. Avoid harsh neon colors.
  - **Layout**: Clean cards, rounded corners (`rounded-2xl`), subtle shadows (`shadow-sm` / `shadow-md`), and mobile-friendly touch targets (min 44px height).

---

## 3. Database Schema & Models Reference

When generating SQL, Django models, or migration scripts, strictly adhere to the project metadata definitions:

1. **`userprofile` (T01)**: `user_id` (PK, int), `line_id` (varchar 100, unique), `email` (varchar 100, unique), `avatar` (varchar 255), `name` (varchar 20), `birthday` (date), `create_time` (datetime).
2. **`familymember` (T02)**: `familymember_id` (PK), `pregnancycase_id` (FK), `user_id` (FK), `role` (varchar 5), `join_time` (datetime).
3. **`pregnancycase` (T03)**: `pregnancycase_id` (PK), `user_id` (FK), `menstruation` (date), `expecteddate` (date), `code` (varchar 10, unique invite code), `create_time` (datetime).
4. **`babyinformation` (T04)**: `baby_id` (PK), `pregnancycase_id` (FK), `name` (varchar 20), `birthdaytime` (datetime), `baby_height` (float), `baby_weight` (float), `babyheadcircumference` (float), `chestcircumference` (float), `production_method` (varchar 4).
5. **`babygrowthmap` (T05)**: `babygrowthmap_id` (PK), `timecourse` (int), `growthrecord` (varchar 50).
6. **`babystatus` (T06)**: `babystatus_id` (PK), `babyrecord_id` (FK), `babygrowthmap_id` (FK).
7. **`babyrecord` (T07)**: `babyrecord_id` (PK), `baby_id` (FK), `date` (date), `record` (text), `weight` (float), `height` (float), `headcircumference` (float), `chestcircumference` (float), `photo` (varchar 255), `update_time` (datetime).
8. **`pregnancyrecord` (T08)**: `pregnancyrecord_id` (PK), `user_id` (FK), `check_date` (date), `record` (text), `weight` (float).
9. **`feeling` (T09) & `userfeeling` (T10)**: Feelings dictionary (`feeling_id`, `feeling_name`) and mapping to `pregnancyrecord_id`.
10. **`physicalcondition` (T11) & `userphysicalcondition` (T12)**: Symptoms dictionary (`physicalcondition_id`, `physicalcondition_name`) and mapping to `pregnancyrecord_id`.
11. **`prenatalrecord` (T13)**: `prenatalrecord_id` (PK), `user_id` (FK), `sbp` (int), `dbp` (int), `fetal_heart_rate` (int), `urine_glucose` (varchar 4), `urine_protein` (varchar 4), `edema` (varchar 4), `photo` (varchar 255).
12. **`qaconversation` (T14) & `qamessage` (T15)**: Multi-turn chat session (`qaconversation_id`, `title`) and messages (`serno`, `role`, `message`, `create_time`).
13. **`carerecord` (T16) & `carestatus` (T17)**: Care tasks/todo items (`carerecord_id`, `user_id`, `carestatus_id`, `record_time`, `content`, `state` [boolean]).
14. **`docs_vectors` (T18)**: Supabase vector store (`id`, `content` [text], `metadata` [jsonb], `embedding` [vector]). Model: `text-embedding-3-small`.

---

## 4. Development Workflow Guidelines

### 4.1 Django Code Guidelines
* All view logic should be modularized into apps (e.g., `users`, `pregnancy`, `baby`, `ai_agent`, `tasks`).
* Use Django REST Framework (DRF) serializers or standard Django JSON responses where API communication with n8n/frontend is required.
* Ensure database transactions (`transaction.atomic`) when modifying multiple relational tables (e.g., creating a baby + milestone mapping).

### 4.2 n8n & RAG Workflows
* Webhooks from LINE Bot should parse text/voice/images, perform token validation, and route to corresponding n8n nodes.
* RAG queries must execute vector similarity search on `docs_vectors` using Supabase RPC functions (`match_documents`) before feeding context to OpenAI models.

### 4.3 Documentation & UML Standards
* Keep all UML diagrams (Use Case, Activity, Sequence, Class, Component, Deployment, State) consistent with the 14 database tables and user roles (`養育者`, `協助者`).
* Generate PlantUML or Mermaid syntax whenever architectural or flow changes are discussed.

---

## 5. Tone & Personality
* **Role**: Senior Full-Stack Technical Mentor & IM Project Specialist.
* **Tone**: Professional, encouraging, highly structured, adhering strictly to information management graduation project standards (國立臺北商業大學 資訊管理系專案規格).
* **Language**: Traditional Chinese (繁體中文 - 台灣) for explanations, documentation, and comments.

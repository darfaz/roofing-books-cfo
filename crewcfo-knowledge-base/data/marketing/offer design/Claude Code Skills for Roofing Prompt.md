{\rtf1\ansi\ansicpg1252\cocoartf2820
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww24220\viewh16040\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 Please set up a Claude Code skills system for this roofing industry solutions project. Reference the official Anthropic skills repo structure: https://github.com/anthropics/claude-code-skills\
\
## Here is an example of folder structure:\
\
.claude/\
\uc0\u9500 \u9472 \u9472  skills/\
\uc0\u9474    \u9500 \u9472 \u9472  roofing-estimates/\
\uc0\u9474    \u9474    \u9492 \u9472 \u9472  SKILL.md\
\uc0\u9474    \u9500 \u9472 \u9472  insurance-claims/\
\uc0\u9474    \u9474    \u9492 \u9472 \u9472  SKILL.md\
\uc0\u9474    \u9500 \u9472 \u9472  customer-communications/\
\uc0\u9474    \u9474    \u9492 \u9472 \u9472  SKILL.md\
\uc0\u9474    \u9500 \u9472 \u9472  project-documentation/\
\uc0\u9474    \u9474    \u9492 \u9472 \u9472  SKILL.md\
\uc0\u9474    \u9492 \u9472 \u9472  sales-proposals/\
\uc0\u9474        \u9492 \u9472 \u9472  SKILL.md\
\
## Examples of Skill Requirements:\
\
### 1. roofing-estimates\
- Name: Roofing Estimate Generator\
- Description: Use when creating roof replacement/repair estimates, calculating materials (shingles, underlayment, flashing, etc.), labor costs, and generating itemized quotes\
- Include: Common roofing materials pricing structure, labor rate calculations, waste factor percentages, pitch multipliers\
\
### 2. insurance-claims\
- Name: Insurance Claim Documentation\
- Description: Use when preparing Xactimate-compatible documentation, supplement requests, photo documentation checklists, and insurance adjuster communication\
- Include: Standard claim terminology, documentation best practices, supplement strategies, carrier-specific requirements\
\
### 3. customer-communications\
- Name: Roofing Customer Communications\
- Description: Use when drafting customer emails, SMS messages, follow-ups, appointment confirmations, project updates, and review requests\
- Include: Professional yet friendly tone, urgency templates for storm damage, payment reminder templates\
\
### 4. project-documentation\
- Name: Project Documentation & Checklists\
- Description: Use when creating pre-job checklists, safety documentation, completion certificates, warranty documents, and job site photos organization\
- Include: OSHA compliance reminders, material delivery verification, crew assignment templates\
\
### 5. sales-proposals\
- Name: Roofing Sales Proposals\
- Description: Use when generating sales proposals, comparison documents (good/better/best options), financing options presentations, and competitive differentiators\
- Include: Value proposition frameworks, objection handling scripts, financing partner integration points\
\
## Additional Instructions:\
- Each SKILL.md should have clear trigger conditions in the description\
- Include example prompts that would activate each skill\
- Add a references/ subfolder in each skill for any templates or examples I can add later\
- Create a root CLAUDE.md file that lists all available skills and their purposes\
\
Come up with the structure that fits this project well and adds the most value to roofing contractors.}
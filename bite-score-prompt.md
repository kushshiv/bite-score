# BiteScore MVP Build Prompt and Founder Playbook

## Purpose

This document contains:
- A full prompt to paste into Cursor to build the first web MVP of **BiteScore**.
- Product strategy for web-first vs mobile.
- Legal, branding, and trademark checks.
- Business registration guidance for a founder living in Germany and targeting a global audience.
- Practical guidance on what to do first: build MVP, register company, or file trademarks.

BiteScore is envisioned as a trust and transparency platform for food safety, hygiene, and food quality, positioned more like a structured trust-score platform than a simple restaurant-review app. Trademark clearance should be checked through official trademark databases such as WIPO, USPTO, EUIPO, DPMA, and India’s IP office before committing to the name globally.[cite:247][cite:268][cite:258][cite:249]

## Recommendation summary

The best order of operations for this project is usually:
1. Validate the product with a small MVP and landing page.
2. Check naming conflicts, domain availability, and logos early.
3. Register a company only when there is commitment to launch, billing, or contracts.
4. File a trademark once the name is chosen and there is confidence it will be used commercially in target markets.

A global trademark strategy should begin with database searches because WIPO’s Global Brand Database is a standard starting point for international searches, and national or regional offices like USPTO, EUIPO, and DPMA should also be checked for core launch markets.[cite:247][cite:267][cite:268][cite:258][cite:249]

## Web-first or mobile-first

A **web-first MVP** is the right choice. A trust-and-rating product needs fast iteration, search discoverability, public pages, moderation tooling, admin workflows, and simple onboarding, all of which are easier to build and validate on the web first. Mobile can be added later as either:
- a responsive web app/PWA first,
- then native apps if user behavior proves photo upload, local discovery, and repeat reviews are strongly mobile-driven.

For MVP, build:
- A responsive web app that works well on mobile browsers.
- PWA basics if easy.
- No native iOS/Android app in V1 unless there is extra time.

---

# Full Cursor Prompt

Copy everything in this section into Cursor.

## Cursor Prompt Start

Build a production-ready MVP for a startup called **BiteScore**.

### Product vision
BiteScore is a global trust and transparency platform for food safety, hygiene, and food quality. It should feel like a blend of:
- Levels.fyi style structured scoring and data transparency,
- consumer trust platform,
- restaurant/place profile pages,
- evidence-based reviews rather than opinion-only reviews.

This is **not** a generic restaurant review app. The focus is food trust, hygiene, and quality signals.

### Core idea
Users can discover food businesses and see a structured trust score based on:
- hygiene observations,
- food handling practices,
- oil reuse concerns,
- cleanliness,
- packaging safety,
- water safety,
- staff hygiene,
- consistency of reviews,
- evidence-backed submissions.

Restaurants/vendors/food businesses can claim profiles and improve their trust profile.

### MVP scope
Build a **web MVP first**, mobile responsive, modern and premium.

### Tech stack
Use the following unless there is a very strong reason not to:
- Nuxt.js latest stable with App Router on Frontend
- TypeScript
- Tailwind CSS
- Python (FastAPI) on backend with pydantic
- PostgreSQL/ RDS on cloud
- Something free for for authentication
- Uploadthing or S3-compatible file uploads for images
- Zod for validation
- Stripe-ready billing scaffolding, but billing can be mocked in MVP
- Map support optional; if added, use a simple provider-friendly abstraction or free map for proximity
- Terraform for IAC (If freely available)
- Deployment to be done of AWS (Simple EC2 will be fine for free version or EKS if really required)

### Design direction
The UI should feel:
- trustworthy,
- clean,
- modern,
- data-rich,
- minimal but premium,
- more “public trust infrastructure” than “food blogger app”.

Avoid generic food-delivery aesthetics. No loud red/yellow fast-food look. Prefer clean greens, slate, off-white, and subtle amber for caution states.

### Product entities
Design the data model for at least these entities:
- User
- Business
- Location
- Review
- StructuredScore
- EvidenceUpload
- ClaimRequest
- VerificationBadge
- Category
- ReportFlag
- AdminAudit

### User roles
Support these roles:
- guest
- user
- moderator
- business_owner
- admin

### Main features for MVP

#### 1. Home page
- Hero section explaining BiteScore
- Search bar for places/cities/cuisines
- Example trusted places
- Explanation of scoring
- CTA for users and business owners

#### 2. Public business profile page
Each business page should include:
- name, category, location
- type of business (Restaurant, street vendor, etc.)
- overall BiteScore
- score breakdown
- badges like “claimed”, “verified”, “high confidence”, “under review”
- structured review highlights
- uploaded evidence gallery
- recent reviews
- business response section
- report / flag button

#### 3. User review flow
Users can submit a structured review with:
- cleanliness score
- staff hygiene score
- food handling score
- packaging score
- water confidence score
- oil/freshness concern indicator
- free-text notes
- optional photos/evidence
- whether they dined in / takeaway / delivery
- date of visit

Do not make the app review too much about taste. Taste can be optional and secondary.

#### 4. Scoring engine
Create a clear, explainable score system.
Example:
- 30% hygiene/cleanliness
- 20% food handling
- 15% staff hygiene
- 10% packaging
- 10% water safety confidence
- 10% evidence credibility
- 5% consistency / confidence weighting

Show score explanation in UI.

#### 5. Trust layer
Build confidence indicators such as:
- low sample size
- verified evidence
- repeated complaints
- recent improvement trend
- owner claimed profile
- moderation reviewed

#### 6. Business dashboard
For claimed businesses:
- profile edit
- respond to reviews
- upload certifications/documents
- request verification
- see score breakdown and recurring issues
- see trend chart over time

#### 7. Admin and moderation dashboard
- review moderation queue
- flag handling
- business claim approvals
- badge assignment
- suspicious review detection dashboard
- ability to hide abusive content

#### 8. Search and discovery
- search by city, cuisine, trust score, category
- filters like “high trust”, “verified”, “budget”, “healthy options”

#### 9. Authentication
- email/password or magic link
- social login optional

### Seed data
Generate realistic seed data for:
- 30 businesses in 3 cities
- 100 reviews
- several badges and categories
- sample admin and business owner accounts

### Mobile responsiveness
The whole web app must be fully mobile responsive.
Design mobile-first for review submission and browsing. Desktop should be best for dashboards and moderation.

### Pages required
At minimum build:
- /
- /search
- /business/[slug]
- /submit-review/[businessId]
- /dashboard
- /business-dashboard
- /admin
- /about
- /how-it-works

### Important UX rules
- structured reviews over ranting
- evidence encouraged but optional
- all score calculations transparent
- trust and moderation visible
- avoid defamation-prone language in templates
- use neutral wording like “reported concern”, “community observation”, “under review”

### Important legal/UX safeguards
Add these into the product copy and UX:
- Terms of Service page
- Privacy Policy page
- Content Moderation Policy page
- business dispute/report correction flow
- no direct accusation language in templates
- user content warning and consent checkbox before submission
- photo upload consent statement

### SEO
Implement strong SEO:
- metadata
- structured title tags
- business pages indexable
- Open Graph tags
- sitemap

### Deliverables
I want:
1. Full codebase
2. Prisma schema
3. seed script
4. setup instructions
5. env example file
6. polished UI
7. working demo routes with realistic fake data

### Nice-to-have
If time permits:
- map view
- PWA install support
- trend graphs
- verification request workflow
- AI-assisted moderation stub

### Code quality
- production-grade folder structure
- strongly typed
- modular components
- reusable design system
- clean code and comments only where necessary

### Final instruction
Do not create a toy project. Build a serious startup-grade MVP that could be shown to investors or first users.

## Cursor Prompt End

---

# Product definition notes

## What BiteScore should be

BiteScore should be positioned as a **food trust score platform**. That means:
- less subjective than Yelp,
- less lifestyle-oriented than Instagram food pages,
- less job-review-like than Glassdoor,
- more structured and evidence-driven than basic review apps.

## MVP positioning statement

**BiteScore helps people discover food businesses they can trust by combining structured hygiene observations, evidence-backed reviews, and transparent scoring.**

## MVP user groups

Primary:
- health-conscious consumers
- fitness enthusiasts
- travelers
- parents
- people with higher concern for cleanliness and food quality

Secondary:
- restaurant owners
- healthy food brands
- food courts and quality-focused chains

---

# Legal and business checklist

## 1. Trademark checks: where to check

Before committing to BiteScore, check these trademark databases:

| Region | Database | Link | Why it matters |
|---|---|---|---|
| Global | WIPO Global Brand Database | https://www.wipo.int/en/web/global-brand-database | Main international search starting point.[cite:247] |
| US | USPTO | https://www.uspto.gov/trademarks | Critical if product may reach US users or investors.[cite:268] |
| EU | EUIPO eSearch | https://euipo.europa.eu/eSearch/ | Important for EU-wide protection.[cite:258] |
| Germany | DPMA | https://www.dpma.de/english/trade_marks/trade_mark_search/index.html | Important because founder lives in Germany.[cite:249] |
| India | IP India trademark search | https://ipindia.gov.in/ | Important if India is an initial target market. |

WIPO specifically recommends searching before filing, and its Global Brand Database is intended for international trademark searching and monitoring.[cite:247][cite:267][cite:272]

## 2. How to do a practical trademark search

Search these versions of the name:
- BiteScore
- Bite Score
- ByteScore
- BiteScor
- ScoreBite
- Bite Safe Score

Also search by classes related to:
- software,
- SaaS,
- ratings platforms,
- food information,
- consumer apps,
- downloadable mobile apps.

Check not only identical names but also names that sound similar.

## 3. What to check besides trademark

Before launch, check all of these:

### Branding assets
- domain availability: `bitescore.com`, `getbitescore.com`, `bitescore.app`, etc.
- Instagram, X, LinkedIn, TikTok, YouTube handles
- logo similarity to existing food or trust brands
- app store name availability later

### Legal risk checks
- no conflict with existing logos
- no misleading “official certification” language unless actually licensed to use it
- no false implication of government approval
- no defamatory business claims without moderation process
- no scraping violations if using third-party sources later

### Product legal pages
The MVP should include:
- Terms of Service
- Privacy Policy
- Community Guidelines
- Content Moderation / Review Policy
- Business Correction / Appeal Process

## 4. How to register a trademark

This depends on where the company will operate first.

### If starting from Germany / EU
- File first in Germany via DPMA if Germany is the first commercial base.[cite:249]
- Or file at EUIPO for broader EU coverage if the business will operate across the EU.[cite:258]
- Later extend internationally through the Madrid System via WIPO if needed.[cite:259][cite:267]

### If starting in India
- File in India if India is the first real market and commercial launch country.
- But this protects mainly in India, not globally.

### If global from day one
Common route:
1. choose base filing country/region,
2. file there first,
3. then extend internationally using WIPO Madrid System if traction appears.
WIPO explains international trademark systems and search-before-filing workflows as part of the trademark process.[cite:264][cite:267]

## 5. Where should a founder living in Germany register?

This is the practical guidance, not legal advice:

### Best likely approach for this case
If living in Germany and planning a global-first digital product, the most practical early legal base is often:
- **Germany or the EU** for company setup and initial trademark protection,
- then expand protection to India and other markets later if traction justifies cost.

Why:
- the founder already lives in Germany,
- opening banking, tax, company administration, and contracts can be easier locally,
- EU/German registration gives stronger clarity for local operations.

### When India may make sense first
India may be better as a first company jurisdiction if:
- the main team will be in India,
- operations and sales will be India-first,
- local partnerships and compliance in India are central,
- there is a reliable local cofounder/operator there.

### Founder-level recommendation
For a solo founder currently living in Germany, it is usually better to:
- build and validate first,
- then likely register the business in Germany or the EU if operating mostly from there,
- only set up Indian structure later if India becomes a major operating market.

A local lawyer and tax advisor should confirm this before incorporation, especially for cross-border tax and residency issues.

## 6. Build first or register first?

### Best practical approach
For this kind of startup, usually do this:

#### Stage 1: before company registration
- choose working name
- do trademark and domain checks
- build MVP
- create landing page
- validate with users
- collect waitlist

#### Stage 2: before taking payments or signing contracts
- register company
- set up business bank account
- set up terms/privacy properly
- file trademark in primary jurisdiction if committed to the name

#### Stage 3: after validation
- expand legal protection
- register additional trademarks if needed
- register in more countries only if traction exists

### Why this order makes sense
Building an MVP first reduces risk. Filing trademarks, incorporating companies, and paying legal/compliance costs too early can waste money if the product or name changes. Official trademark systems are valuable, but the founder should not skip search and validation first.[cite:247][cite:267][cite:268]

### Exception
If the brand name is extremely important, or there is strong concern about someone else taking it, file earlier once search results look clear.

## 7. Business registration guidance

### Likely early path for a solo founder in Germany
- Start building before formal incorporation if still validating.
- Operate as an individual during pre-revenue MVP phase only if local law and tax rules allow it.
- Incorporate before charging customers, hiring, or signing vendor agreements.

### Questions to resolve with a German advisor
- sole proprietorship vs UG/GmbH,
- VAT obligations,
- invoicing users globally,
- privacy/GDPR obligations,
- platform liability,
- insurance.

## 8. Privacy and platform law issues

For BiteScore, these matter early:
- GDPR, especially if users in the EU submit reviews and photos.
- lawful basis for collecting data.
- right to delete account and data.
- moderation and appeals process.
- handling complaints from businesses.
- safe wording to reduce defamation risk.

Important UX/legal rules:
- Use structured categories, not pure accusations.
- Require users to confirm they are reporting honestly.
- Provide business owners a response and correction path.
- Log moderation actions.

## 9. If using “scores,” be careful

A scoring platform can look authoritative. That is good for trust, but risky if misleading. So:
- show methodology clearly,
- avoid pretending to be a government certifier,
- label BiteScore as community and platform-derived unless verified through an official program,
- distinguish between “community score,” “verified score,” and “under review.”

## 10. Logo and website checks

Before finalizing branding:
- buy domain quickly after choosing name,
- reserve social handles,
- create a simple wordmark first,
- avoid copying shield/check/badge styles too close to competitors,
- ensure favicon and logo are distinct.

## 11. Payments and launch order

Recommended launch order:
1. Landing page with email capture.
2. MVP web app with seeded demo data.
3. Private beta.
4. Legal pages and moderation process.
5. Company registration.
6. Trademark filing in main jurisdiction.
7. Public launch.

---

# Founder action plan

## First 7 days
- Search trademark databases: WIPO, USPTO, EUIPO, DPMA, India.[cite:247][cite:268][cite:258][cite:249]
- Check domains and social handles.
- Decide final name.
- Start MVP in Cursor using the prompt above.

## First 30 days
- Build web MVP.
- Publish landing page.
- Test with 20–50 users.
- Create privacy policy, terms, moderation rules.
- Decide whether BiteScore is still the final brand.

## Before first revenue
- Register company.
- Open bank/payment setup.
- File trademark in primary jurisdiction.
- Consult German tax/legal advisor.

## After validation
- Add mobile app later if usage shows strong mobile behavior.
- Consider trademark expansion to US/India/EU through appropriate offices and WIPO pathways.[cite:259][cite:267]

---

# Final recommendation

Build **web-first** and make it fully mobile responsive. Do **not** start with native mobile unless early users clearly need frequent on-the-go review posting. Search and validate the name before spending on branding, and for a founder living in Germany, the most practical legal path is usually to validate first, then incorporate and protect the brand in Germany or the EU first, expanding later if the product gains traction. Trademark search should begin with WIPO and then the specific core markets through USPTO, EUIPO, DPMA, and India’s trademark system.[cite:247][cite:268][cite:258][cite:249][cite:267]

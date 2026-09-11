import { ServiceItem, CaseStudy, JobOpening } from '../types';

export const servicesData: ServiceItem[] = [
  {
    id: 'web-apps',
    number: '01',
    title: 'Website & Web Application Development',
    sublabel: 'High-Performance Frontend & Reactive Platforms',
    description: 'We architect mission-critical enterprise web applications, real-time collaboration platforms, and customer portals with reactive state management, edge caching, and sub-100ms TTFB.',
    deliverables: [
      'Server Components (RSC) & Edge Compute architectures',
      'Micro-frontend orchestration & module federation',
      'Progressive Web Apps (PWA) with offline resilience',
      'WCAG 2.1 AAA Accessibility & Core Web Vitals optimization'
    ],
    specs: [
      { label: 'Median TTFB', value: '< 65ms' },
      { label: 'Initial JS Bundle', value: '< 110 KB' },
      { label: 'Lighthouse Score', value: '98 - 100' }
    ],
    techStack: ['Next.js 14', 'React 18', 'TypeScript', 'Node.js', 'GraphQL', 'Tailwind CSS', 'WebAssembly'],
    ctaText: 'Scope Web Application'
  },
  {
    id: 'custom-software',
    number: '02',
    title: 'Custom Enterprise Software Solutions',
    sublabel: 'Resilient Backend Engineering & Distributed Systems',
    description: 'Zero-downtime event streaming clusters, hardened backend services, distributed databases, and fault-tolerant transactional backbones designed for massive concurrent enterprise scale.',
    deliverables: [
      'Multi-region event streaming & message brokers',
      'CQRS and event sourcing architectural patterns',
      'ACID-compliant transactional microservices',
      'Zero-downtime legacy database and schema migrations'
    ],
    specs: [
      { label: 'Throughput', value: '10,000+ TPS' },
      { label: 'Availability SLO', value: '99.999%' },
      { label: 'P99 Latency', value: '< 18ms' }
    ],
    techStack: ['Go', 'Rust', 'Python', 'Apache Kafka', 'PostgreSQL', 'Redis', 'gRPC', 'Docker'],
    ctaText: 'Explore Enterprise Architecture'
  },
  {
    id: 'ui-ux-design',
    number: '03',
    title: 'UI/UX & Digital Product Design',
    sublabel: 'Human-Crafted Interfaces & Design Systems',
    description: 'Digital product design created by engineers who understand code and designers who study cognitive ergonomics. We transform intricate workflows into clean, effortless user experiences.',
    deliverables: [
      'Qualitative user research & cognitive flow mapping',
      'Multi-platform tokenized design systems in Figma',
      'Automated design token CI/CD pipelines to code',
      'Multi-state interactive prototypes & usability verification'
    ],
    specs: [
      { label: 'Component Coverage', value: '100% Tokenized' },
      { label: 'Design-to-Code Sync', value: 'Automated CI/CD' },
      { label: 'WCAG Compliance', value: 'Level AAA' }
    ],
    techStack: ['Figma Tokens', 'Storybook', 'Tailwind CSS', 'Radix UI', 'Framer Motion'],
    ctaText: 'Review Design Process'
  },
  {
    id: 'ecommerce',
    number: '04',
    title: 'E-Commerce & Headless Commerce',
    sublabel: 'High-Volume Transactional Retail Systems',
    description: 'Headless commerce engines built for high-throughput flash sales, sub-second checkout pipelines, and international multi-currency fulfillment routing.',
    deliverables: [
      'Headless Shopify Plus & Medusa custom storefronts',
      'Sub-second checkout pipelines with Stripe & Adyen',
      'Bi-directional ERP inventory sync via webhook mesh',
      'Global edge caching for catalog search with Algolia'
    ],
    specs: [
      { label: 'Checkout Time', value: '< 800ms' },
      { label: 'Peak Concurrency', value: '50k users/min' },
      { label: 'Cart Conversion Uplift', value: '+34% avg' }
    ],
    techStack: ['Shopify Plus', 'Medusa', 'Stripe API', 'Next.js Commerce', 'Algolia', 'Redis'],
    ctaText: 'Configure Commerce Architecture'
  },
  {
    id: 'business-automation',
    number: '05',
    title: 'Business Automation & Workflow Engineering',
    sublabel: 'Internal Tools & Operational Acceleration',
    description: 'Eliminating operational overhead and manual bottlenecks through idempotent background queues, automated document parsing pipelines, and unified bi-directional CRM/ERP integrations.',
    deliverables: [
      'Custom administrative control planes & portals',
      'Idempotent webhook ingestion buses & queue workers',
      'Asynchronous ETL data pipelines & compliance audits',
      'Human-in-the-loop operational validation dashboards'
    ],
    specs: [
      { label: 'Manual Work Cut', value: '65% - 85%' },
      { label: 'Pipeline Reliability', value: '99.98%' },
      { label: 'Execution Speed', value: '12x faster' }
    ],
    techStack: ['Python', 'FastAPI', 'Temporal', 'Apache Airflow', 'PostgreSQL', 'OpenAI API'],
    ctaText: 'Automate Workflows'
  },
  {
    id: 'cloud-devops',
    number: '06',
    title: 'Cloud Architecture & Infrastructure (DevOps)',
    sublabel: 'Scalable Cloud Foundations & Zero-Trust Security',
    description: 'Immutable cloud infrastructure managed as code. We design resilient multi-cloud environments, automated ephemeral review environments, and military-grade CI/CD pipelines.',
    deliverables: [
      'Terraform & OpenTofu Infrastructure as Code modules',
      'Multi-tenant Kubernetes clusters with ArgoCD GitOps',
      'Automated preview environments generated per PR',
      'SOC2 and ISO 27001 baseline security compliance'
    ],
    specs: [
      { label: 'Deployment Frequency', value: 'Multiple/day' },
      { label: 'Recovery Time (MTTR)', value: '< 5 mins' },
      { label: 'Infrastructure Code', value: '100% IaC' }
    ],
    techStack: ['AWS', 'Google Cloud', 'Terraform', 'Kubernetes', 'ArgoCD', 'Datadog', 'GitHub Actions'],
    ctaText: 'Audit Cloud Infrastructure'
  },
  {
    id: 'maintenance-support',
    number: '07',
    title: 'Maintenance, Support & 24/7 SLAs',
    sublabel: 'Mission-Critical Reliability & Continuous Telemetry',
    description: 'Dedicated site reliability engineering and guaranteed enterprise SLAs to ensure zero surprise outages, instant security patch deployment, and long-term codebase vitality.',
    deliverables: [
      'Guaranteed 15-minute emergency response SLA',
      'Synthetic uptime probing & distributed tracing',
      'Automated CVE dependency scanning & patching',
      'Quarterly architectural audits & refactoring roadmaps'
    ],
    specs: [
      { label: 'Emergency SLA', value: '15 mins' },
      { label: 'Uptime Guarantee', value: '99.99%' },
      { label: 'Coverage', value: '24/7/365' }
    ],
    techStack: ['Datadog', 'Prometheus', 'Grafana', 'Sentry', 'PagerDuty', 'CloudWatch'],
    ctaText: 'View SLA Tiers'
  }
];

export const caseStudiesData: CaseStudy[] = [
  {
    id: 'paygrid-global',
    number: '01',
    client: 'PayGrid Global Inc.',
    industry: 'FinTech & Banking Infrastructure',
    title: 'Modernizing a High-Throughput Global Payment Gateway',
    tagline: 'Re-architecting legacy monolithic transaction settlement into an ultra-low latency event-driven Go and Kafka infrastructure.',
    challenge: 'PayGrid’s monolithic PHP backend was experiencing 4.2-second latency spikes during European market opening hours, causing settlement drops and failing enterprise banking compliance audits under $400M+ monthly volume.',
    solution: 'Azyntrix engineered an event-driven Go microservices architecture paired with Apache Kafka for immutable transaction logging, zero-downtime database replication, and edge-routed Next.js merchant dashboards.',
    architecture: {
      legacy: 'Monolithic PHP / MySQL backend → Single-region RDS bottleneck → Synchronous blocking calls → 4.2s latency spikes.',
      modern: 'Event-driven Go microservices → Multi-region Kafka cluster → CQRS event sourcing with Redis cache → 74ms P99 latency.'
    },
    metrics: [
      { label: 'Peak Uptime', value: '99.999%', detail: 'Zero unannounced downtime in 18 months' },
      { label: 'P99 TTFB', value: '74ms', detail: 'Down from 4,200ms legacy baseline' },
      { label: 'Volume Handled', value: '$420M / mo', detail: 'Seamless processing of 8.5M transactions' }
    ],
    technologies: ['Go', 'Apache Kafka', 'Next.js 14', 'PostgreSQL', 'AWS', 'Docker', 'Redis'],
    testimonial: {
      quote: 'Azyntrix delivered our core settlement pipeline two months ahead of schedule. We processed over $420M last month without a single dropped packet or compliance flag.',
      author: 'Marcus Vance',
      role: 'VP of Engineering',
      company: 'PayGrid Global Inc.'
    }
  },
  {
    id: 'carepoint-health',
    number: '02',
    client: 'CarePoint Telehealth Systems',
    industry: 'Healthcare & Clinical Operations',
    title: 'HIPAA-Compliant Real-Time Clinical Telemetry & Patient Portal',
    tagline: 'Building a zero-trust telehealth portal and live patient telemetry routing network across 140+ medical centers.',
    challenge: 'CarePoint required a unified web platform to securely stream real-time ICU vital telemetry from disparate hardware monitors to centralized physician portals with zero data leakage and strict HIPAA compliance.',
    solution: 'We engineered a zero-trust WebRTC and WebSockets pipeline in FastAPI and React with end-to-end encrypted telemetry channels, automated audit logs, and sub-100ms vital sign updates.',
    architecture: {
      legacy: 'Fragmented on-premise servers → Unstandardized CSV polling → 15-minute manual sync lag → Inefficient doctor queueing.',
      modern: 'End-to-end encrypted WebSockets → Distributed FastAPI microservices → Real-time doctor queue dispatch → Sub-second alerts.'
    },
    metrics: [
      { label: 'Intake Wait Time', value: '-48%', detail: 'Average triage reduced from 22 to 11 minutes' },
      { label: 'Active Patients', value: '1.4M+', detail: 'Synchronized across 140 regional facilities' },
      { label: 'Security Breaches', value: '0', detail: '100% HIPAA & SOC2 Type II audit compliance' }
    ],
    technologies: ['React', 'Python', 'FastAPI', 'Docker', 'Google Cloud', 'PostgreSQL', 'WebSockets'],
    testimonial: {
      quote: 'The architectural clarity and security rigor Azyntrix brought to our clinical systems gave our hospital board total confidence.',
      author: 'Dr. Elena Rostova',
      role: 'Chief Medical Technology Officer',
      company: 'CarePoint Health'
    }
  },
  {
    id: 'auracommerce',
    number: '03',
    client: 'Aura Commerce Brands',
    industry: 'E-Commerce & Global Retail',
    title: 'Headless Global Commerce Engine for High-Velocity Flash Sales',
    tagline: 'Replacing a slow legacy Magento store with a sub-second headless Next.js 14 and Shopify Plus commerce pipeline.',
    challenge: 'Aura’s legacy storefront frequently crashed during Black Friday flash sales with 45,000 concurrent shoppers, resulting in lost revenue and high bounce rates.',
    solution: 'Designed an ultra-fast headless Next.js 14 architecture with Edge caching, custom Stripe checkout integration, and automated Algolia search indexing.',
    architecture: {
      legacy: 'Monolithic Magento on single EC2 → Uncached database queries → 3.8s page load → Cart abandonment at checkout.',
      modern: 'Next.js 14 on Vercel Edge → Headless Shopify Plus API → Algolia instant search → 380ms TTFB worldwide.'
    },
    metrics: [
      { label: 'Checkout Speed', value: '380ms', detail: '4.2x faster than previous store' },
      { label: 'Conversion Uplift', value: '+38%', detail: 'Direct $3.2M increase during holiday quarter' },
      { label: 'Crash Rate', value: '0.00%', detail: 'Handled 62k concurrent users effortlessly' }
    ],
    technologies: ['Next.js 14', 'Shopify Plus', 'Stripe API', 'Tailwind CSS', 'Algolia', 'Redis'],
    testimonial: {
      quote: 'Our store was lightning-fast during our biggest product drop in company history. Zero crashes, instantaneous search, and record revenue.',
      author: 'Julian Thorne',
      role: 'Head of Digital Experience',
      company: 'Aura Brands'
    }
  }
];

export const openPositionsData: JobOpening[] = [
  {
    id: 'senior-fullstack-web-architect',
    title: 'Senior Full-Stack Web Architect',
    department: 'Frontend',
    level: 'Staff',
    location: 'Worldwide Remote',
    type: 'Full-Time',
    salary: '$140,000 – $180,000 USD / Year + Profit Share',
    overview: 'Lead the frontend architecture of mission-critical Next.js 14 micro-frontends, edge caching, and scalable APIs for global enterprise clients with asynchronous autonomy.',
    responsibilities: [
      'Architect and scale distributed Next.js 14+ / React enterprise web applications with sub-100ms TTFB.',
      'Direct micro-frontend orchestration, streaming SSR, and edge compute caching strategies across AWS & Cloudflare Workers.',
      'Drive strict TypeScript conventions, automated end-to-end testing, and zero-compromise code review standards.',
      'Partner directly with client VP of Engineering leads to translate business requirements into RFC blueprints.',
      'Instrument comprehensive real-time telemetry (Datadog, Core Web Vitals) ensuring 99.99% availability.',
      'Mentor staff and senior engineers through asynchronous PR teardowns and architectural workshops.'
    ],
    requirements: [
      '7+ years building enterprise web apps with deep React, Next.js (App Router, Server Components), and TypeScript mastery.',
      'Solid experience designing Node.js / Go microservices, GraphQL APIs, and event-driven data streaming.',
      'Master of modern frontend performance: Core Web Vitals (LCP, INP, CLS), code-splitting, bundle profiling, WebAssembly.',
      'Proven track record deploying on AWS, Vercel Enterprise, Kubernetes, and Docker CI/CD pipelines.'
    ],
    bonusSkills: [
      'Production experience with Rust and WebAssembly compilation.',
      'Experience with Apache Kafka, NATS, or temporal workflow orchestration.',
      'Author or core contributor of recognized open-source libraries or design systems.'
    ],
    perks: [
      'Top-tier global compensation without geo-discounting',
      '$3,500 direct home office setup grant',
      '$4,000 annual continuous learning & conference budget',
      'Flexible 4-day focus week options & true async workflow',
      'Unlimited PTO with mandatory 25-day minimum',
      'Top-spec M3 Max MacBook Pro / Linux workstation refresh every 2 years'
    ],
    techStack: ['Next.js 14', 'TypeScript', 'React', 'Node.js', 'GraphQL', 'AWS', 'Docker', 'Tailwind CSS']
  },
  {
    id: 'lead-distributed-systems-engineer',
    title: 'Lead Distributed Systems Engineer',
    department: 'Backend',
    level: 'Principal',
    location: 'Worldwide Remote',
    type: 'Full-Time',
    salary: '$160,000 – $210,000 USD / Year + Profit Share',
    overview: 'Design and build resilient, event-driven distributed backends handling 10,000+ transactions per second with Go, Rust, Apache Kafka, and Kubernetes.',
    responsibilities: [
      'Architect fault-tolerant microservices and high-throughput data pipelines with Go and Rust.',
      'Design event streaming architectures using Apache Kafka and CQRS/Event Sourcing patterns.',
      'Optimize database queries and schema designs across PostgreSQL and distributed key-value stores.',
      'Lead technical RFC processes and system design reviews for mission-critical client deployments.'
    ],
    requirements: [
      '8+ years backend engineering experience with 5+ years in Go or Rust.',
      'Deep expertise in distributed systems fundamentals (consensus, partitioning, eventual consistency).',
      'Hands-on mastery of Apache Kafka, PostgreSQL internals, and gRPC/Protobuf.',
      'Experience running containerized workloads on Kubernetes in production.'
    ],
    bonusSkills: [
      'Experience with high-frequency trading or payment gateway infrastructure.',
      'Contributions to open-source distributed systems projects.'
    ],
    perks: [
      'Top of market global salary',
      '$3,500 home office grant',
      '$4,000 annual learning budget',
      'Full health, dental, and vision coverage',
      'Bi-annual global team retreats (Bali, Zurich, Tokyo)'
    ],
    techStack: ['Go', 'Rust', 'Apache Kafka', 'PostgreSQL', 'gRPC', 'Kubernetes', 'Docker', 'AWS']
  },
  {
    id: 'staff-cloud-devops-engineer',
    title: 'Staff Cloud Infrastructure & DevOps Engineer',
    department: 'Cloud & DevOps',
    level: 'Staff',
    location: 'Worldwide Remote',
    type: 'Full-Time',
    salary: '$150,000 – $190,000 USD / Year + Profit Share',
    overview: 'Own and evolve automated Infrastructure as Code (Terraform), Kubernetes cluster orchestration, and zero-trust security postures for multi-cloud enterprise deployments.',
    responsibilities: [
      'Author reusable, modular Terraform and OpenTofu infrastructure modules across AWS and GCP.',
      'Design zero-downtime blue/green deployment pipelines with ArgoCD and GitHub Actions.',
      'Enforce SOC2 and ISO 27001 compliance policies and automated security vulnerability gates.',
      'Build observability pipelines and automated alerting with Datadog and Prometheus.'
    ],
    requirements: [
      '6+ years in SRE/DevOps with deep AWS/GCP and Kubernetes mastery.',
      'Advanced Terraform Infrastructure as Code production expertise.',
      'Solid programming skills in Python or Go for infrastructure automation.',
      'Experience managing multi-region high-availability systems.'
    ],
    bonusSkills: [
      'Experience with service meshes (Istio, Linkerd).',
      'Certified Kubernetes Administrator (CKA).'
    ],
    perks: [
      'Global equal pay policy',
      '$3,500 workstation grant',
      'Flexible working hours & async culture',
      'Comprehensive wellness benefits'
    ],
    techStack: ['AWS', 'Google Cloud', 'Terraform', 'Kubernetes', 'ArgoCD', 'Datadog', 'GitHub Actions']
  },
  {
    id: 'senior-ui-ux-product-designer',
    title: 'Senior UI/UX Product Designer & Systems Lead',
    department: 'Product & Design',
    level: 'Senior',
    location: 'Worldwide Remote',
    type: 'Full-Time',
    salary: '$120,000 – $160,000 USD / Year + Profit Share',
    overview: 'Craft elegant, human-centered digital product interfaces, complex SaaS workflows, and scalable design token systems in close partnership with senior engineers.',
    responsibilities: [
      'Design intuitive, cognitive-friendly interfaces for complex data workflows and enterprise systems.',
      'Build and maintain multi-variant design systems in Figma with automated design token exports.',
      'Conduct qualitative user testing and translate insights into iterative prototype improvements.',
      'Collaborate with frontend architects in Storybook to guarantee pixel-perfect code fidelity.'
    ],
    requirements: [
      '5+ years in digital product and UI/UX design for web applications.',
      'Deep mastery of Figma, design systems, autolayout, and design tokens.',
      'Strong understanding of web technologies (HTML/CSS, React, accessibility WCAG 2.1 AA).',
      'Exceptional portfolio showing complex problem solving and refined editorial craft.'
    ],
    bonusSkills: [
      'Ability to write clean CSS / Tailwind code.',
      'Experience conducting enterprise customer interviews.'
    ],
    perks: [
      'Top-tier global compensation',
      '$3,500 home studio setup allowance',
      '$4,000 annual learning stipend',
      'Unlimited flexible vacation policy'
    ],
    techStack: ['Figma', 'Tokens Studio', 'Storybook', 'HTML/CSS', 'Tailwind', 'Whimsical']
  }
];

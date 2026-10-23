import { JobModel } from '../models/Job.mjs';
import { CaseStudyModel } from '../models/CaseStudy.mjs';

export const initialJobs = [
  {
    id: 'senior-fullstack-web-architect',
    title: 'Senior Full-Stack Web Architect',
    department: 'Frontend',
    location: 'Remote (Worldwide / UTC-8 to UTC+4)',
    type: 'Full-Time / Guild Core',
    experience: '6+ Years',
    salaryRange: '$160,000 – $210,000 USD + Token Equity',
    description: 'Lead the architecture and delivery of mission-critical React/Next.js and distributed web platforms for Tier-1 fintech and healthcare clients. Own end-to-end technical blueprints, performance budgets (<80ms TTFB), and client engineering alignment.',
    responsibilities: [
      'Architect robust web applications with Next.js 14, React Server Components, and Tailwind Design Systems.',
      'Lead technical discovery sessions and write comprehensive Architecture Decision Records (ADRs).',
      'Optimize Web Vitals, CDN edge caching, hydration latency, and browser rendering pipelines.',
      'Mentor senior engineers in asynchronous code reviews and rigorous TypeScript type systems.',
      'Interface directly with client CTOs and engineering directors during sprint milestones.'
    ],
    requirements: [
      '6+ years of production experience shipping complex web applications at scale.',
      'Deep mastery of TypeScript, modern React, Next.js, Node.js, and browser performance APIs.',
      'Demonstrated experience with state management, WebSockets/SSE, and distributed caching.',
      'Strong portfolio or open-source track record showcasing clean architecture and UX craft.',
      'Excellent written asynchronous communication skills.'
    ],
    techStack: ['TypeScript', 'Next.js 14', 'React', 'Node.js', 'Tailwind CSS', 'PostgreSQL', 'Redis', 'Docker'],
    isActive: true,
    applicantCount: 14
  },
  {
    id: 'lead-backend-distributed-systems-engineer',
    title: 'Lead Backend & Distributed Systems Engineer',
    department: 'Backend',
    location: 'Remote (Worldwide)',
    type: 'Full-Time / Guild Core',
    experience: '7+ Years',
    salaryRange: '$175,000 – $230,000 USD + Token Equity',
    description: 'Design and deploy fault-tolerant, high-throughput microservices, event meshes, and database architectures capable of sub-5ms transaction settlement and 99.999% uptime SLAs.',
    responsibilities: [
      'Engineer distributed APIs, event-driven pipelines (Kafka / RabbitMQ), and transactional engines.',
      'Design PostgreSQL/MongoDB schemas with high concurrency and zero-downtime migration strategies.',
      'Implement multi-region failover, circuit breakers, and rate-limiting mesh layers.',
      'Perform security audits, SOC2 Type II compliance reviews, and penetration vulnerability testing.'
    ],
    requirements: [
      '7+ years designing distributed backend services in Go, Node.js, or Rust.',
      'Extensive experience with PostgreSQL, MongoDB, Redis, and distributed consensus.',
      'Deep understanding of ACID guarantees, partition tolerance, and load balancing algorithms.',
      'Experience in financial ledger systems or real-time telemetry processing is a strong plus.'
    ],
    techStack: ['Node.js', 'Go', 'PostgreSQL', 'MongoDB', 'Redis', 'Kafka', 'Docker', 'Kubernetes'],
    isActive: true,
    applicantCount: 22
  },
  {
    id: 'principal-cloud-infrastructure-sre',
    title: 'Principal Cloud Infrastructure & SRE',
    department: 'Cloud & DevOps',
    location: 'Remote (Worldwide)',
    type: 'Full-Time / Guild Core',
    experience: '8+ Years',
    salaryRange: '$180,000 – $240,000 USD + Token Equity',
    description: 'Own our multi-cloud infrastructure blueprints across AWS, GCP, and Edge networks. Automate zero-trust Kubernetes deployments, telemetry dashboards, and incident response runbooks.',
    responsibilities: [
      'Manage multi-tenant Kubernetes clusters, Terraform IaC modules, and GitOps pipelines.',
      'Establish real-time observability stacks (Prometheus, Grafana, OpenTelemetry, Datadog).',
      'Optimize cloud compute expenditures, autoscaling triggers, and spot instance topologies.',
      'Conduct chaos engineering simulations and ensure enterprise 99.999% SLA guarantees.'
    ],
    requirements: [
      '8+ years in cloud infrastructure, site reliability engineering, and production DevOps.',
      'Mastery of Terraform, Kubernetes, AWS/GCP, Docker, and CI/CD automation.',
      'Strong scripting background in Python, Bash, or Go.',
      'Proven incident management and disaster recovery experience.'
    ],
    techStack: ['Terraform', 'Kubernetes', 'AWS', 'GCP', 'OpenTelemetry', 'Prometheus', 'ArgoCD', 'Cloudflare Edge'],
    isActive: true,
    applicantCount: 9
  },
  {
    id: 'staff-product-designer-design-systems',
    title: 'Staff Product Designer (Design Systems & Web UI)',
    department: 'Product & Design',
    location: 'Remote (Europe / Americas)',
    type: 'Full-Time / Guild Core',
    experience: '6+ Years',
    salaryRange: '$150,000 – $195,000 USD + Token Equity',
    description: 'Craft high-fidelity, editorial digital design systems and web application interfaces. Bridge the gap between bespoke visual craft, tokenized design systems, and production frontend code.',
    responsibilities: [
      'Lead UI/UX design from conceptual wireframing to high-fidelity interactive prototypes.',
      'Build and maintain scalable design systems with strict typographic scales and tokens in Figma.',
      'Collaborate closely with frontend architects to ensure pixel-perfect CSS/component parity.',
      'Conduct user research sessions and translate complex data workflows into intuitive interfaces.'
    ],
    requirements: [
      '6+ years designing SaaS, FinTech, or digital agency client platforms.',
      'World-class portfolio demonstrating editorial design sense, layout craft, and micro-interactions.',
      'Deep fluency in Figma variables, auto-layout, prototyping, and design token handoff.',
      'Strong understanding of HTML/CSS capabilities, CSS Grid, and responsive ergonomics.'
    ],
    techStack: ['Figma', 'Design Tokens', 'Tailwind CSS', 'Storybook', 'Protopie', 'User Testing'],
    isActive: true,
    applicantCount: 31
  }
];

export const initialCaseStudies = [
  {
    id: 'paygrid-global',
    client: 'PayGrid Global Inc.',
    title: 'Real-Time Global Settlement & Multi-Currency Treasury Mesh',
    tagline: 'High-throughput cross-border financial reconciliation engine processing $420M+ monthly.',
    category: 'Financial Infrastructure',
    impact: '$420M/mo Processed',
    summary: 'PayGrid required a modernized distributed settlement platform to replace legacy monolithic batch processing with real-time multi-currency settlement and instant compliance verification.',
    architecture: {
      frontend: 'React 18 Micro-Frontend Architecture with Tailwind Design System',
      backend: 'Distributed Node.js & Go Event Mesh with gRPC Inter-Service Communication',
      database: 'MongoDB Sharded Cluster with TimescaleDB Financial Ledger',
      infra: 'Multi-Region AWS EKS with ArgoCD GitOps & Cloudflare Global Edge',
      realtime: 'Apache Kafka Event Streams with sub-15ms reconciliation latency'
    },
    metrics: [
      { label: 'Monthly Settlement Volume', value: '$420M+', subtext: '99.999% ledger accuracy' },
      { label: 'End-to-End Latency', value: '< 18ms', subtext: 'Across 42 fiat currency pairs' },
      { label: 'System Uptime SLA', value: '99.999%', subtext: 'Zero unplanned downtime across 18 mo' }
    ],
    featured: true
  },
  {
    id: 'carepoint-health',
    client: 'CarePoint Telehealth Systems',
    title: 'HIPAA-Compliant Remote Diagnostics & Clinical Consultation Suite',
    tagline: 'Encrypted clinical consultation platform serving 250,000+ active patient consultations.',
    category: 'Healthcare & SaaS',
    impact: '250K+ Patients Served',
    summary: 'CarePoint contracted Azyntrix to architect a zero-latency clinical triage and video diagnostic platform with automated EHR syncing and SOC2 Type II bilateral data segregation.',
    architecture: {
      frontend: 'Next.js 14 with WebRTC Video Mesh and Accessible UI Framework',
      backend: 'Node.js Microservices with End-to-End Field Level Encryption',
      database: 'MongoDB with CSFLE (Client-Side Field Level Encryption)',
      infra: 'HIPAA-Compliant AWS Fargate Cluster with Encrypted Storage Vaults',
      realtime: 'WebSocket Clinical Telemetry with Real-Time Vital Stream Sync'
    },
    metrics: [
      { label: 'Patient Wait-Time Reduction', value: '-48%', subtext: 'From 24 min to under 12 min' },
      { label: 'Active Clinical Providers', value: '4,200+', subtext: 'Licensed doctors across 38 states' },
      { label: 'Compliance Audit Score', value: '100%', subtext: 'Zero findings on SOC2 Type II audit' }
    ],
    featured: true
  },
  {
    id: 'aura-commerce',
    client: 'Aura Luxury Global',
    title: 'Headless Global Commerce Engine & Omnichannel Inventory Fabric',
    tagline: 'Sub-350ms checkout experience powering 12 luxury lifestyle brands globally.',
    category: 'Enterprise E-Commerce',
    impact: '+64% Checkout Conversion',
    summary: 'Re-engineered legacy monolithic storefronts into a unified headless commerce platform with real-time inventory synchronization across 84 worldwide physical boutiques.',
    architecture: {
      frontend: 'Next.js Edge Storefront with Incremental Static Regeneration',
      backend: 'Node.js & GraphQL Gateway with Automated Inventory Orchestration',
      database: 'MongoDB Atlas with Redis Multi-Region Cache Cluster',
      infra: 'Vercel Enterprise with Global Anycast Edge Routing',
      realtime: 'Stripe Global Webhooks with Instant Fraud Scoring Mesh'
    },
    metrics: [
      { label: 'Average TTFB Globally', value: '62ms', subtext: 'Measured via real user monitoring' },
      { label: 'Checkout Conversion Lift', value: '+64%', subtext: 'Post-launch 90-day comparison' },
      { label: 'Peak Black Friday Load', value: '48,000 req/s', subtext: 'Zero degradation or rate spikes' }
    ],
    featured: true
  }
];

export async function seedDatabase() {
  try {
    const jobCount = await JobModel.countDocuments();
    if (jobCount === 0) {
      console.log('[Azyntrix Seeder] Seeding initial job positions into MongoDB...');
      await JobModel.insertMany(initialJobs);
      console.log(`[Azyntrix Seeder] ✅ Seeded ${initialJobs.length} open job positions.`);
    }

    const caseCount = await CaseStudyModel.countDocuments();
    if (caseCount === 0) {
      console.log('[Azyntrix Seeder] Seeding initial case studies into MongoDB...');
      await CaseStudyModel.insertMany(initialCaseStudies);
      console.log(`[Azyntrix Seeder] ✅ Seeded ${initialCaseStudies.length} case studies.`);
    }
  } catch (error) {
    console.warn(`[Azyntrix Seeder] Seed note: ${error.message}`);
  }
}

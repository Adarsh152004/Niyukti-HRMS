export interface ServiceItem {
  id: string;
  number: string;
  title: string;
  sublabel: string;
  description: string;
  deliverables: string[];
  specs: {
    label: string;
    value: string;
  }[];
  techStack: string[];
  ctaText: string;
}

export interface CaseStudy {
  id: string;
  number: string;
  client: string;
  industry: string;
  title: string;
  tagline: string;
  challenge: string;
  solution: string;
  architecture: {
    legacy: string;
    modern: string;
  };
  metrics: {
    label: string;
    value: string;
    detail: string;
  }[];
  technologies: string[];
  testimonial?: {
    quote: string;
    author: string;
    role: string;
    company: string;
  };
}

export interface JobOpening {
  id: string;
  title: string;
  department: 'Frontend' | 'Backend' | 'Cloud & DevOps' | 'Product & Design' | 'Data & AI';
  level: 'Senior' | 'Staff' | 'Lead' | 'Principal';
  location: string;
  type: 'Full-Time' | 'Contract';
  salary: string;
  overview: string;
  responsibilities: string[];
  requirements: string[];
  bonusSkills: string[];
  perks: string[];
  techStack: string[];
}

export interface CandidateApplication {
  fullName: string;
  email: string;
  phone: string;
  location: string;
  linkedin: string;
  github: string;
  yearsOfExperience: string;
  currentRole: string;
  selectedSkills: string[];
  coverLetter: string;
  resumeFileName?: string;
  resumeFileSize?: string;
  consentAgreed: boolean;
}

export interface ClientInquiry {
  fullName: string;
  email: string;
  company: string;
  phone?: string;
  services: string[];
  budget: string;
  timeline: string;
  description: string;
  fileName?: string;
  communicationChannel: 'slack' | 'email' | 'meet';
}

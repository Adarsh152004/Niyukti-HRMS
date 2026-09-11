import mongoose from 'mongoose';

const caseStudySchema = new mongoose.Schema({
  id: {
    type: String,
    required: true,
    unique: true,
  },
  client: {
    type: String,
    required: true,
  },
  title: {
    type: String,
    required: true,
  },
  tagline: {
    type: String,
    required: true,
  },
  category: {
    type: String,
    required: true,
  },
  impact: {
    type: String,
    required: true,
  },
  summary: {
    type: String,
    required: true,
  },
  architecture: {
    frontend: String,
    backend: String,
    database: String,
    infra: String,
    realtime: String,
  },
  metrics: [{
    label: String,
    value: String,
    subtext: String,
  }],
  featured: {
    type: Boolean,
    default: false,
  },
}, {
  timestamps: true,
});

export const CaseStudyModel = mongoose.models.CaseStudy || mongoose.model('CaseStudy', caseStudySchema);

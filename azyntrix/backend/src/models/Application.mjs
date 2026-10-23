import mongoose from 'mongoose';

const applicationSchema = new mongoose.Schema({
  referenceId: {
    type: String,
    required: true,
    unique: true,
    index: true,
  },
  jobId: {
    type: String,
    required: true,
    index: true,
  },
  jobTitle: {
    type: String,
    required: true,
  },
  fullName: {
    type: String,
    required: true,
    trim: true,
  },
  email: {
    type: String,
    required: true,
    trim: true,
    lowercase: true,
    index: true,
  },
  phone: {
    type: String,
    trim: true,
  },
  location: {
    type: String,
    required: true,
  },
  linkedin: {
    type: String,
    trim: true,
  },
  github: {
    type: String,
    required: true,
    trim: true,
  },
  yearsOfExperience: {
    type: String,
    required: true,
  },
  currentRole: {
    type: String,
    trim: true,
  },
  selectedSkills: [{
    type: String,
  }],
  coverLetter: {
    type: String,
  },
  resumeFileName: {
    type: String,
  },
  resumeFileSize: {
    type: String,
  },
  resumeFilePath: {
    type: String,
  },
  consentAgreed: {
    type: Boolean,
    required: true,
    default: true,
  },
  status: {
    type: String,
    enum: ['submitted', 'screening', 'interview_scheduled', 'offered', 'rejected'],
    default: 'submitted',
  },
  reviewerNotes: [{
    author: String,
    note: String,
    createdAt: { type: Date, default: Date.now },
  }],
}, {
  timestamps: true,
});

export const ApplicationModel = mongoose.models.Application || mongoose.model('Application', applicationSchema);

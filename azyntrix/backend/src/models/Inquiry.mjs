import mongoose from 'mongoose';

const inquirySchema = new mongoose.Schema({
  referenceId: {
    type: String,
    required: true,
    unique: true,
    index: true,
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
  },
  company: {
    type: String,
    required: true,
    trim: true,
  },
  role: {
    type: String,
    trim: true,
  },
  projectType: {
    type: String,
    required: true,
  },
  budgetTier: {
    type: String,
    required: true,
  },
  timeline: {
    type: String,
    required: true,
  },
  projectSummary: {
    type: String,
    required: true,
  },
  slackConnect: {
    type: Boolean,
    default: false,
  },
  status: {
    type: String,
    enum: ['pending_review', 'under_scoping', 'proposal_sent', 'active_client', 'archived'],
    default: 'pending_review',
  },
  ndaSigned: {
    type: Boolean,
    default: true,
  },
}, {
  timestamps: true,
});

export const InquiryModel = mongoose.models.Inquiry || mongoose.model('Inquiry', inquirySchema);

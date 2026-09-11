import mongoose from 'mongoose';

const jobSchema = new mongoose.Schema({
  id: {
    type: String,
    required: true,
    unique: true,
    trim: true,
  },
  title: {
    type: String,
    required: true,
    trim: true,
  },
  department: {
    type: String,
    required: true,
    enum: [
      'Frontend',
      'Backend',
      'Full Stack',
      'Cloud & DevOps',
      'Data & AI',
      'Mobile',
      'Security',
      'QA & Testing',
      'Product & Design',
      'Engineering Leadership',
      'Management',
      'Sales & Marketing',
      'Operations',
      'HR & People',
    ],
  },
  location: {
    type: String,
    required: true,
    default: 'Remote (Worldwide)',
  },
  type: {
    type: String,
    required: true,
    default: 'Full-Time / Guild Core',
  },
  experience: {
    type: String,
    required: true,
  },
  salaryRange: {
    type: String,
    required: true,
  },
  description: {
    type: String,
    required: true,
  },
  responsibilities: [{
    type: String,
  }],
  requirements: [{
    type: String,
  }],
  techStack: [{
    type: String,
  }],
  isActive: {
    type: Boolean,
    default: true,
  },
  applicantCount: {
    type: Number,
    default: 0,
  }
}, {
  timestamps: true,
});

export const JobModel = mongoose.models.Job || mongoose.model('Job', jobSchema);

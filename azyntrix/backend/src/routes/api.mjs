import express from 'express';
import multer from 'multer';
import path from 'path';
import fs from 'fs';
import { getJobs, getJobById } from '../controllers/jobController.mjs';
import { submitApplication, getApplications, getApplicationByRef } from '../controllers/applicationController.mjs';
import { submitInquiry, getInquiries } from '../controllers/inquiryController.mjs';
import { getStatus } from '../controllers/statusController.mjs';

const router = express.Router();

// Configure Multer storage for candidate CV uploads
const uploadDir = path.resolve('uploads');
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir, { recursive: true });
}

const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, 'cv-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({
  storage,
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB limit
});

// Telemetry & Health
router.get('/health', getStatus);
router.get('/status', getStatus);

// Careers & Job Openings
router.get('/jobs', getJobs);
router.get('/jobs/:jobId', getJobById);

// Candidate Applications
router.post('/applications', upload.single('resume'), submitApplication);
router.get('/applications', getApplications);
router.get('/applications/:referenceId', getApplicationByRef);

// Project Discovery Inquiries
router.post('/inquiries', submitInquiry);
router.get('/inquiries', getInquiries);

export default router;

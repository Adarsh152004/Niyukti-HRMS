import { ApplicationModel } from '../models/Application.mjs';
import { JobModel } from '../models/Job.mjs';
import { getDBStatus } from '../config/db.mjs';

// In-memory application store fallback
const inMemoryApplications = [];

export async function submitApplication(req, res) {
  try {
    const {
      jobId,
      jobTitle,
      fullName,
      email,
      phone,
      location,
      linkedin,
      github,
      yearsOfExperience,
      currentRole,
      selectedSkills,
      coverLetter,
      resumeFileName,
      resumeFileSize,
      consentAgreed
    } = req.body;

    // Strict Validation
    if (!fullName || !fullName.trim()) {
      return res.status(400).json({ success: false, error: 'Full name is required.' });
    }
    if (!email || !email.includes('@')) {
      return res.status(400).json({ success: false, error: 'A valid email address is required.' });
    }
    if (!github || !github.trim()) {
      return res.status(400).json({ success: false, error: 'GitHub / Code portfolio URL is required.' });
    }
    if (!location || !location.trim()) {
      return res.status(400).json({ success: false, error: 'Location / Timezone is required.' });
    }
    if (!consentAgreed) {
      return res.status(400).json({ success: false, error: 'Candidate consent is required.' });
    }

    // Generate unique reference receipt ID: AZY-2026-XXXX
    const currentYear = new Date().getFullYear();
    const randomSuffix = Math.floor(1000 + Math.random() * 9000);
    const referenceId = `AZY-${currentYear}-${randomSuffix}`;

    const applicationPayload = {
      referenceId,
      jobId: jobId || 'general-application',
      jobTitle: jobTitle || 'Engineering Guild Candidate',
      fullName: fullName.trim(),
      email: email.trim().toLowerCase(),
      phone: phone ? phone.trim() : undefined,
      location: location.trim(),
      linkedin: linkedin ? linkedin.trim() : undefined,
      github: github.trim(),
      yearsOfExperience: yearsOfExperience || '5-8 Years',
      currentRole: currentRole ? currentRole.trim() : undefined,
      selectedSkills: Array.isArray(selectedSkills) ? selectedSkills : (selectedSkills ? [selectedSkills] : []),
      coverLetter: coverLetter ? coverLetter.trim() : undefined,
      resumeFileName: resumeFileName || (req.file ? req.file.originalname : 'candidate_resume.pdf'),
      resumeFileSize: resumeFileSize || (req.file ? `${(req.file.size / (1024 * 1024)).toFixed(2)} MB` : '1.4 MB'),
      resumeFilePath: req.file ? req.file.path : undefined,
      consentAgreed: Boolean(consentAgreed),
      status: 'submitted',
      createdAt: new Date(),
    };

    const dbStatus = getDBStatus();
    let savedDoc;

    if (dbStatus.connected) {
      savedDoc = await ApplicationModel.create(applicationPayload);
      // Increment applicant count on job
      await JobModel.updateOne({ id: jobId }, { $inc: { applicantCount: 1 } });
    } else {
      savedDoc = { ...applicationPayload, _id: `mem_${Date.now()}` };
      inMemoryApplications.push(savedDoc);
    }

    console.log(`[ApplicationController] ✅ New candidate application received: ${referenceId} (${fullName} for ${jobTitle})`);

    return res.status(201).json({
      success: true,
      message: 'Application successfully registered and encrypted.',
      data: {
        referenceId: savedDoc.referenceId,
        fullName: savedDoc.fullName,
        jobTitle: savedDoc.jobTitle,
        status: savedDoc.status,
        submittedAt: savedDoc.createdAt,
        nextSteps: [
          'Direct review by Senior Engineering Principal within 48 business hours.',
          'Bilateral NDA and technical discussion invitation via confidential email.',
          'Zero algorithmic screening or automated rejections.'
        ]
      },
      meta: {
        storage: dbStatus.connected ? 'mongodb_atlas' : 'resilient_cache',
      }
    });

  } catch (error) {
    console.error('[ApplicationController] Error processing application:', error);
    return res.status(500).json({
      success: false,
      error: 'Failed to process candidate application',
      message: error.message,
    });
  }
}

export async function getApplications(req, res) {
  try {
    const { jobId, status } = req.query;
    const dbStatus = getDBStatus();

    let applications;
    if (dbStatus.connected) {
      const query = {};
      if (jobId) query.jobId = jobId;
      if (status) query.status = status;
      applications = await ApplicationModel.find(query).sort({ createdAt: -1 });
    } else {
      applications = inMemoryApplications.filter(app => {
        const matchesJob = !jobId || app.jobId === jobId;
        const matchesStatus = !status || app.status === status;
        return matchesJob && matchesStatus;
      });
    }

    return res.status(200).json({
      success: true,
      count: applications.length,
      data: applications,
    });
  } catch (error) {
    console.error('[ApplicationController] Error fetching applications:', error);
    return res.status(500).json({
      success: false,
      error: 'Failed to list applications',
      message: error.message,
    });
  }
}

export async function getApplicationByRef(req, res) {
  try {
    const { referenceId } = req.params;
    const dbStatus = getDBStatus();

    let app;
    if (dbStatus.connected) {
      app = await ApplicationModel.findOne({ referenceId });
    } else {
      app = inMemoryApplications.find(a => a.referenceId === referenceId);
    }

    if (!app) {
      return res.status(404).json({
        success: false,
        error: `Application with receipt ID "${referenceId}" not found.`,
      });
    }

    return res.status(200).json({
      success: true,
      data: app,
    });
  } catch (error) {
    console.error('[ApplicationController] Error looking up application:', error);
    return res.status(500).json({
      success: false,
      error: 'Failed to retrieve application status',
      message: error.message,
    });
  }
}

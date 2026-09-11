/**
 * HRMS AI Agent Controller
 * Provides full programmatic access to all data layers for the AI agent.
 * Covers: Jobs (CRUD), Applications (manage), Analytics, and system ops.
 */

import { JobModel } from '../models/Job.mjs';
import { ApplicationModel } from '../models/Application.mjs';
import { InquiryModel } from '../models/Inquiry.mjs';
import { getDBStatus } from '../config/db.mjs';
import { initialJobs } from '../seed/seedData.mjs';

// ─── In-memory fallback stores (shared references) ──────────────────────────
const inMemoryJobs = [];
const inMemoryApplications = [];
let inMemoryJobIdCounter = 1000;

// ─────────────────────────────────────────────────────────────────────────────
// ANALYTICS & DASHBOARD
// ─────────────────────────────────────────────────────────────────────────────

export async function getAgentDashboard(req, res) {
  try {
    const dbStatus = getDBStatus();

    if (dbStatus.connected) {
      const [
        totalJobs,
        activeJobs,
        totalApplications,
        submittedApps,
        screeningApps,
        interviewApps,
        offeredApps,
        rejectedApps,
        totalInquiries,
        recentApps,
        topJobs,
      ] = await Promise.all([
        JobModel.countDocuments(),
        JobModel.countDocuments({ isActive: true }),
        ApplicationModel.countDocuments(),
        ApplicationModel.countDocuments({ status: 'submitted' }),
        ApplicationModel.countDocuments({ status: 'screening' }),
        ApplicationModel.countDocuments({ status: 'interview_scheduled' }),
        ApplicationModel.countDocuments({ status: 'offered' }),
        ApplicationModel.countDocuments({ status: 'rejected' }),
        InquiryModel.countDocuments(),
        ApplicationModel.find().sort({ createdAt: -1 }).limit(5).select('referenceId fullName jobTitle status createdAt email'),
        JobModel.find({ isActive: true }).sort({ applicantCount: -1 }).limit(5).select('id title department applicantCount'),
      ]);

      return res.status(200).json({
        success: true,
        dashboard: {
          jobs: {
            total: totalJobs,
            active: activeJobs,
            closed: totalJobs - activeJobs,
          },
          applications: {
            total: totalApplications,
            byStatus: {
              submitted: submittedApps,
              screening: screeningApps,
              interview_scheduled: interviewApps,
              offered: offeredApps,
              rejected: rejectedApps,
            },
            conversionRate: totalApplications > 0
              ? `${((offeredApps / totalApplications) * 100).toFixed(1)}%`
              : '0%',
          },
          inquiries: { total: totalInquiries },
          recentApplications: recentApps,
          topJobs,
        },
        meta: { source: 'mongodb_atlas', generatedAt: new Date().toISOString() },
      });
    } else {
      // In-memory fallback stats
      return res.status(200).json({
        success: true,
        dashboard: {
          jobs: { total: inMemoryJobs.length, active: inMemoryJobs.filter(j => j.isActive).length, closed: 0 },
          applications: { total: inMemoryApplications.length, byStatus: {}, conversionRate: '0%' },
          inquiries: { total: 0 },
          recentApplications: [],
          topJobs: [],
        },
        meta: { source: 'resilient_cache', generatedAt: new Date().toISOString() },
      });
    }
  } catch (err) {
    return res.status(500).json({ success: false, error: 'Dashboard generation failed', message: err.message });
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// JOB MANAGEMENT (Full CRUD)
// ─────────────────────────────────────────────────────────────────────────────

export async function agentListJobs(req, res) {
  try {
    const { status, department, limit = 50, page = 1 } = req.query;
    const dbStatus = getDBStatus();

    if (dbStatus.connected) {
      const filter = {};
      if (status === 'active') filter.isActive = true;
      if (status === 'closed') filter.isActive = false;
      if (department) filter.department = department;

      const skip = (parseInt(page) - 1) * parseInt(limit);
      const total = await JobModel.countDocuments(filter);
      const jobs = await JobModel.find(filter).sort({ createdAt: -1 }).skip(skip).limit(parseInt(limit));

      return res.status(200).json({
        success: true,
        count: jobs.length,
        total,
        page: parseInt(page),
        totalPages: Math.ceil(total / parseInt(limit)),
        data: jobs,
        meta: { source: 'mongodb_atlas' },
      });
    } else {
      let jobs = inMemoryJobs;
      if (status === 'active') jobs = jobs.filter(j => j.isActive);
      if (status === 'closed') jobs = jobs.filter(j => !j.isActive);
      if (department) jobs = jobs.filter(j => j.department === department);
      return res.status(200).json({ success: true, count: jobs.length, total: jobs.length, data: jobs, meta: { source: 'resilient_cache' } });
    }
  } catch (err) {
    return res.status(500).json({ success: false, error: 'Failed to list jobs', message: err.message });
  }
}

export async function agentCreateJob(req, res) {
  try {
    const {
      title, department, location, type, experience, salaryRange,
      description, responsibilities, requirements, techStack, isActive
    } = req.body;

    // Validation
    if (!title || !department || !description) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: title, department, description are mandatory.',
      });
    }

    // Generate unique job ID
    const slugId = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
    const timestamp = Date.now().toString().slice(-6);
    const jobId = `${slugId}-${timestamp}`;

    const jobPayload = {
      id: jobId,
      title: title.trim(),
      department,
      location: location || 'Remote (Worldwide)',
      type: type || 'Full-Time',
      experience: experience || 'Mid Level',
      salaryRange: salaryRange || 'Competitive',
      description: description.trim(),
      responsibilities: Array.isArray(responsibilities) ? responsibilities : [],
      requirements: Array.isArray(requirements) ? requirements : [],
      techStack: Array.isArray(techStack) ? techStack : [],
      isActive: isActive !== undefined ? Boolean(isActive) : true,
      applicantCount: 0,
    };

    const dbStatus = getDBStatus();
    let savedJob;

    if (dbStatus.connected) {
      savedJob = await JobModel.create(jobPayload);
    } else {
      savedJob = { ...jobPayload, _id: `mem_${Date.now()}`, createdAt: new Date(), updatedAt: new Date() };
      inMemoryJobs.push(savedJob);
    }

    console.log(`[AgentController] ✅ Job created by AI Agent: ${savedJob.id} — "${savedJob.title}"`);

    return res.status(201).json({
      success: true,
      message: `Job "${savedJob.title}" has been posted successfully.`,
      data: savedJob,
      meta: { source: dbStatus.connected ? 'mongodb_atlas' : 'resilient_cache' },
    });
  } catch (err) {
    if (err.code === 11000) {
      return res.status(409).json({ success: false, error: 'A job with this ID already exists. Try a different title or include more specifics.' });
    }
    return res.status(500).json({ success: false, error: 'Failed to create job', message: err.message });
  }
}

export async function agentUpdateJob(req, res) {
  try {
    const { jobId } = req.params;
    const updates = req.body;
    const dbStatus = getDBStatus();

    // Remove immutable fields
    delete updates._id;
    delete updates.id;
    delete updates.createdAt;
    delete updates.applicantCount;

    let updatedJob;

    if (dbStatus.connected) {
      updatedJob = await JobModel.findOneAndUpdate(
        { id: jobId },
        { $set: updates },
        { new: true, runValidators: true }
      );
    } else {
      const idx = inMemoryJobs.findIndex(j => j.id === jobId);
      if (idx !== -1) {
        inMemoryJobs[idx] = { ...inMemoryJobs[idx], ...updates, updatedAt: new Date() };
        updatedJob = inMemoryJobs[idx];
      }
    }

    if (!updatedJob) {
      return res.status(404).json({ success: false, error: `Job with ID "${jobId}" not found.` });
    }

    console.log(`[AgentController] ✏️ Job updated by AI Agent: ${jobId}`);

    return res.status(200).json({
      success: true,
      message: `Job "${updatedJob.title}" has been updated.`,
      data: updatedJob,
    });
  } catch (err) {
    return res.status(500).json({ success: false, error: 'Failed to update job', message: err.message });
  }
}

export async function agentDeleteJob(req, res) {
  try {
    const { jobId } = req.params;
    const { hardDelete = false } = req.query;
    const dbStatus = getDBStatus();

    let result;

    if (dbStatus.connected) {
      if (hardDelete === 'true') {
        result = await JobModel.findOneAndDelete({ id: jobId });
      } else {
        // Soft delete: mark inactive
        result = await JobModel.findOneAndUpdate(
          { id: jobId },
          { $set: { isActive: false } },
          { new: true }
        );
      }
    } else {
      const idx = inMemoryJobs.findIndex(j => j.id === jobId);
      if (idx !== -1) {
        if (hardDelete === 'true') {
          result = inMemoryJobs.splice(idx, 1)[0];
        } else {
          inMemoryJobs[idx].isActive = false;
          result = inMemoryJobs[idx];
        }
      }
    }

    if (!result) {
      return res.status(404).json({ success: false, error: `Job with ID "${jobId}" not found.` });
    }

    const action = hardDelete === 'true' ? 'permanently deleted' : 'closed (soft-deleted)';
    console.log(`[AgentController] 🗑️ Job ${action} by AI Agent: ${jobId}`);

    return res.status(200).json({
      success: true,
      message: `Job "${result.title}" has been ${action}.`,
      data: { jobId, action, hardDelete: hardDelete === 'true' },
    });
  } catch (err) {
    return res.status(500).json({ success: false, error: 'Failed to delete/close job', message: err.message });
  }
}

export async function agentToggleJobStatus(req, res) {
  try {
    const { jobId } = req.params;
    const dbStatus = getDBStatus();

    let job;

    if (dbStatus.connected) {
      job = await JobModel.findOne({ id: jobId });
      if (!job) return res.status(404).json({ success: false, error: `Job "${jobId}" not found.` });
      job.isActive = !job.isActive;
      await job.save();
    } else {
      job = inMemoryJobs.find(j => j.id === jobId);
      if (!job) return res.status(404).json({ success: false, error: `Job "${jobId}" not found.` });
      job.isActive = !job.isActive;
    }

    const statusLabel = job.isActive ? 'ACTIVE (publicly visible)' : 'CLOSED (hidden from public)';
    console.log(`[AgentController] 🔄 Job status toggled: ${jobId} → ${statusLabel}`);

    return res.status(200).json({
      success: true,
      message: `Job "${job.title}" is now ${statusLabel}.`,
      data: { jobId, title: job.title, isActive: job.isActive, status: statusLabel },
    });
  } catch (err) {
    return res.status(500).json({ success: false, error: 'Failed to toggle job status', message: err.message });
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// APPLICATION MANAGEMENT
// ─────────────────────────────────────────────────────────────────────────────

export async function agentListApplications(req, res) {
  try {
    const { jobId, status, email, limit = 50, page = 1 } = req.query;
    const dbStatus = getDBStatus();

    if (dbStatus.connected) {
      const filter = {};
      if (jobId) filter.jobId = jobId;
      if (status) filter.status = status;
      if (email) filter.email = { $regex: email, $options: 'i' };

      const skip = (parseInt(page) - 1) * parseInt(limit);
      const total = await ApplicationModel.countDocuments(filter);
      const applications = await ApplicationModel.find(filter)
        .sort({ createdAt: -1 })
        .skip(skip)
        .limit(parseInt(limit));

      return res.status(200).json({
        success: true,
        count: applications.length,
        total,
        page: parseInt(page),
        totalPages: Math.ceil(total / parseInt(limit)),
        data: applications,
        meta: { source: 'mongodb_atlas' },
      });
    } else {
      let apps = inMemoryApplications;
      if (jobId) apps = apps.filter(a => a.jobId === jobId);
      if (status) apps = apps.filter(a => a.status === status);
      return res.status(200).json({ success: true, count: apps.length, total: apps.length, data: apps, meta: { source: 'resilient_cache' } });
    }
  } catch (err) {
    return res.status(500).json({ success: false, error: 'Failed to list applications', message: err.message });
  }
}

export async function agentUpdateApplicationStatus(req, res) {
  try {
    const { referenceId } = req.params;
    const { status, reviewerNote, reviewerName } = req.body;

    const validStatuses = ['submitted', 'screening', 'interview_scheduled', 'offered', 'rejected'];
    if (!status || !validStatuses.includes(status)) {
      return res.status(400).json({
        success: false,
        error: `Invalid status. Must be one of: ${validStatuses.join(', ')}`,
      });
    }

    const dbStatus = getDBStatus();
    let application;

    if (dbStatus.connected) {
      const updateData = { status };
      const pushData = {};

      if (reviewerNote) {
        pushData.reviewerNotes = {
          author: reviewerName || 'HRMS Agent',
          note: reviewerNote,
          createdAt: new Date(),
        };
      }

      application = await ApplicationModel.findOneAndUpdate(
        { referenceId },
        {
          $set: updateData,
          ...(reviewerNote ? { $push: pushData } : {}),
        },
        { new: true }
      );
    } else {
      application = inMemoryApplications.find(a => a.referenceId === referenceId);
      if (application) {
        application.status = status;
        if (reviewerNote) {
          if (!application.reviewerNotes) application.reviewerNotes = [];
          application.reviewerNotes.push({
            author: reviewerName || 'HRMS Agent',
            note: reviewerNote,
            createdAt: new Date(),
          });
        }
      }
    }

    if (!application) {
      return res.status(404).json({ success: false, error: `Application "${referenceId}" not found.` });
    }

    console.log(`[AgentController] 📋 Application ${referenceId} status updated → ${status} by ${reviewerName || 'HRMS Agent'}`);

    return res.status(200).json({
      success: true,
      message: `Application ${referenceId} for "${application.fullName}" has been moved to "${status}".`,
      data: application,
    });
  } catch (err) {
    return res.status(500).json({ success: false, error: 'Failed to update application status', message: err.message });
  }
}

export async function agentBulkUpdateStatus(req, res) {
  try {
    const { referenceIds, status, reviewerNote, reviewerName } = req.body;

    if (!Array.isArray(referenceIds) || referenceIds.length === 0) {
      return res.status(400).json({ success: false, error: 'referenceIds must be a non-empty array.' });
    }

    const validStatuses = ['submitted', 'screening', 'interview_scheduled', 'offered', 'rejected'];
    if (!validStatuses.includes(status)) {
      return res.status(400).json({ success: false, error: `Invalid status. Must be one of: ${validStatuses.join(', ')}` });
    }

    const dbStatus = getDBStatus();
    let modifiedCount = 0;

    if (dbStatus.connected) {
      const updatePayload = { $set: { status } };
      if (reviewerNote) {
        updatePayload.$push = {
          reviewerNotes: {
            author: reviewerName || 'HRMS Agent',
            note: reviewerNote,
            createdAt: new Date(),
          },
        };
      }

      const result = await ApplicationModel.updateMany(
        { referenceId: { $in: referenceIds } },
        updatePayload
      );
      modifiedCount = result.modifiedCount;
    } else {
      referenceIds.forEach(ref => {
        const app = inMemoryApplications.find(a => a.referenceId === ref);
        if (app) { app.status = status; modifiedCount++; }
      });
    }

    console.log(`[AgentController] 📦 Bulk status update: ${modifiedCount} applications → ${status}`);

    return res.status(200).json({
      success: true,
      message: `${modifiedCount} applications have been moved to "${status}".`,
      data: { modifiedCount, status, referenceIds },
    });
  } catch (err) {
    return res.status(500).json({ success: false, error: 'Bulk update failed', message: err.message });
  }
}

export async function agentAddReviewerNote(req, res) {
  try {
    const { referenceId } = req.params;
    const { note, author } = req.body;

    if (!note || !note.trim()) {
      return res.status(400).json({ success: false, error: 'A note is required.' });
    }

    const noteEntry = {
      author: author || 'HRMS Agent',
      note: note.trim(),
      createdAt: new Date(),
    };

    const dbStatus = getDBStatus();
    let application;

    if (dbStatus.connected) {
      application = await ApplicationModel.findOneAndUpdate(
        { referenceId },
        { $push: { reviewerNotes: noteEntry } },
        { new: true }
      );
    } else {
      application = inMemoryApplications.find(a => a.referenceId === referenceId);
      if (application) {
        if (!application.reviewerNotes) application.reviewerNotes = [];
        application.reviewerNotes.push(noteEntry);
      }
    }

    if (!application) {
      return res.status(404).json({ success: false, error: `Application "${referenceId}" not found.` });
    }

    return res.status(200).json({
      success: true,
      message: `Reviewer note added to application ${referenceId}.`,
      data: { referenceId, noteAdded: noteEntry, totalNotes: application.reviewerNotes?.length || 1 },
    });
  } catch (err) {
    return res.status(500).json({ success: false, error: 'Failed to add reviewer note', message: err.message });
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// INQUIRIES MANAGEMENT
// ─────────────────────────────────────────────────────────────────────────────

export async function agentListInquiries(req, res) {
  try {
    const { status, limit = 50, page = 1 } = req.query;
    const dbStatus = getDBStatus();

    if (dbStatus.connected) {
      const filter = {};
      if (status) filter.status = status;

      const skip = (parseInt(page) - 1) * parseInt(limit);
      const total = await InquiryModel.countDocuments(filter);
      const inquiries = await InquiryModel.find(filter)
        .sort({ createdAt: -1 })
        .skip(skip)
        .limit(parseInt(limit));

      return res.status(200).json({
        success: true,
        count: inquiries.length,
        total,
        data: inquiries,
        meta: { source: 'mongodb_atlas' },
      });
    }

    return res.status(200).json({ success: true, count: 0, total: 0, data: [], meta: { source: 'resilient_cache' } });
  } catch (err) {
    return res.status(500).json({ success: false, error: 'Failed to list inquiries', message: err.message });
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// SYSTEM: Seed Reset & Agent Info
// ─────────────────────────────────────────────────────────────────────────────

export async function agentReseedJobs(req, res) {
  try {
    const { force = false } = req.body;
    const dbStatus = getDBStatus();
    const { seedDatabase } = await import('../seed/seedData.mjs');

    if (dbStatus.connected) {
      if (force) {
        await JobModel.deleteMany({});
        console.log('[AgentController] 🔄 Cleared all jobs for forced reseed.');
      }
      await seedDatabase();
      const count = await JobModel.countDocuments();
      return res.status(200).json({
        success: true,
        message: `Database reseeded. Total jobs: ${count}.`,
        data: { totalJobs: count, forcedClear: Boolean(force) },
      });
    } else {
      // Reset in-memory to initial
      inMemoryJobs.length = 0;
      initialJobs.forEach(j => inMemoryJobs.push({ ...j }));
      return res.status(200).json({
        success: true,
        message: 'In-memory store reseeded from initial data.',
        data: { totalJobs: inMemoryJobs.length },
      });
    }
  } catch (err) {
    return res.status(500).json({ success: false, error: 'Reseed failed', message: err.message });
  }
}

export async function getAgentCapabilities(req, res) {
  return res.status(200).json({
    success: true,
    agent: {
      name: 'Azyntrix HRMS AI Agent',
      version: '1.0.0',
      description: 'Full-access programmatic control layer for the Azyntrix HRMS. Capable of managing all job listings, applications, and analytics.',
      capabilities: [
        'GET  /api/v1/agent/dashboard          — Full analytics dashboard',
        'GET  /api/v1/agent/jobs               — List all jobs (active + closed)',
        'POST /api/v1/agent/jobs               — Create/post a new job listing',
        'PUT  /api/v1/agent/jobs/:jobId        — Update any field of a job',
        'DELETE /api/v1/agent/jobs/:jobId      — Close (soft) or permanently delete a job',
        'PATCH /api/v1/agent/jobs/:jobId/toggle — Toggle job active/closed status',
        'GET  /api/v1/agent/applications       — List all applications with filters',
        'PATCH /api/v1/agent/applications/:ref/status  — Update application pipeline status',
        'POST /api/v1/agent/applications/bulk-status   — Bulk update multiple applications',
        'POST /api/v1/agent/applications/:ref/note     — Add reviewer note',
        'GET  /api/v1/agent/inquiries          — List all contact inquiries',
        'POST /api/v1/agent/reseed             — Reseed job data from seed file',
      ],
      supportedJobStatuses: ['active', 'closed'],
      supportedApplicationStatuses: ['submitted', 'screening', 'interview_scheduled', 'offered', 'rejected'],
    },
    meta: { timestamp: new Date().toISOString() },
  });
}
